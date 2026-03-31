from app.core.config import Settings
from app.llm.factory import build_llm_client
from app.llm.providers import GeminiLLMClient, OpenAICompatibleLLMClient


def test_llm_factory_returns_none_when_provider_is_disabled() -> None:
    settings = Settings(
        llm_provider="none",
        llm_model=None,
        llm_api_key=None,
    )

    client = build_llm_client(settings=settings)

    assert client is None


def test_llm_factory_builds_openai_compatible_client() -> None:
    settings = Settings(
        llm_provider="openai_compatible",
        llm_model="deepseek-chat",
        llm_api_key="secret",
        llm_base_url="https://api.deepseek.com/v1",
    )

    client = build_llm_client(settings=settings)

    assert isinstance(client, OpenAICompatibleLLMClient)
    assert client.model == "deepseek-chat"
    assert client.base_url == "https://api.deepseek.com/v1"


def test_llm_factory_builds_gemini_client_with_default_base_url() -> None:
    settings = Settings(
        llm_provider="gemini",
        llm_model="gemini-2.5-flash",
        llm_api_key="secret",
        llm_base_url=None,
    )

    client = build_llm_client(settings=settings)

    assert isinstance(client, GeminiLLMClient)
    assert client.model == "gemini-2.5-flash"
    assert client.base_url == "https://generativelanguage.googleapis.com/v1beta/models"
