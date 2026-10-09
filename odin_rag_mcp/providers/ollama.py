from __future__ import annotations

from odin_rag_mcp.config import settings
from odin_rag_mcp.providers.base import BaseProvider

try:
    import ollama
except ImportError:  # pragma: no cover
    ollama = None


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self.base_url = self.config.get("base_url") or settings.ollama_base_url
        self.model = self.config.get("model") or settings.ollama_model
        self.client = ollama.Client(host=self.base_url) if ollama else None

    def generate(
        self,
        prompt: str,
        *,
        context: str | None = None,
        model: str | None = None,
    ) -> str:
        if self.client is not None:
            try:
                response = self.client.generate(
                    model=model or self.model,
                    prompt=f"Contexto:\n{context or ''}\n\nPergunta:\n{prompt}",
                )
                return response.get("response", "")
            except Exception:
                pass

        safe_context = context or "Sem contexto adicional."
        return (
            f"[Ollama:{model or self.model}] Resposta baseada em contexto:\n"
            f"{safe_context}\n\nPergunta: {prompt}"
        )
