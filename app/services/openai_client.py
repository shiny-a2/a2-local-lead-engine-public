import httpx

from app.settings import Settings


class OpenAIClient:
    """Minimal OpenAI Chat Completions client (httpx; no extra SDK dependency).

    Only used when AI generation is explicitly enabled and an API key is set. The key is
    the single card-requiring service the project allows; everything else stays free.
    """

    API_URL = "https://api.openai.com/v1/chat/completions"
    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, settings: Settings, http_post=None):
        self.settings = settings
        self._post = http_post or self._default_post

    def _default_post(self, payload: dict, headers: dict):
        return httpx.post(self.API_URL, json=payload, headers=headers, timeout=60)

    def chat_json(self, system: str, user: str, model: str | None = None) -> str:
        payload = {
            "model": model or self.settings.openai_email_model or self.DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.settings.openai_email_temperature,
            "max_tokens": self.settings.openai_email_max_tokens,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        response = self._post(payload, headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
