from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app.core.enums import EmailSendQueueStatus, SuppressionReason
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.suppression import SuppressionList
from app.db.session import make_session_factory
from app.services.phase10_dashboard_service import Phase10DashboardService
from app.settings import get_settings

router = APIRouter(prefix="/admin/send")


def _session():
    return make_session_factory(get_settings())()


def _auth(request: Request) -> None:
    settings = get_settings()
    if not settings.phase10_send_dashboard_enabled and not settings.testing:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="send dashboard disabled")
    if settings.phase9_basic_auth_enabled and settings.phase9_review_username:
        from fastapi import HTTPException, status

        if request.headers.get("x-review-user") != settings.phase9_review_username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth required")


async def _form(request: Request) -> dict[str, str]:
    parsed = parse_qs((await request.body()).decode("utf-8"))
    return {key: values[-1] for key, values in parsed.items() if values}


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"<!doctype html><html lang='fa' dir='rtl'><head><title>{title}</title><link rel='stylesheet' href='/static/send/send_fa.css'></head><body><main><h1>{title}</h1>{body}<p class='warn'>این داشبورد دکمه ارسال گروهی، پیگیری خودکار، inbox sync یا bounce parsing ندارد.</p></main></body></html>")


@router.get("", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    _auth(request)
    return _page("داشبورد ارسال", "<p>وضعیت صف ارسال، آمادگی فرستنده و محدودیت‌ها.</p>")


@router.get("/queue", response_class=HTMLResponse)
def queue(request: Request) -> HTMLResponse:
    _auth(request)
    try:
        with _session() as session:
            rows = session.scalars(select(EmailSendQueue).order_by(EmailSendQueue.id.desc())).all()
            body = "<table><tr><th>شناسه</th><th>گیرنده</th><th>وضعیت</th></tr>"
            for row in rows:
                status = Phase10DashboardService().status_fa(row.queue_status.value)
                body += f"<tr><td><a href='/admin/send/items/{row.id}'>{row.id}</a></td><td>{row.recipient_email}</td><td>{status}</td></tr>"
            body += "</table>"
    except Exception:
        body = "<p>دیتابیس در این context در دسترس نیست.</p>"
    return _page("صف ارسال ایمیل", body)


@router.get("/items/{item_id}", response_class=HTMLResponse)
def item_detail(item_id: int, request: Request) -> HTMLResponse:
    _auth(request)
    with _session() as session:
        item = session.get(EmailSendQueue, item_id)
        if item is None:
            return _page("جزئیات ارسال", "مورد پیدا نشد.")
        status = Phase10DashboardService().status_fa(item.queue_status.value)
        body = f"<p>گیرنده: <span dir='ltr'>{item.recipient_email}</span></p><p>وضعیت: {status}</p><form method='post' action='/admin/send/items/{item_id}/hold'><input name='reason' value='بررسی دستی'><button>نگه‌داشتن</button></form><form method='post' action='/admin/send/items/{item_id}/cancel'><input name='reason' value='لغو توسط اپراتور'><button>لغو</button></form>"
    return _page("جزئیات ارسال", body)


@router.get("/provider-readiness", response_class=HTMLResponse)
def provider_readiness(request: Request) -> HTMLResponse:
    _auth(request)
    return _page("آمادگی فرستنده", "<p>secretها نمایش داده نمی‌شوند. ارسال تست انجام نمی‌شود.</p>")


@router.get("/suppression", response_class=HTMLResponse)
def suppression(request: Request) -> HTMLResponse:
    _auth(request)
    return _page("لیست عدم ارسال", "<form method='post' action='/admin/send/suppression/add'><input name='email'><input name='reason' value='MANUAL_BLOCK'><button>افزودن</button></form>")


@router.post("/suppression/add")
async def suppression_add(request: Request):
    _auth(request)
    form = await _form(request)
    with _session() as session:
        session.add(SuppressionList(email=form.get("email", "").lower() or None, domain=form.get("domain", "").lower() or None, reason=SuppressionReason(form.get("reason", "MANUAL_BLOCK")), source="dashboard"))
        session.commit()
    return RedirectResponse("/admin/send/suppression", status_code=303)


@router.get("/suppression/import", response_class=HTMLResponse)
def suppression_import(request: Request) -> HTMLResponse:
    _auth(request)
    return _page("وارد کردن لیست عدم ارسال", "<p>وارد کردن CSV از CLI امن‌تر است.</p>")


@router.post("/suppression/import")
def suppression_import_post(request: Request):
    _auth(request)
    return RedirectResponse("/admin/send/suppression/import", status_code=303)


@router.post("/items/{item_id}/hold")
async def hold_item(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    with _session() as session:
        item = session.get(EmailSendQueue, item_id)
        if item:
            item.queue_status = EmailSendQueueStatus.HELD_BY_OPERATOR
            item.hold_reason = form.get("reason", "نگه‌داشتن توسط اپراتور")
            session.commit()
    return RedirectResponse(f"/admin/send/items/{item_id}", status_code=303)


@router.post("/items/{item_id}/cancel")
async def cancel_item(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    with _session() as session:
        item = session.get(EmailSendQueue, item_id)
        if item:
            item.queue_status = EmailSendQueueStatus.CANCELLED_BY_OPERATOR
            item.cancel_reason = form.get("reason", "لغو توسط اپراتور")
            session.commit()
    return RedirectResponse(f"/admin/send/items/{item_id}", status_code=303)


@router.get("/unsubscribes", response_class=HTMLResponse)
def unsubscribes(request: Request) -> HTMLResponse:
    _auth(request)
    return _page("رویدادهای لغو اشتراک", "<p>لغو اشتراک‌های ثبت‌شده اینجا نمایش داده می‌شوند.</p>")


@router.get("/reports/{run_id}", response_class=HTMLResponse)
def report(run_id: str, request: Request) -> HTMLResponse:
    _auth(request)
    return _page("گزارش ارسال", f"<p>گزارش اجرا: <span dir='ltr'>{run_id}</span></p>")
