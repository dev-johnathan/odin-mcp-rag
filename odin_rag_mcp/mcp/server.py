"""Servidor MCP que expõe as ferramentas do agente."""

from __future__ import annotations

from typing import Any, Callable

from odin_rag_mcp.rag.agent import RAGAgent


class MCPServer:
    """Fachada que expõe as capacidades do agente como ferramentas MCP."""

    def __init__(self) -> None:
        self.agent = RAGAgent()
        self.tools: dict[str, dict[str, Any]] = {
            "search_knowledge": {
                "description": "Busca contexto relevante em memória local",
                "handler": self._search_knowledge,
            },
            "answer_question": {
                "description": "Responde uma pergunta com RAG e provider configurado",
                "handler": self._answer_question,
            },
            "ingest_documents": {
                "description": "Indexa novos documentos no conhecimento local",
                "handler": self._ingest_documents,
            },
        }

    def list_tools(self) -> list[dict[str, str]]:
        """Expõe o catálogo de ferramentas em formato simples e serializável."""
        return [
            {"name": name, "description": tool["description"]}
            for name, tool in self.tools.items()
        ]

    def handle_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Roteia as operações MCP para o handler correto."""
        handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
            "list_tools": lambda _params: {"tools": self.list_tools()},
            "health": lambda _params: {"status": "ok", "service": "Odin MCP"},
            "query": self._handle_query,
            "ingest": self._handle_ingest,
            "call_tool": self._handle_call_tool,
        }

        handler = handlers.get(method)
        if handler is None:
            return {"error": f"Unsupported MCP method: {method}"}

        return handler(params or {})

    def _handle_query(self, params: dict[str, Any]) -> dict[str, Any]:
        question = params.get("question", "")
        return {
            "answer": self.agent.ask(
                question,
                provider_name=params.get("provider"),
                model_name=params.get("model"),
            )
        }

    def _handle_ingest(self, params: dict[str, Any]) -> dict[str, Any]:
        documents = params.get("documents", [])
        return {"count": self.agent.ingest(documents)}

    def _handle_call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        tool_name = params.get("name")
        if tool_name not in self.tools:
            return {"error": f"Tool not found: {tool_name}"}

        result = self.tools[tool_name]["handler"](params.get("arguments", {}))
        return {"tool": tool_name, "result": result}

    def _search_knowledge(self, arguments: dict[str, Any]) -> dict[str, Any]:
        query = arguments.get("query", "")
        return {"results": self.agent.knowledge_base.search(query, limit=3)}

    def _answer_question(self, arguments: dict[str, Any]) -> dict[str, Any]:
        question = arguments.get("question", "")
        provider = arguments.get("provider")
        model = arguments.get("model")
        answer = self.agent.ask(question, provider_name=provider, model_name=model)
        return {"answer": answer}

    def _ingest_documents(self, arguments: dict[str, Any]) -> dict[str, Any]:
        documents = arguments.get("documents", [])
        return {"count": self.agent.ingest(documents)}
