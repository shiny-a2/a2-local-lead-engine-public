import json

from app.services.pre_send_qa_service import PreSendQaService
from app.settings import Settings


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": json.dumps(self._payload)}}]}


def _client(payload):
    from app.services.openai_client import OpenAIClient

    return OpenAIClient(Settings(openai_api_key="sk-x"), http_post=lambda p, h: _Resp(payload))


def test_qa_passes_clean_email():
    qa = PreSendQaService(Settings(openai_api_key="sk-x"), openai_client=_client({"go": True, "issues": []}))
    r = qa.check("Tonic Room", "Auckland", "New Zealand", "info@tonicroom.co.nz", "Website for Tonic Room", "body")
    assert r["go"] is True


def test_qa_blocks_wrong_business():
    payload = {"go": False, "issues": ["recipient email does not match the business"]}
    qa = PreSendQaService(Settings(openai_api_key="sk-x"), openai_client=_client(payload))
    r = qa.check("Loft Skin Clinic", "Auckland", "New Zealand", "info@thebeautyloft.co.nz", "s", "b")
    assert r["go"] is False
    assert r["issues"]


def test_qa_fails_closed_without_key():
    r = PreSendQaService(Settings()).check("B", "C", "New Zealand", "a@b.nz", "s", "b")
    assert r["go"] is False
