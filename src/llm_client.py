"""LLM client factory for multi-provider support.

Implements D-01, D-02, D-03, D-04:
- D-01: Multi-provider equal support via LangChain unified interface
- D-02: Runtime provider selection based on .env configuration
- D-03: Fail immediately on API errors — no retry, no failover
- D-04: Supported providers: OpenAI, Claude (Anthropic), DeepSeek
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI

from src.config import settings


def _openai_kwargs(temperature: float | None = None) -> dict:
    """Build kwargs for OpenAI-compatible chat models."""
    kwargs = {"model": settings.llm_model, "api_key": settings.openai_api_key}
    base_url = getattr(settings, "openai_base_url", None)
    if isinstance(base_url, str) and base_url.strip():
        kwargs["base_url"] = base_url
    if temperature is not None:
        kwargs["temperature"] = temperature
    return kwargs


def create_llm() -> BaseChatModel:
    """Create LLM client based on current settings.

    Returns:
        BaseChatModel: Configured LLM client for the selected provider.

    Raises:
        ValueError: If the provider is not supported.
    """
    provider = settings.llm_provider
    model = settings.llm_model

    if provider == "openai":
        return ChatOpenAI(**_openai_kwargs())
    elif provider == "claude":
        return ChatAnthropic(model_name=model, api_key=settings.anthropic_api_key)
    elif provider == "deepseek":
        return ChatDeepSeek(model=model, api_key=settings.deepseek_api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def create_llm_with_temp(temperature: float = 0.0) -> BaseChatModel:
    """Create LLM client with specific temperature for agent roles.

    Per AGT-01, AGT-02, AGT-03:
    - Screenwriter: 0.1 (AGT-01: 0.0-0.2)
    - Writer: 0.5 (AGT-02: 0.4-0.7)
    - Reviewer: 0.2 (AGT-03: 0.1-0.3)

    Args:
        temperature: Temperature value for LLM generation (0.0 to 1.0).

    Returns:
        BaseChatModel: Configured LLM client with specified temperature.

    Raises:
        ValueError: If the provider is not supported.
    """
    provider = settings.llm_provider
    model = settings.llm_model

    if provider == "openai":
        return ChatOpenAI(**_openai_kwargs(temperature=temperature))
    elif provider == "claude":
        return ChatAnthropic(model_name=model, api_key=settings.anthropic_api_key, temperature=temperature)
    elif provider == "deepseek":
        return ChatDeepSeek(model=model, api_key=settings.deepseek_api_key, temperature=temperature)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
