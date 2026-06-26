from fastapi import APIRouter

from app.settings import get_settings

router = APIRouter()


@router.get("/status")
def status() -> dict[str, object]:
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "app_env": settings.app_env,
        "local_api_only": settings.local_api_only,
        "external_api_status": "disabled/not-called",
        "email_sending": "disabled",
        "voice_calls": "disabled",
        "google_maps": "disabled/prohibited for MVP",
    }

