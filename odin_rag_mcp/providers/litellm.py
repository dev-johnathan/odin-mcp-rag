from __future__ import annotations

from odin_rag_mcp.config import settings
from odin_rag_mcp.providers.base import BaseProvider


class LiteLLMProvider(BaseProvider):
    name = "litellm"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self.base_url = self.config.get("base_url") or settings.litellm_base_url
        self.api_key = self.config.get("api_key") or settings.litellm_api_key
        self.model = self.config.get("model") or settings.openai_model

    def generate(
        self,
        prompt: str,
        *,
        context: str | None = None,
        model: str | None = None,
    ) -> str:
        safe_context = context or "Sem contexto adicional."
        return (
            f"[LiteLLM:{model or self.model}] Resposta via gateway aberto:\n"
            f"{safe_context}\n\nPergunta: {prompt}"
        )
