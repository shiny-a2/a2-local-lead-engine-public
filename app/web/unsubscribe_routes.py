from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.db.session import make_session_factory
from app.services.unsubscribe_service import UnsubscribeService
from app.services.unsubscribe_token_service import UnsubscribeTokenService
from app.settings import get_settings

router = APIRouter()


def _session():
    return make_session_factory(get_settings())()


@router.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe(token: str | None = None) -> HTMLResponse:
    if not token:
        return HTMLResponse("Invalid or already used unsubscribe link.")
    try:
        with _session() as session:
            row = UnsubscribeTokenService(session, get_settings()).find(token)
            if row is None or row.status.value != "ACTIVE":
                return HTMLResponse("Invalid or already used unsubscribe link.")
    except Exception:
        return HTMLResponse("Invalid or already used unsubscribe link.")
    return HTMLResponse(f"<form method='post' action='/unsubscribe/confirm'><input type='hidden' name='token' value='{token}'><button>Unsubscribe</button></form>")


@router.post("/unsubscribe/confirm", response_class=HTMLResponse)
async def unsubscribe_confirm(request: Request) -> HTMLResponse:
    parsed = parse_qs((await request.body()).decode("utf-8"))
    token = parsed.get("token", [""])[-1]
    with _session() as session:
        ok, message = UnsubscribeService(session, get_settings()).confirm(token, request.client.host if request.client else None, request.headers.get("user-agent"))
        session.commit()
    return HTMLResponse("You have been unsubscribed." if ok else message)
