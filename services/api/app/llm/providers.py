import json
from urllib import parse, request

from app.llm.interfaces import LLMClient


class BaseHTTPJsonLLMClient(LLMClient):
    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        timeout_seconds: float,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def _post_json(self, *, url: str, headers: dict[str, str], payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url=url,
            data=body,
            headers=headers,
            method="POST",
        )
        with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))


class OpenAICompatibleLLMClient(BaseHTTPJsonLLMClient):
    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str,
        timeout_seconds: float,
    ) -> None:
        super().__init__(
            model=model,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        self.base_url = base_url.rstrip("/")

    def generate(self, *, system_prompt: str, user_prompt: str) -> dict[str, str]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.9,
        }
        response = self._post_json(
            url=f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            payload=payload,
        )
        choices = response.get("choices", [])
        if not choices:
            raise ValueError("openai-compatible response does not contain choices")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("openai-compatible response does not contain message content")
        return {"content": content.strip()}


class GeminiLLMClient(BaseHTTPJsonLLMClient):
    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str,
        timeout_seconds: float,
    ) -> None:
        super().__init__(
            model=model,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        self.base_url = base_url.rstrip("/")

    def generate(self, *, system_prompt: str, user_prompt: str) -> dict[str, str]:
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.9,
            },
        }
        query = parse.urlencode({"key": self.api_key})
        response = self._post_json(
            url=f"{self.base_url}/{self.model}:generateContent?{query}",
            headers={"Content-Type": "application/json"},
            payload=payload,
        )
        candidates = response.get("candidates", [])
        if not candidates:
            raise ValueError("gemini response does not contain candidates")
        content_parts = candidates[0].get("content", {}).get("parts", [])
        text_part = next(
            (
                part.get("text")
                for part in content_parts
                if isinstance(part.get("text"), str) and part.get("text").strip()
            ),
            None,
        )
        if text_part is None:
            raise ValueError("gemini response does not contain text content")
        return {"content": text_part.strip()}
