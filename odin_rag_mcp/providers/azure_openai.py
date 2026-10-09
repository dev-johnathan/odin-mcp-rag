from __future__ import annotations

from odin_rag_mcp.config import settings
from odin_rag_mcp.providers.base import BaseProvider


class AzureOpenAIProvider(BaseProvider):
    name = "azure_openai"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self.api_key = self.config.get("api_key") or settings.azure_openai_api_key
        self.endpoint = self.config.get("endpoint") or settings.azure_openai_endpoint
        self.model = self.config.get("model") or settings.azure_openai_model

    def generate(
        self,
        prompt: str,
        *,
        context: str | None = None,
        model: str | None = None,
    ) -> str:
        safe_context = context or "Sem contexto adicional."
        return (
            f"[AzureOpenAI:{model or self.model}] Resposta com endpoint configurado:\n"
            f"{safe_context}\n\nPergunta: {prompt}"
        )
