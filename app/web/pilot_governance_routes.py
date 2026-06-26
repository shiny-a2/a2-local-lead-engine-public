from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from app.db.models.fix_pack_recommendation import FixPackRecommendation
from app.db.models.ops_readiness_check import OpsReadinessCheck
from app.db.models.pilot_audit_run import PilotAuditRun
from app.db.models.risk_register_item import RiskRegisterItem
from app.db.session import make_session_factory
from app.services.phase14_dashboard_service import Phase14DashboardService
from app.settings import get_settings

router = APIRouter(prefix="/admin/pilot")


def _auth(request: Request) -> HTMLResponse | None:
    settings = get_settings()
    if not settings.phase14_governance_dashboard_enabled and not settings.testing:
        return HTMLResponse("Not found", status_code=404)
    if not settings.phase9_basic_auth_enabled:
        return None
    if settings.testing:
        return None
    if not settings.phase9_review_username or not settings.phase9_review_password_hash:
        return HTMLResponse("Authentication required", status_code=401)
    if request.headers.get("x-review-user") != settings.phase9_review_username:
        return HTMLResponse("Authentication required", status_code=401)
    return None


def _page(title: str, body: str = "") -> HTMLResponse:
    return HTMLResponse(
        '<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">'
        '<link rel="stylesheet" href="/static/pilot/pilot_fa.css">'
        f"<title>{title}</title></head><body><main><h1>{title}</h1>"
        '<p class="warning">فاز ۱۴ فقط گزارش حاکمیتی، آمادگی عملیاتی و تصمیم‌گیری انسانی را نمایش می‌دهد. ارسال ایمیل، جمع‌آوری لید، API خارجی، follow-up، پاسخ، قیمت، proposal، جلسه، payment link یا تماس انجام نمی‌شود.</p>'
        f"{body}</main></body></html>"
    )


def _session():
    return make_session_factory(get_settings())()


@router.get("")
def dashboard(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    try:
        with _session() as session:
            data = Phase14DashboardService(session).dashboard()
    except Exception:
        data = {"runs": 0, "risks": 0, "fixpacks": 0, "ops_blockers": 0, "no_outbound": True}
    return _page("داشبورد پایلوت", f"<pre>{data}</pre>")


@router.get("/funnel")
def funnel(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    return _page("قیف کامل سیستم", "<p>نمای کلی از کاندیدها، پیش‌نویس‌ها، ارسال کنترل‌شده، پاسخ‌ها و فرصت‌ها.</p>")


@router.get("/kpis")
def kpis(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    return _page("شاخص‌های کلیدی", "<p>شاخص‌ها از آخرین اجرای audit پایلوت خوانده می‌شوند.</p>")


@router.get("/phase-readiness")
def phase_readiness(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    return _page("وضعیت فازها", "<p>فاز ۱۵ برای MVP به عنوان post-MVP scale علامت‌گذاری می‌شود.</p>")


@router.get("/risks")
def risks(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    with _session() as session:
        rows = session.scalars(select(RiskRegisterItem).order_by(RiskRegisterItem.id.desc())).all()
    body = "".join(f"<p>{row.risk_code} - {row.severity} - {row.title}</p>" for row in rows)
    return _page("ریسک‌ها و هشدارها", body)


@router.get("/fixpacks")
def fixpacks(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    with _session() as session:
        rows = session.scalars(select(FixPackRecommendation).order_by(FixPackRecommendation.id.desc())).all()
    body = "".join(f"<p>{row.code} - {row.priority} - {row.title}</p>" for row in rows)
    return _page("Fix Packها", body)


@router.get("/scale-decision")
def scale_decision(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    return _page("تصمیم توسعه / توقف / اصلاح", "<p>اگر نمونه کافی نباشد تصمیم باید PILOT_INCONCLUSIVE باشد.</p>")


@router.get("/ops-readiness")
def ops_readiness(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    with _session() as session:
        rows = session.scalars(select(OpsReadinessCheck).order_by(OpsReadinessCheck.id.desc())).all()
    body = "".join(f"<p>{row.check_name}: {row.status} ({row.severity})</p>" for row in rows)
    return _page("آمادگی عملیاتی", body)


@router.get("/retention")
def retention(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    return _page("سیاست نگهداری داده", "<p>فایل‌های .env و secretها در export قرار نمی‌گیرند.</p>")


@router.get("/final-report")
def final_report(request: Request):
    auth = _auth(request)
    if auth:
        return auth
    with _session() as session:
        run = session.scalar(select(PilotAuditRun).order_by(PilotAuditRun.id.desc()))
    run_id = run.run_id if run else "هنوز گزارشی ساخته نشده"
    return _page("گزارش نهایی پایلوت", f"<p>آخرین run: <span dir='ltr'>{run_id}</span></p>")
