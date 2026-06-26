from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app.core.enums import HumanTaskStatus, OpportunityStatus, Phase12TaskType
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.phase12_human_task import Phase12HumanTask
from app.db.session import make_session_factory
from app.services.opportunity_dashboard_service import OpportunityDashboardService
from app.settings import get_settings

router = APIRouter(prefix="/admin/opportunities")


def _html(title: str, body: str = "") -> HTMLResponse:
    return HTMLResponse(
        '<!doctype html><html lang="fa" dir="rtl"><body>'
        f"<h1>{title}</h1>"
        "<p>فاز ۱۲ فقط راهنمای انسانی می‌سازد. ارسال پاسخ، ارسال قیمت، رزرو جلسه، proposal و payment link وجود ندارد.</p>"
        f"{body}</body></html>"
    )


def _auth(request: Request) -> HTMLResponse | None:
    settings = get_settings()
    if not settings.phase9_basic_auth_enabled:
        return None
    return HTMLResponse("Authentication required", status_code=401)


@router.get("")
def dashboard(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    try:
        with make_session_factory(get_settings())() as session:
            data = OpportunityDashboardService(session).dashboard()
    except Exception:
        data = {"opportunities": 0, "tasks": 0, "pricing_guidance": 0}
    return _html("داشبورد فرصت‌ها", f"<pre>{data}</pre>")


@router.get("/price-requests")
def price_requests(request: Request):
    return _html("درخواست‌های قیمت")


@router.get("/call-requests")
def call_requests(request: Request):
    return _html("درخواست‌های تماس")


@router.get("/tasks")
def tasks(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    try:
        with make_session_factory(get_settings())() as session:
            rows = session.scalars(select(Phase12HumanTask)).all()
    except Exception:
        rows = []
    return _html("وظایف انسانی", "".join(f"<p>{r.task_type.value}</p>" for r in rows))


@router.get("/closed")
def closed(request: Request):
    return _html("لیدهای بسته‌شده")


@router.get("/reports")
def reports(request: Request):
    return _html("گزارش فرصت‌ها")


@router.get("/{opportunity_id}")
def detail(request: Request, opportunity_id: int):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        opp = session.get(OpportunityRecord, opportunity_id)
    body = f"<p>وضعیت: {opp.opportunity_status.value if opp else 'نامشخص'}</p>"
    body += (
        f'<form method="post" action="{opportunity_id}/create-task">'
        "<button>ایجاد وظیفه پاسخ دستی</button></form>"
    )
    body += (
        f'<form method="post" action="{opportunity_id}/close">'
        '<button>بستن فرصت</button><input name="reason" value="manual"></form>'
    )
    return _html("جزئیات فرصت", body)


@router.post("/{opportunity_id}/create-task")
def create_task(request: Request, opportunity_id: int):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        opp = session.get(OpportunityRecord, opportunity_id)
        if opp:
            session.add(
                Phase12HumanTask(
                    opportunity_id=opp.id,
                    candidate_business_id=opp.candidate_business_id,
                    inbound_message_id=opp.source_inbound_message_id,
                    task_type=Phase12TaskType.PREPARE_REPLY,
                    priority="MEDIUM",
                    status=HumanTaskStatus.OPEN,
                    recommended_action="Prepare manually. Do not send automatically.",
                )
            )
            session.commit()
    return RedirectResponse(f"/admin/opportunities/{opportunity_id}", status_code=303)


@router.post("/{opportunity_id}/close")
async def close(request: Request, opportunity_id: int):
    auth = _auth(request)
    if auth:
        return auth
    await request.body()
    with make_session_factory(get_settings())() as session:
        opp = session.get(OpportunityRecord, opportunity_id)
        if opp:
            opp.opportunity_status = OpportunityStatus.CLOSED_NOT_INTERESTED
            session.commit()
    return RedirectResponse(f"/admin/opportunities/{opportunity_id}", status_code=303)


@router.post("/{opportunity_id}/mark-manual-response-needed")
def mark_manual_response(request: Request, opportunity_id: int):
    return RedirectResponse(f"/admin/opportunities/{opportunity_id}", status_code=303)


@router.post("/{opportunity_id}/mark-manual-call-needed")
def mark_manual_call(request: Request, opportunity_id: int):
    return RedirectResponse(f"/admin/opportunities/{opportunity_id}", status_code=303)


@router.post("/tasks/{task_id}/update")
async def update_task(request: Request, task_id: int):
    body = (await request.body()).decode()
    status = parse_qs(body).get("status", ["DONE"])[0]
    with make_session_factory(get_settings())() as session:
        task = session.get(Phase12HumanTask, task_id)
        if task:
            task.status = HumanTaskStatus(status)
            session.commit()
    return RedirectResponse("/admin/opportunities/tasks", status_code=303)
