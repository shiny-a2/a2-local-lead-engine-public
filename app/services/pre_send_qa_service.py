import json

from app.services.openai_client import OpenAIClient
from app.settings import Settings


class PreSendQaService:
    """Final no-blunder gate before a real send. A GPT reviewer confirms, for one email:
      1. the recipient address plausibly belongs to THIS specific business (not a same-named
         business elsewhere, not a directory/aggregator);
      2. the text correctly names this business and fits its category/location;
      3. the text is fluent and professional with NO garbled/mojibake characters or obvious
         errors; and
      4. there are no false or hallucinated claims.
    Anything less than a clean pass is blocked (fails CLOSED).
    """

    def __init__(self, settings: Settings, openai_client=None):
        self.settings = settings
        self._client = openai_client

    def check(
        self,
        business_name: str,
        city: str | None,
        country: str | None,
        recipient_email: str,
        subject: str,
        body: str,
    ) -> dict:
        if not self.settings.openai_api_key and self._client is None:
            return {"go": False, "issues": ["pre-send QA enabled but no OpenAI key"]}
        client = self._client or OpenAIClient(self.settings)
        system = (
            "You are the final QA gate before a cold B2B email is actually sent. Be strict and "
            "block anything embarrassing. Check ALL of: (1) the recipient email plausibly belongs "
            "to THIS exact business (same name AND same country/city; a same-named business in "
            "another country, or a directory/aggregator/marketplace address, is a FAIL); (2) the "
            "email text names this business correctly and fits its category and location; (3) the "
            "text is fluent, professional English with NO garbled or mojibake characters, broken "
            "words, or placeholder tokens, and the business name in the text is spelled cleanly; "
            "(4) no invented facts, fake awards, prices, or guarantees. Return ONLY JSON: "
            '{"go": true/false, "issues": ["short reason", ...]}. go=true ONLY if every check passes.'
        )
        user = json.dumps(
            {
                "business_name": business_name,
                "city": city,
                "country": country,
                "recipient_email": recipient_email,
                "email_subject": subject,
                "email_body": body,
            },
            ensure_ascii=False,
        )
        try:
            data = json.loads(client.chat_json(system, user))
            return {
                "go": bool(data.get("go", False)),
                "issues": [str(x)[:200] for x in (data.get("issues") or [])],
            }
        except Exception as exc:  # noqa: BLE001 - fail closed
            return {"go": False, "issues": [f"QA check failed: {type(exc).__name__}"]}
