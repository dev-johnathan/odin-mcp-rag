"""Optional LangChain and LangSmith integration for tracing and LLM orchestration."""

from __future__ import annotations

import os
from typing import Any

from odin_rag_mcp.config import settings


def configure_langchain_environment() -> None:
    """Set LangSmith/LangChain environment variables when tracing is enabled."""
    if not settings.langsmith_enabled:
        return

    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", settings.langchain_project)

    api_key = settings.langchain_api_key or settings.langsmith_api_key
    if api_key:
        os.environ.setdefault("LANGCHAIN_API_KEY", api_key)
        os.environ.setdefault("LANGSMITH_API_KEY", api_key)


def is_langchain_available() -> bool:
    """Return whether LangChain and the OpenAI adapter are installed."""
    try:
        import langchain_core  # noqa: F401
        from langchain_openai import ChatOpenAI  # noqa: F401

        return True
    except ImportError:  # pragma: no cover - optional dependency path
        return False


def get_langchain_llm(model_name: str | None = None, *, api_key: str | None = None, temperature: float = 0.2):
    """Create a LangChain chat model when the optional dependency is available."""
    if not settings.langsmith_enabled:
        return None

    try:
        from langchain_openai import ChatOpenAI
    except ImportError:  # pragma: no cover - optional dependency path
        return None

    configured_api_key = api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY")
    if not configured_api_key:
        return None

    configure_langchain_environment()
    return ChatOpenAI(
        model=model_name or settings.openai_model,
        openai_api_key=configured_api_key,
        temperature=temperature,
    )


def build_langchain_response(question: str, *, context: str | None = None, model_name: str | None = None) -> str | None:
    """Generate a response through LangChain if tracing is enabled and dependencies exist."""
    llm = get_langchain_llm(model_name=model_name)
    if llm is None:
        return None

    try:
        from langchain_core.prompts import ChatPromptTemplate
    except ImportError:  # pragma: no cover - optional dependency path
        return None

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "Você é Odin, um guia de sabedoria analítica."),
            ("user", "Contexto:\n{context}\n\nPergunta:\n{question}"),
        ]
    )

    chain = prompt_template | llm
    response = chain.invoke({"context": context or "Sem contexto adicional.", "question": question})
    content = getattr(response, "content", None)
    if content is None and isinstance(response, dict):
        content = response.get("text") or response.get("content")
    return str(content) if content is not None else None
