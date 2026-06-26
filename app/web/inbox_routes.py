from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app.core.enums import HumanTaskStatus, ReplyClassificationValue, SuppressionReason
from app.db.models.bounce_event import BounceEvent
from app.db.models.human_response_task import HumanResponseTask
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.lead_response_timeline import LeadResponseTimeline
from app.db.models.reply_classification import ReplyClassification
from app.db.models.suppression import SuppressionList
from app.db.session import make_session_factory
from app.services.inbound_dashboard_service import InboundDashboardService
from app.services.mailbox_sync_service import MailboxSyncService
from app.settings import get_settings

router = APIRouter(prefix="/admin/inbox")


def _templates():
    try:
        from fastapi.templating import Jinja2Templates
    except ImportError:
        class SimpleTemplates:
            def TemplateResponse(self, name: str, context: dict) -> HTMLResponse:
                title = "داشبورد پاسخ‌ها"
                if "mailbox_readiness" in name:
                    title = "آمادگی صندوق ورودی"
                body = (
                    '<!doctype html><html lang="fa" dir="rtl"><body>'
                    f"<h1>{title}</h1>"
                    "<p>فاز ۱۱ پاسخ ارسال نمی‌کند و ارسال follow-up وجود ندارد.</p>"
                    f"<pre>{context}</pre>"
                    "</body></html>"
                )
                return HTMLResponse(body)

        return SimpleTemplates()

    return Jinja2Templates(directory="app/templates")


def _auth(request: Request) -> HTMLResponse | None:
    settings = get_settings()
    if not settings.phase9_basic_auth_enabled:
        return None
    auth = request.headers.get("authorization", "")
    if settings.phase9_review_username and settings.phase9_review_username in auth:
        return None
    return HTMLResponse("Authentication required", status_code=401)


@router.get("")
def dashboard(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    try:
        with make_session_factory(get_settings())() as session:
            data = InboundDashboardService(session).dashboard()
    except Exception:
        data = {"messages": 0, "bounces": 0, "tasks": 0, "no_outbound": True}
    return _templates().TemplateResponse(
        "inbox/dashboard.html", {"request": request, "data": data}
    )


@router.get("/messages")
def messages(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        rows = InboundDashboardService(session).messages()
    return _templates().TemplateResponse(
        "inbox/messages.html", {"request": request, "messages": rows}
    )


@router.get("/messages/{message_id}")
def message_detail(request: Request, message_id: int):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        message = session.get(InboundEmailMessage, message_id)
        classifications = session.scalars(
            select(ReplyClassification).where(ReplyClassification.inbound_message_id == message_id)
        ).all()
    return _templates().TemplateResponse(
        "inbox/message_detail.html",
        {"request": request, "message": message, "classifications": classifications},
    )


@router.post("/messages/{message_id}/override-classification")
async def override_classification(request: Request, message_id: int):
    auth = _auth(request)
    if auth:
        return auth
    body = (await request.body()).decode()
    form = parse_qs(body)
    value = form.get("classification", ["UNKNOWN_NEEDS_REVIEW"])[0]
    with make_session_factory(get_settings())() as session:
        message = session.get(InboundEmailMessage, message_id)
        if message:
            session.add(
                ReplyClassification(
                    inbound_message_id=message.id,
                    candidate_business_id=message.matched_candidate_business_id,
                    classification=ReplyClassificationValue(value),
                    confidence=1.0,
                    classifier_type="manual",
                    manual_override=True,
                    signals_json={"dashboard_override": True},
                )
            )
            session.commit()
    return RedirectResponse(f"/admin/inbox/messages/{message_id}", status_code=303)


@router.post("/messages/{message_id}/create-task")
async def create_task(request: Request, message_id: int):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        message = session.get(InboundEmailMessage, message_id)
        if message and message.matched_candidate_business_id:
            session.add(
                HumanResponseTask(
                    candidate_business_id=message.matched_candidate_business_id,
                    inbound_message_id=message.id,
                    task_type="REVIEW_UNKNOWN_REPLY",
                    priority="MEDIUM",
                    status=HumanTaskStatus.OPEN,
                    notes="Dashboard-created task. No outbound reply sent.",
                )
            )
            session.commit()
    return RedirectResponse(f"/admin/inbox/messages/{message_id}", status_code=303)


@router.post("/messages/{message_id}/suppress")
def suppress_message(request: Request, message_id: int):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        message = session.get(InboundEmailMessage, message_id)
        if message:
            session.add(
                SuppressionList(
                    email=message.from_email,
                    reason=SuppressionReason.MANUAL_BLOCK,
                    source="phase11_dashboard",
                )
            )
            session.commit()
    return RedirectResponse(f"/admin/inbox/messages/{message_id}", status_code=303)


@router.get("/leads/{candidate_id}/timeline")
def lead_timeline(request: Request, candidate_id: int):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        rows = session.scalars(
            select(LeadResponseTimeline).where(
                LeadResponseTimeline.candidate_business_id == candidate_id
            )
        ).all()
    return _templates().TemplateResponse(
        "inbox/lead_timeline.html", {"request": request, "timeline": rows}
    )


@router.get("/bounces")
def bounces(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        rows = session.scalars(select(BounceEvent)).all()
    return _templates().TemplateResponse(
        "inbox/bounces.html", {"request": request, "bounces": rows}
    )


@router.get("/unsubscribes")
def unsubscribes(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        rows = session.scalars(
            select(ReplyClassification).where(
                ReplyClassification.classification
                == ReplyClassificationValue.UNSUBSCRIBE_REQUEST
            )
        ).all()
    return _templates().TemplateResponse(
        "inbox/unsubscribes.html", {"request": request, "rows": rows}
    )


@router.get("/tasks")
def tasks(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        rows = session.scalars(select(HumanResponseTask)).all()
    return _templates().TemplateResponse(
        "inbox/human_tasks.html", {"request": request, "tasks": rows}
    )


@router.post("/tasks/{task_id}/update")
async def update_task(request: Request, task_id: int):
    auth = _auth(request)
    if auth:
        return auth
    body = (await request.body()).decode()
    status = parse_qs(body).get("status", ["DONE"])[0]
    with make_session_factory(get_settings())() as session:
        task = session.get(HumanResponseTask, task_id)
        if task:
            task.status = HumanTaskStatus(status)
            session.commit()
    return RedirectResponse("/admin/inbox/tasks", status_code=303)


@router.get("/mailbox-readiness")
def mailbox_readiness(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    try:
        with make_session_factory(get_settings())() as session:
            plan = MailboxSyncService(session, get_settings()).plan("default")
            session.commit()
    except Exception:
        plan = {
            "ready": False,
            "gaps": ["DATABASE_UNAVAILABLE"],
            "secrets": "redacted",
            "imports_messages": False,
        }
    return _templates().TemplateResponse(
        "inbox/mailbox_readiness.html", {"request": request, "plan": plan}
    )


@router.get("/reports/{run_id}")
def reports(request: Request, run_id: str):
    auth = _auth(request)
    if auth:
        return auth
    return _templates().TemplateResponse(
        "inbox/reports.html", {"request": request, "run_id": run_id}
    )
