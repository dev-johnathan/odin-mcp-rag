"""Abstract contracts used by all LLM provider adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract provider contract shared by every AI backend.

    This class enforces the Liskov substitution principle: every concrete
    provider must expose the same interface and behave according to the same
    contract, regardless of the underlying vendor.
    """

    name: str = "base"

    def __init__(self, config: dict | None = None) -> None:
        self.config = config or {}

    def build_prompt(self, prompt: str, *, context: str | None = None) -> str:
        """Create a normalized prompt structure for all providers."""
        safe_context = context or "Sem contexto adicional."
        return f"Contexto:\n{safe_context}\n\nPergunta:\n{prompt}"

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        context: str | None = None,
        model: str | None = None,
    ) -> str:
        """Return a generated answer for the given prompt and context."""
        raise NotImplementedError
