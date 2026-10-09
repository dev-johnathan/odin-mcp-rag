"""Orquestrador principal do agente Odin."""

from __future__ import annotations

from odin_rag_mcp.providers.factory import build_provider
from odin_rag_mcp.rag.knowledge_base import KnowledgeBase


class RAGAgent:
    """Coordena recuperação de contexto e geração de resposta.

    A classe fica responsável por orquestrar o fluxo de busca e resposta sem
    misturar regra de negócio com HTTP ou MCP.
    """

    def __init__(self, knowledge_base: KnowledgeBase | None = None) -> None:
        self.knowledge_base = knowledge_base or KnowledgeBase()

    def ingest(self, documents: list[str]) -> int:
        """Insere documentos na base de conhecimento e devolve o total atual."""
        return self.knowledge_base.index(documents)

    def ask(
        self,
        question: str,
        *,
        provider_name: str | None = None,
        model_name: str | None = None,
        context_documents: list[str] | None = None,
    ) -> str:
        """Busca contexto relevante, escolhe o provedor e responde a pergunta."""
        if not question or not question.strip():
            return "Pergunta inválida. Forneça um texto para que o Odin possa responder."

        if context_documents:
            self.knowledge_base.index(context_documents)

        results = self.knowledge_base.search(question, limit=4)
        context = "\n\n".join(item["content"] for item in results)

        provider = build_provider(provider_name)
        return provider.generate(
            question,
            context=context or "Sem contexto relevante encontrado.",
            model=model_name,
        )
