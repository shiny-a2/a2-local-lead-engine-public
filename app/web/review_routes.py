from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.human_review_audit_event import HumanReviewAuditEvent
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.session import make_session_factory
from app.services.dashboard_auth_service import DashboardAuthService
from app.services.final_pre_send_review_service import FinalPreSendReviewService
from app.services.human_decision_service import HumanDecisionService
from app.services.manual_edit_service import ManualEditService
from app.services.review_lock_service import ReviewLockService
from app.settings import get_settings

router = APIRouter(prefix="/admin/review")


def _session():
    return make_session_factory(get_settings())()


def _auth(request: Request) -> None:
    DashboardAuthService(get_settings()).require(request)


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        f"""<!doctype html><html><head><title>{title}</title><link rel="stylesheet" href="/static/review/review.css"></head><body><main><h1>{title}</h1>{body}<p class="safe">No send, schedule, inbox sync, or bounce processing exists in Phase 9.</p></main></body></html>"""
    )


async def _form(request: Request) -> dict[str, str]:
    raw = (await request.body()).decode("utf-8")
    parsed = parse_qs(raw)
    return {key: values[-1] for key, values in parsed.items() if values}


@router.get("", response_class=HTMLResponse)
def queue(request: Request) -> HTMLResponse:
    _auth(request)
    try:
        with _session() as session:
            rows = session.scalars(select(HumanReviewQueueItem).order_by(HumanReviewQueueItem.id.desc())).all()
            body = "<table><tr><th>ID</th><th>Candidate</th><th>Draft</th><th>Status</th><th>Lane</th></tr>"
            for row in rows:
                body += f"<tr><td><a href='/admin/review/items/{row.id}'>{row.id}</a></td><td>{row.candidate_business_id}</td><td>{row.email_draft_variant_id}</td><td>{row.queue_status.value}</td><td>{row.campaign_lane or ''}</td></tr>"
            body += "</table>"
    except Exception:
        body = "<p>Review dashboard is private. Database is not available in this context.</p>"
    return _page("Human Review Queue", body)


@router.get("/items/{item_id}", response_class=HTMLResponse)
def detail(item_id: int, request: Request) -> HTMLResponse:
    _auth(request)
    with _session() as session:
        item = session.get(HumanReviewQueueItem, item_id)
        if item is None:
            return _page("Not Found", "Queue item not found.")
        draft = session.get(EmailDraftVariant, item.email_draft_variant_id)
        judge = session.scalar(select(EmailJudgeDecision).where(EmailJudgeDecision.email_draft_variant_id == item.email_draft_variant_id).order_by(EmailJudgeDecision.id.desc()))
        body = f"""
        <section><h2>Draft</h2><p><strong>{draft.subject_text if draft else ''}</strong></p><pre>{draft.body_text if draft else ''}</pre></section>
        <section><h2>Judge</h2><p>{judge.decision.value if judge else 'missing'}</p></section>
        <section><h2>Evidence</h2><p>Evidence and claim panels are read-only in Phase 9.</p></section>
        <section><h2>Sender Readiness</h2><p>Metadata only. SMTP secrets are not stored.</p></section>
        <section><h2>Mailbox Readiness</h2><p>Inbox and bounce handling are future phases.</p></section>
        <form method="post" action="/admin/review/items/{item_id}/final-check"><button>Run Final Check</button></form>
        <form method="post" action="/admin/review/items/{item_id}/approve-phase10"><input name="reviewer" value="Amirali"><input name="notes" value=""><button>Approve for Phase 10 Queue</button></form>
        """
    return _page(f"Review Item {item_id}", body)


@router.get("/items/{item_id}/history", response_class=HTMLResponse)
def history(item_id: int, request: Request) -> HTMLResponse:
    _auth(request)
    with _session() as session:
        rows = session.scalars(select(HumanReviewAuditEvent).where(HumanReviewAuditEvent.queue_item_id == item_id)).all()
        body = "".join(f"<p>{row.action.value}: {row.reason or ''}</p>" for row in rows)
    return _page("Review History", body)


@router.get("/items/{item_id}/final-check", response_class=HTMLResponse)
def final_check_page(item_id: int, request: Request) -> HTMLResponse:
    _auth(request)
    return _page("Final Check", f"<form method='post' action='/admin/review/items/{item_id}/final-check'><button>Run final pre-send check</button></form>")


@router.post("/items/{item_id}/final-check")
def final_check(item_id: int, request: Request):
    _auth(request)
    with _session() as session:
        FinalPreSendReviewService(session, get_settings()).run(item_id)
        session.commit()
    return RedirectResponse(f"/admin/review/items/{item_id}", status_code=303)


@router.get("/items/{item_id}/edit", response_class=HTMLResponse)
def edit_page(item_id: int, request: Request) -> HTMLResponse:
    _auth(request)
    with _session() as session:
        item = session.get(HumanReviewQueueItem, item_id)
        draft = session.get(EmailDraftVariant, item.email_draft_variant_id) if item else None
    return _page("Edit Draft", f"<form method='post'><input name='subject' value='{draft.subject_text if draft else ''}'><textarea name='body'>{draft.body_text if draft else ''}</textarea><input name='editor' value='Amirali'><input name='reason' value='Manual correction'><button>Save version</button></form>")


@router.post("/items/{item_id}/edit")
async def edit(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    subject = form.get("subject", "Manual edited subject")
    body = form.get("body", "")
    editor = form.get("editor", "Amirali")
    reason = form.get("reason", "Manual correction")
    with _session() as session:
        ManualEditService(session, get_settings()).create_version(item_id, subject, body, editor, reason)
        session.commit()
    return RedirectResponse(f"/admin/review/items/{item_id}", status_code=303)


@router.post("/items/{item_id}/approve-phase10")
async def approve(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    reviewer = form.get("reviewer", "Amirali")
    notes = form.get("notes", "")
    with _session() as session:
        HumanDecisionService(session, get_settings()).approve(item_id, reviewer, notes)
        session.commit()
    return RedirectResponse(f"/admin/review/items/{item_id}", status_code=303)


@router.post("/items/{item_id}/reject")
async def reject(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    reviewer = form.get("reviewer", "Amirali")
    reason = form.get("reason", "Rejected by reviewer")
    with _session() as session:
        HumanDecisionService(session, get_settings()).reject(item_id, reviewer, reason)
        session.commit()
    return RedirectResponse("/admin/review", status_code=303)


@router.post("/items/{item_id}/hold")
async def hold(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    reviewer = form.get("reviewer", "Amirali")
    reason = form.get("reason", "Held by reviewer")
    with _session() as session:
        HumanDecisionService(session, get_settings()).hold(item_id, reviewer, reason)
        session.commit()
    return RedirectResponse("/admin/review", status_code=303)


@router.post("/items/{item_id}/return-phase7")
async def return_phase7(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    reviewer = form.get("reviewer", "Amirali")
    reason = form.get("reason", "Needs rewrite")
    with _session() as session:
        HumanDecisionService(session, get_settings()).return_rewrite(item_id, reviewer, reason)
        session.commit()
    return RedirectResponse("/admin/review", status_code=303)


@router.post("/items/{item_id}/return-phase8")
async def return_phase8(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    reviewer = form.get("reviewer", "Amirali")
    reason = form.get("reason", "Needs rejudge")
    with _session() as session:
        HumanDecisionService(session, get_settings()).return_judge(item_id, reviewer, reason)
        session.commit()
    return RedirectResponse("/admin/review", status_code=303)


@router.post("/items/{item_id}/lock")
async def lock(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    reviewer = form.get("reviewer", "Amirali")
    with _session() as session:
        ReviewLockService(session, get_settings()).lock(item_id, reviewer)
        session.commit()
    return RedirectResponse(f"/admin/review/items/{item_id}", status_code=303)


@router.post("/items/{item_id}/unlock")
async def unlock(item_id: int, request: Request):
    _auth(request)
    form = await _form(request)
    reviewer = form.get("reviewer", "Amirali")
    with _session() as session:
        ReviewLockService(session, get_settings()).unlock(item_id, reviewer)
        session.commit()
    return RedirectResponse(f"/admin/review/items/{item_id}", status_code=303)
