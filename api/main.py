"""Ponto de entrada da API do Odin.

A ideia aqui é manter a camada HTTP bem fina. Ela apenas recebe a requisição,
valida o payload e delega a lógica de negócio para o agente, a base de
conhecimento e o servidor MCP.
"""

from __future__ import annotations

import hmac
import time
from collections import defaultdict
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from odin_rag_mcp.auth import verify_access_token
from odin_rag_mcp.config import settings
from odin_rag_mcp.mcp.server import MCPServer
from odin_rag_mcp.observability import observability
from odin_rag_mcp.rag.agent import RAGAgent

ProviderName = Literal["openai", "anthropic", "ollama", "litellm", "openrouter", "azure_openai"]
MCPMethod = Literal["list_tools", "call_tool", "query", "ingest", "health"]


class ChatRequest(BaseModel):
    """Contrato da requisição de conversa com o agente."""

    question: str = Field(..., min_length=1, max_length=2000, description="Question to answer")
    provider: ProviderName | None = Field(default=None, description="Optional provider override")
    model: str | None = Field(default=None, min_length=1, max_length=100, description="Optional model override")
    context: list[str] | None = Field(
        default=None,
        max_length=5,
        description="Additional context snippets manually injected before the answer.",
    )

    @field_validator("context")
    @classmethod
    def validate_context(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        for item in value:
            if len(item) > 5000:
                raise ValueError("Each context snippet must be shorter than 5000 characters.")
        return value


class MCPRequest(BaseModel):
    """Generic MCP command request routed to the MCP server."""

    method: MCPMethod = Field(..., description="MCP method name to execute")
    params: dict[str, Any] | None = Field(
        default=None,
        description="Method arguments, if required by the selected operation.",
    )


app = FastAPI(
    title="Odin RAG MCP API",
    version="0.1.0",
    description="Agente modular de RAG + MCP para orquestração de IA multi-provider.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_allowed_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

REQUEST_BUCKETS: dict[str, list[float]] = defaultdict(list)
AUDIT_LOG: list[dict[str, Any]] = []


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Avoid exposing internal validation details in production responses."""
    return JSONResponse(status_code=422, content={"detail": "Invalid request payload."})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return normalized HTTP error payloads to API consumers."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Enforce API key validation, JWT auth, request limits, tracing and security headers."""
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown").split(",")[0].strip()
    trace_id = request.headers.get("X-Trace-Id") or observability.new_trace_id()
    request.state.trace_id = trace_id
    started_at = time.perf_counter()

    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_request_size_bytes:
        duration_ms = (time.perf_counter() - started_at) * 1000
        observability.record_request(
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
            status_code=413,
            duration_ms=duration_ms,
            trace_id=trace_id,
        )
        response = JSONResponse(status_code=413, content={"detail": "Request body too large."})
        response.headers["X-Trace-Id"] = trace_id
        return response

    rate_limit = settings.rate_limit_per_minute
    window = settings.rate_limit_window_seconds
    if rate_limit > 0:
        now = time.monotonic()
        requests = REQUEST_BUCKETS[client_ip]
        requests[:] = [timestamp for timestamp in requests if now - timestamp < window]
        if len(requests) >= rate_limit:
            duration_ms = (time.perf_counter() - started_at) * 1000
            observability.record_request(
                method=request.method,
                path=request.url.path,
                client_ip=client_ip,
                status_code=429,
                duration_ms=duration_ms,
                trace_id=trace_id,
            )
            response = JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})
            response.headers["X-Trace-Id"] = trace_id
            return response
        requests.append(now)

    configured_key = settings.odin_api_key
    jwt_secret = settings.jwt_secret
    authorization = request.headers.get("Authorization", "")
    token = None
    if authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]

    if jwt_secret:
        if not token:
            duration_ms = (time.perf_counter() - started_at) * 1000
            observability.record_request(
                method=request.method,
                path=request.url.path,
                client_ip=client_ip,
                status_code=401,
                duration_ms=duration_ms,
                trace_id=trace_id,
            )
            response = JSONResponse(status_code=401, content={"detail": "Invalid or missing JWT token."})
            response.headers["X-Trace-Id"] = trace_id
            return response
        try:
            verify_access_token(token)
        except Exception:
            duration_ms = (time.perf_counter() - started_at) * 1000
            observability.record_request(
                method=request.method,
                path=request.url.path,
                client_ip=client_ip,
                status_code=401,
                duration_ms=duration_ms,
                trace_id=trace_id,
            )
            response = JSONResponse(status_code=401, content={"detail": "Invalid or expired JWT token."})
            response.headers["X-Trace-Id"] = trace_id
            return response
    elif configured_key:
        provided = request.headers.get("X-API-Key")
        if not provided and token:
            provided = token

        if not provided or not hmac.compare_digest(provided, configured_key):
            duration_ms = (time.perf_counter() - started_at) * 1000
            observability.record_request(
                method=request.method,
                path=request.url.path,
                client_ip=client_ip,
                status_code=401,
                duration_ms=duration_ms,
                trace_id=trace_id,
            )
            response = JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key."},
            )
            response.headers["X-Trace-Id"] = trace_id
            return response

    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    duration_ms = (time.perf_counter() - started_at) * 1000
    observability.record_request(
        method=request.method,
        path=request.url.path,
        client_ip=client_ip,
        status_code=response.status_code,
        duration_ms=duration_ms,
        trace_id=trace_id,
    )
    AUDIT_LOG.append(
        {
            "timestamp": time.time(),
            "trace_id": trace_id,
            "ip": client_ip,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 3),
        }
    )
    AUDIT_LOG[:] = AUDIT_LOG[-50:]

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    return response


# The HTTP layer keeps domain objects isolated and reusable by other interfaces.
mcp_server = MCPServer()
agent = RAGAgent()

AVAILABLE_PROVIDERS = list(settings.allowed_providers)


@app.get("/health")
async def health() -> dict[str, Any]:
    """Endpoint de saúde para verificar se a API e o registro MCP estão vivos."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "providers": mcp_server.list_tools(),
    }


@app.get("/providers")
async def providers() -> dict[str, Any]:
    """Lista os provedores disponíveis para o frontend e integrações externas."""
    return {
        "default_provider": settings.default_provider,
        "available": AVAILABLE_PROVIDERS,
    }


@app.post("/chat")
async def chat(payload: ChatRequest) -> dict[str, Any]:
    """Responde uma pergunta usando o fluxo atual de RAG e proveniência de modelo."""
    answer = agent.ask(
        question=payload.question,
        provider_name=payload.provider,
        model_name=payload.model,
        context_documents=payload.context,
    )

    return {
        "answer": answer,
        "provider": payload.provider or settings.default_provider,
        "model": payload.model or settings.default_provider,
    }


@app.post("/mcp")
async def mcp(payload: MCPRequest) -> dict[str, Any]:
    """Encaminha requisições para o servidor MCP e executa as ferramentas do agente."""
    return mcp_server.handle_request(payload.method, payload.params or {})


@app.get("/")
async def root() -> dict[str, Any]:
    """Endpoint raiz com os principais pontos de entrada da aplicação."""
    return {
        "name": settings.app_name,
        "status": "online",
        "docs": "/docs",
        "mcp": "/mcp",
        "chat": "/chat",
    }


@app.get("/audit")
async def audit() -> dict[str, Any]:
    """Retorna os últimos eventos de auditoria da API."""
    return {
        "count": len(AUDIT_LOG),
        "entries": AUDIT_LOG[-10:],
    }


@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    """Exposes the latest aggregated metrics for observability dashboards."""
    return observability.snapshot()
