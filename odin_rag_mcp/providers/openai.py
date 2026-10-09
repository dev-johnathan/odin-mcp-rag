from __future__ import annotations

from odin_rag_mcp.config import settings
from odin_rag_mcp.langchain_support import build_langchain_response
from odin_rag_mcp.providers.base import BaseProvider

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self.api_key = self.config.get("api_key") or settings.openai_api_key
        self.model = self.config.get("model") or settings.openai_model
        self.client = OpenAI(api_key=self.api_key) if OpenAI and self.api_key else None

    def generate(
        self,
        prompt: str,
        *,
        context: str | None = None,
        model: str | None = None,
    ) -> str:
        langchain_response = build_langchain_response(prompt, context=context, model_name=model or self.model)
        if langchain_response is not None:
            return langchain_response

        if self.client is not None:
            try:
                response = self.client.chat.completions.create(
                    model=model or self.model,
                    messages=[
                        {"role": "system", "content": "Você é Odin, um guia de sabedoria analítica."},
                        {"role": "user", "content": f"Contexto:\n{context or ''}\n\nPergunta:\n{prompt}"},
                    ],
                )
                return response.choices[0].message.content or ""
            except Exception:
                pass

        safe_context = context or "Sem contexto adicional."
        return (
            f"[OpenAI:{model or self.model}] Resposta baseada em contexto:\n"
            f"{safe_context}\n\nPergunta: {prompt}"
        )
