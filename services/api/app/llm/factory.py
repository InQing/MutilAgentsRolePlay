from app.core.config import Settings
from app.llm.interfaces import LLMClient
from app.llm.providers import GeminiLLMClient, OpenAICompatibleLLMClient


def build_llm_client(*, settings: Settings) -> LLMClient | None:
    provider = settings.llm_provider.strip().lower()
    model = settings.llm_model.strip() if settings.llm_model else None
    api_key = settings.llm_api_key.strip() if settings.llm_api_key else None
    base_url = settings.llm_base_url.strip() if settings.llm_base_url else None

    if provider in {"", "none"}:
        return None

    if not model or not api_key:
        return None

    if provider == "openai_compatible":
        resolved_base_url = base_url or "https://api.openai.com/v1"
        return OpenAICompatibleLLMClient(
            model=model,
            api_key=api_key,
            base_url=resolved_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    if provider == "gemini":
        resolved_base_url = base_url or "https://generativelanguage.googleapis.com/v1beta/models"
        return GeminiLLMClient(
            model=model,
            api_key=api_key,
            base_url=resolved_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    raise ValueError(f"unsupported llm provider: {settings.llm_provider}")
