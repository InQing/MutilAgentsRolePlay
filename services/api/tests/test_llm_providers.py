from app.llm.providers import GeminiLLMClient, OpenAICompatibleLLMClient


def test_openai_compatible_llm_client_extracts_message_content() -> None:
    client = OpenAICompatibleLLMClient(
        model="deepseek-chat",
        api_key="secret",
        base_url="https://api.deepseek.com/v1",
        timeout_seconds=10.0,
    )
    client._post_json = lambda **_: {
        "choices": [
            {
                "message": {
                    "content": "这是来自兼容接口的内容。"
                }
            }
        ]
    }

    payload = client.generate(
        system_prompt="system",
        user_prompt="user",
    )

    assert payload["content"] == "这是来自兼容接口的内容。"


def test_gemini_llm_client_extracts_candidate_text() -> None:
    client = GeminiLLMClient(
        model="gemini-2.5-flash",
        api_key="secret",
        base_url="https://generativelanguage.googleapis.com/v1beta/models",
        timeout_seconds=10.0,
    )
    client._post_json = lambda **_: {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "这是 Gemini 返回的表达。"}
                    ]
                }
            }
        ]
    }

    payload = client.generate(
        system_prompt="system",
        user_prompt="user",
    )

    assert payload["content"] == "这是 Gemini 返回的表达。"
