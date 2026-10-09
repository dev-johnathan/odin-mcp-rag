"""Factory and registry responsible for provider resolution."""

from __future__ import annotations

from odin_rag_mcp.config import settings
from odin_rag_mcp.providers.anthropic import AnthropicProvider
from odin_rag_mcp.providers.azure_openai import AzureOpenAIProvider
from odin_rag_mcp.providers.base import BaseProvider
from odin_rag_mcp.providers.litellm import LiteLLMProvider
from odin_rag_mcp.providers.ollama import OllamaProvider
from odin_rag_mcp.providers.openai import OpenAIProvider
from odin_rag_mcp.providers.openrouter import OpenRouterProvider


class ProviderRegistry:
    """Central registry for provider instantiation.

    The registry follows the factory pattern to keep the rest of the system
    decoupled from concrete vendor implementations.
    """

    _providers: dict[str, type[BaseProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
        "litellm": LiteLLMProvider,
        "openrouter": OpenRouterProvider,
        "azure_openai": AzureOpenAIProvider,
    }

    @classmethod
    def register(cls, name: str, provider_cls: type[BaseProvider]) -> None:
        """Register a new provider without modifying the domain logic."""
        cls._providers[name.lower()] = provider_cls

    @classmethod
    def get(cls, provider_name: str | None, **kwargs) -> BaseProvider:
        """Instantiate the requested provider or raise a domain error."""
        normalized = (provider_name or settings.default_provider).lower()
        provider_cls = cls._providers.get(normalized)
        if provider_cls is None:
            raise ValueError(f"Unsupported provider: {provider_name}")
        return provider_cls(**kwargs)


def build_provider(provider_name: str | None = None, **kwargs) -> BaseProvider:
    """High-level helper for creating provider implementations."""
    return ProviderRegistry.get(provider_name, **kwargs)
