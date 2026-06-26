from fastapi import APIRouter, Request

from app.db.session import make_session_factory
from app.services.provider_webhook_ingestion_service import ProviderWebhookIngestionService
from app.settings import get_settings

router = APIRouter(prefix="/webhooks")


@router.post("/{provider_type}/inbound")
async def inbound_webhook(provider_type: str, request: Request) -> dict:
    settings = get_settings()
    signature_valid = request.headers.get("x-a2-signature-valid") == "true"
    payload = await request.json()
    with make_session_factory(settings)() as session:
        row = ProviderWebhookIngestionService(session, settings).ingest(
            provider_type, payload, signature_valid
        )
        session.commit()
    return {"accepted": bool(row and row.signature_valid), "outbound_sent": False}
