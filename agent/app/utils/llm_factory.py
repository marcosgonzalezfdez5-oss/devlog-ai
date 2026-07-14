"""Provider-agnostic chat model factory.

The Deep Agent must be able to run on different LLM backends (Claude,
GPT-4, Gemini Flash, ...) without changing agent or tool code. Callers
ask for "a chat model" and get one back; which provider and model name
that resolves to is a config concern, not an agent concern.
"""

from langchain_core.language_models.chat_models import BaseChatModel

from app.config import LLMProvider, get_settings


def get_chat_model(provider: LLMProvider | None = None) -> BaseChatModel:
    """Build a LangChain chat model for the given provider.

    Falls back to ``Settings.llm_provider`` when no provider is given,
    so most call sites just say ``get_chat_model()``. An explicit
    override lets a future step pick a cheaper/faster model (e.g.
    Gemini Flash) for a specific reasoning step.
    """
    settings = get_settings()
    resolved_provider = provider or settings.llm_provider

    if resolved_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model_name=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
        )

    if resolved_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
        )

    if resolved_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
        )

    raise ValueError(f"Unsupported LLM provider: {resolved_provider}")
