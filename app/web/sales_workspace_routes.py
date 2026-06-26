from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app.core.enums import (
    ChecklistItemStatus,
    ManualCommunicationType,
    OpportunityCloseReason,
    ProposalChecklistItemStatus,
    SalesTaskStatus,
)
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.proposal_checklist_item import ProposalChecklistItem
from app.db.models.sales_task import SalesTask
from app.db.models.scope_checklist_item import ScopeChecklistItem
from app.db.session import make_session_factory
from app.services.internal_pricing_worksheet_service import InternalPricingWorksheetService
from app.services.manual_communication_log_service import ManualCommunicationLogService
from app.services.opportunity_close_service import OpportunityCloseService
from app.services.phase13_dashboard_service import Phase13DashboardService
from app.services.proposal_readiness_gate_service import ProposalReadinessGateService
from app.services.quote_readiness_gate_service import QuoteReadinessGateService
from app.services.sales_task_service import SalesTaskService
from app.services.scope_completeness_service import ScopeCompletenessService
from app.settings import get_settings
from app.web.sales_workspace_view_models import status_label

router = APIRouter(prefix="/admin/sales")


def _auth(request: Request) -> HTMLResponse | None:
    settings = get_settings()
    if not settings.phase9_basic_auth_enabled:
        return None
    return HTMLResponse("Authentication required", status_code=401)


def _html(title: str, body: str = "") -> HTMLResponse:
    return HTMLResponse(
        '<!doctype html><html lang="fa" dir="rtl"><head>'
        '<meta charset="utf-8"><link rel="stylesheet" href="/static/sales_workspace/sales_workspace_fa.css">'
        f"<title>{title}</title></head><body><main><h1>{title}</h1>"
        '<p class="warning">فاز ۱۳ فقط فضای فروش دستی است: ارسال پاسخ، follow-up، quote، proposal، رزرو جلسه، payment link و تماس خودکار انجام نمی‌شود.</p>'
        f"{body}</main></body></html>"
    )


def _ltr(text: str) -> str:
    return f'<span dir="ltr">{text}</span>'


@router.get("")
def dashboard(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    try:
        with make_session_factory(get_settings())() as session:
            data = Phase13DashboardService(session).dashboard()
    except Exception:
        data = {"workspace_items": 0, "open_tasks": 0, "closed": 0, "outbound_actions": False}
    return _html("داشبورد فروش دستی", f"<pre>{data}</pre>")


@router.get("/kanban")
def kanban(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    return _html("کانبان فرصت‌ها", "<p>ستون‌ها فقط وضعیت‌های انسانی را نمایش می‌دهند.</p>")


@router.get("/opportunities")
def opportunities(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    try:
        with make_session_factory(get_settings())() as session:
            rows = session.scalars(select(OpportunityRecord)).all()
    except Exception:
        rows = []
    body = "".join(
        f'<p><a href="/admin/sales/opportunities/{row.id}">فرصت #{row.id}</a> - {status_label(row.opportunity_status.value)}</p>'
        for row in rows
    )
    return _html("فرصت‌های باز", body)


@router.get("/opportunities/{opportunity_id}")
def opportunity_detail(request: Request, opportunity_id: int):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        data = Phase13DashboardService(session).detail(opportunity_id)
    opportunity = data["opportunity"]
    status = opportunity.opportunity_status.value if opportunity else "نامشخص"
    body = f"<h2>جزئیات فرصت</h2><p>وضعیت: {_ltr(status)}</p>"
    body += '<section><h3>راهنمای انسانی</h3><p>پاسخ، قیمت، Proposal و جلسه فقط توسط انسان و بیرون از سیستم انجام می‌شود.</p></section>'
    body += f'<p><a href="/admin/sales/opportunities/{opportunity_id}/scope">Scope</a></p>'
    body += f'<p><a href="/admin/sales/opportunities/{opportunity_id}/proposal">Proposal checklist</a></p>'
    body += f'<p><a href="/admin/sales/opportunities/{opportunity_id}/pricing">Internal pricing</a></p>'
    body += (
        f'<form method="post" action="/admin/sales/opportunities/{opportunity_id}/task/create">'
        '<button>ساخت task</button></form>'
    )
    body += (
        f'<form method="post" action="/admin/sales/opportunities/{opportunity_id}/communication-log">'
        '<input name="summary" value="ثبت اقدام دستی"><button>ثبت یادداشت / اقدام دستی</button></form>'
    )
    body += (
        f'<form method="post" action="/admin/sales/opportunities/{opportunity_id}/close">'
        '<input name="reason" value="MANUAL_DECISION"><button>بستن فرصت</button></form>'
    )
    return _html("جزئیات فرصت", body)


@router.get("/opportunities/{opportunity_id}/scope")
def scope_page(request: Request, opportunity_id: int):
    auth = _auth(request)
    if auth:
        return auth
    with make_session_factory(get_settings())() as session:
        items = session.scalars(select(ScopeChecklistItem)).all()
    body = "".join(f"<p>{item.item_key}: {item.status.value}</p>" for item in items)
    return _html("نیازمند دریافت Scope", body)


@router.post("/scope-items/{item_id}/update")
async def update_scope_item(request: Request, item_id: int):
    body = parse_qs((await request.body()).decode())
    with make_session_factory(get_settings())() as session:
        item = session.get(ScopeChecklistItem, item_id)
        if item:
            item.answer_text = body.get("answer", [""])[0]
            item.status = ChecklistItemStatus(body.get("status", ["ANSWERED"])[0])
            from app.db.models.scope_checklist import ScopeChecklist

            checklist = session.get(ScopeChecklist, item.scope_checklist_id)
            if checklist:
                ScopeCompletenessService(session, get_settings()).calculate(checklist)
            session.commit()
    return RedirectResponse("/admin/sales/opportunities", status_code=303)


@router.get("/opportunities/{opportunity_id}/proposal")
def proposal_page(request: Request, opportunity_id: int):
    auth = _auth(request)
    if auth:
        return auth
    return _html("چک‌لیست Proposal", "<p>هیچ Proposal مشتری‌محور تولید یا ارسال نمی‌شود.</p>")


@router.post("/proposal-items/{item_id}/update")
async def update_proposal_item(request: Request, item_id: int):
    body = parse_qs((await request.body()).decode())
    with make_session_factory(get_settings())() as session:
        item = session.get(ProposalChecklistItem, item_id)
        if item:
            item.status = ProposalChecklistItemStatus(body.get("status", ["READY"])[0])
            item.notes = body.get("notes", [""])[0]
            from app.db.models.proposal_checklist import ProposalChecklist

            checklist = session.get(ProposalChecklist, item.proposal_checklist_id)
            if checklist:
                ProposalReadinessGateService(session, get_settings()).evaluate(checklist)
            session.commit()
    return RedirectResponse("/admin/sales/opportunities", status_code=303)


@router.get("/opportunities/{opportunity_id}/pricing")
def pricing_page(request: Request, opportunity_id: int):
    auth = _auth(request)
    if auth:
        return auth
    return _html("آماده‌سازی قیمت دستی", "<p>قیمت داخلی است و quote مشتری‌محور خودکار تولید نمی‌شود.</p>")


@router.post("/opportunities/{opportunity_id}/pricing/update")
async def pricing_update(request: Request, opportunity_id: int):
    body = parse_qs((await request.body()).decode())
    amount = float(body.get("manual_base_price", ["0"])[0])
    notes = body.get("notes", [""])[0]
    with make_session_factory(get_settings())() as session:
        InternalPricingWorksheetService(session).update_manual_price(opportunity_id, amount, notes)
        QuoteReadinessGateService(session).evaluate(opportunity_id)
        session.commit()
    return RedirectResponse(f"/admin/sales/opportunities/{opportunity_id}/pricing", status_code=303)


@router.post("/opportunities/{opportunity_id}/quote/approve-manual")
async def quote_approve_manual(request: Request, opportunity_id: int):
    body = parse_qs((await request.body()).decode())
    with make_session_factory(get_settings())() as session:
        InternalPricingWorksheetService(session).approve_manually(
            opportunity_id, body.get("approved_by", ["Amirali"])[0], body.get("notes", [""])[0]
        )
        QuoteReadinessGateService(session).evaluate(opportunity_id)
        session.commit()
    return RedirectResponse(f"/admin/sales/opportunities/{opportunity_id}/pricing", status_code=303)


@router.post("/opportunities/{opportunity_id}/task/create")
def create_task(request: Request, opportunity_id: int):
    with make_session_factory(get_settings())() as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity:
            SalesTaskService(session, get_settings()).create_initial_tasks(opportunity)
            session.commit()
    return RedirectResponse(f"/admin/sales/opportunities/{opportunity_id}", status_code=303)


@router.post("/sales/tasks/{task_id}/update")
@router.post("/tasks/{task_id}/update")
async def update_task(request: Request, task_id: int):
    body = parse_qs((await request.body()).decode())
    with make_session_factory(get_settings())() as session:
        task = session.get(SalesTask, task_id)
        if task:
            task.status = SalesTaskStatus(body.get("status", ["DONE"])[0])
            session.commit()
    return RedirectResponse("/admin/sales/tasks", status_code=303)


@router.post("/opportunities/{opportunity_id}/communication-log")
async def communication_log(request: Request, opportunity_id: int):
    body = parse_qs((await request.body()).decode())
    with make_session_factory(get_settings())() as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity:
            ManualCommunicationLogService(session).log(
                opportunity,
                ManualCommunicationType.MANUAL_REPLY_SENT,
                body.get("summary", ["ثبت اقدام دستی"])[0],
                "Amirali",
            )
            session.commit()
    return RedirectResponse(f"/admin/sales/opportunities/{opportunity_id}", status_code=303)


@router.post("/opportunities/{opportunity_id}/close")
async def close(request: Request, opportunity_id: int):
    body = parse_qs((await request.body()).decode())
    with make_session_factory(get_settings())() as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity:
            OpportunityCloseService(session).close(
                opportunity,
                OpportunityCloseReason(body.get("reason", ["MANUAL_DECISION"])[0]),
                "Amirali",
                body.get("notes", [""])[0],
            )
            session.commit()
    return RedirectResponse(f"/admin/sales/opportunities/{opportunity_id}", status_code=303)


@router.get("/tasks")
def tasks(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    return _html("وظایف فروش", "<p>taskهای فروش فقط برای اقدام انسانی هستند.</p>")


@router.get("/reports")
def reports(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    return _html("گزارش فرصت‌ها", "<p>گزارش فضای فروش دستی.</p>")
