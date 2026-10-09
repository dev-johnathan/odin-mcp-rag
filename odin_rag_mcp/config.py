"""Configuração central do Odin.

Tudo que é sensível ou variável por ambiente fica aqui. Mantemos a configuração
imutável para evitar mudanças acidentais em tempo de execução.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Configuração imutável carregada a partir do ambiente."""

    app_name: str = os.getenv("APP_NAME", "Odin RAG MCP")
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8001"))
    frontend_port: int = int(os.getenv("FRONTEND_PORT", "3000"))
    default_provider: str = os.getenv("DEFAULT_PROVIDER", "openai")
    odin_api_key: str | None = os.getenv("ODIN_API_KEY")
    jwt_secret: str | None = os.getenv("JWT_SECRET")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    langsmith_api_key: str | None = os.getenv("LANGSMITH_API_KEY")
    langchain_api_key: str | None = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
    langchain_tracing_v2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").strip().lower() in {"1", "true", "yes", "on"}
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "odin-rag-mcp")
    langsmith_enabled: bool = (
        bool(os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY"))
        and os.getenv("LANGCHAIN_TRACING_V2", "false").strip().lower() in {"1", "true", "yes", "on"}
    )
    cors_allowed_origins: tuple[str, ...] = tuple(
        item.strip()
        for item in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
        if item.strip()
    )
    allowed_providers: tuple[str, ...] = (
        "openai",
        "anthropic",
        "ollama",
        "litellm",
        "openrouter",
        "azure_openai",
    )
    max_question_length: int = int(os.getenv("MAX_QUESTION_LENGTH", "2000"))
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    max_request_size_bytes: int = int(os.getenv("MAX_REQUEST_SIZE_BYTES", "1048576"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    litellm_base_url: str = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
    litellm_api_key: str | None = os.getenv("LITELLM_API_KEY")
    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    azure_openai_api_key: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str | None = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_model: str = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")


settings = Settings()
