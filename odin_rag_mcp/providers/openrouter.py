from __future__ import annotations

from odin_rag_mcp.config import settings
from odin_rag_mcp.providers.base import BaseProvider


class OpenRouterProvider(BaseProvider):
    name = "openrouter"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self.api_key = self.config.get("api_key") or settings.openrouter_api_key
        self.model = self.config.get("model") or settings.openrouter_model

    def generate(
        self,
        prompt: str,
        *,
        context: str | None = None,
        model: str | None = None,
    ) -> str:
        safe_context = context or "Sem contexto adicional."
        return (
            f"[OpenRouter:{model or self.model}] Resposta via router público:\n"
            f"{safe_context}\n\nPergunta: {prompt}"
        )
