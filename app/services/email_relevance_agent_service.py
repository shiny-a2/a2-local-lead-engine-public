import json

from app.services.openai_client import OpenAIClient
from app.settings import Settings


class EmailRelevanceAgentService:
    """Final-stage AI agent: confirm a drafted email truly belongs to THIS business.

    Catches wrong-business contacts, generic copy, and hallucinated facts before a draft
    can reach the send queue. Returns a verdict; the judge blocks low-relevance drafts.
    """

    def __init__(self, settings: Settings, openai_client=None):
        self.settings = settings
        self._client = openai_client

    def check(
        self,
        business_name: str,
        city: str | None,
        category: str | None,
        subject: str,
        body: str,
    ) -> dict:
        if not self.settings.openai_api_key and self._client is None:
            # Fail CLOSED: if the agent is on but cannot run, send the draft to manual review
            # rather than silently passing it.
            return {
                "relevant": False,
                "score": 0,
                "reason": "relevance agent enabled but no OpenAI key - manual review required",
            }
        client = self._client or OpenAIClient(self.settings)
        system = (
            "You are a strict reviewer of cold outreach emails. Decide whether the drafted "
            "email is specifically and correctly about the GIVEN business. It must address the "
            "right business name, fit its category and location, mention no other/competitor "
            "business, and invent no facts (no fake services, awards, prices, or claims). If the "
            "email is generic boilerplate that could be sent to anyone, that is NOT relevant. "
            'Return ONLY JSON: {"relevant": true/false, "score": 0-100, "reason": "short reason"}.'
        )
        user = json.dumps(
            {
                "business_name": business_name,
                "city": city,
                "category": category,
                "email_subject": subject,
                "email_body": body,
            },
            ensure_ascii=False,
        )
        try:
            data = json.loads(client.chat_json(system, user))
            return {
                "relevant": bool(data.get("relevant", False)),
                "score": int(data.get("score", 0)),
                "reason": str(data.get("reason", ""))[:300],
            }
        except Exception as exc:  # noqa: BLE001 - fail safe (treat as needs review)
            return {"relevant": False, "score": 0, "reason": f"relevance check failed: {type(exc).__name__}"}
