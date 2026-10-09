from __future__ import annotations

from odin_rag_mcp.config import settings
from odin_rag_mcp.providers.base import BaseProvider

try:
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self.api_key = self.config.get("api_key") or settings.anthropic_api_key
        self.model = self.config.get("model") or settings.anthropic_model
        self.client = anthropic.Anthropic(api_key=self.api_key) if anthropic and self.api_key else None

    def generate(
        self,
        prompt: str,
        *,
        context: str | None = None,
        model: str | None = None,
    ) -> str:
        if self.client is not None:
            try:
                response = self.client.messages.create(
                    model=model or self.model,
                    max_tokens=512,
                    system="Você é Odin, um guia de sabedoria analítica.",
                    messages=[{"role": "user", "content": f"Contexto:\n{context or ''}\n\nPergunta:\n{prompt}"}],
                )
                return response.content[0].text if response.content else ""
            except Exception:
                pass

        safe_context = context or "Sem contexto adicional."
        return (
            f"[Anthropic:{model or self.model}] Resposta baseada em contexto:\n"
            f"{safe_context}\n\nPergunta: {prompt}"
        )
