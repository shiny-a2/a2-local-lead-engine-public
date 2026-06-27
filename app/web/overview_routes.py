from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select

from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.candidate_lead_score import CandidateLeadScore
from app.db.models.candidate_web_presence_verification import CandidateWebPresenceVerification
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision
from app.db.models.raw_source_record import RawSourceRecord
from app.db.session import make_session_factory
from app.services.country_compliance_service import CountryComplianceService
from app.settings import get_settings

router = APIRouter(prefix="/admin/overview")


def _count(session, model, *where) -> int:
    stmt = select(func.count()).select_from(model)
    for clause in where:
        stmt = stmt.where(clause)
    return int(session.scalar(stmt) or 0)


def _card(label: str, value, hint: str = "") -> str:
    hint_html = f"<div class='hint'>{hint}</div>" if hint else ""
    return f"<div class='card'><div class='num'>{value}</div><div class='lbl'>{label}</div>{hint_html}</div>"


@router.get("", response_class=HTMLResponse)
def overview() -> HTMLResponse:
    settings = get_settings()
    session = make_session_factory(settings)()
    try:
        raw = _count(session, RawSourceRecord)
        candidates = _count(session, CandidateBusiness)
        ready_v = _count(session, CandidateBusiness, CandidateBusiness.status == "READY_FOR_WEBSITE_VERIFICATION")
        verified = _count(session, CandidateWebPresenceVerification)
        scored = _count(session, CandidateLeadScore)
        ready6 = _count(session, Phase5CandidateDecision, Phase5CandidateDecision.ready_for_phase6.is_(True))
        drafts = _count(session, EmailDraftVariant)
        improvement = _count(session, EmailDraftVariant, EmailDraftVariant.campaign_lane == "IMPROVEMENT")
        queued = _count(session, HumanReviewQueueItem)
        send_q = _count(session, EmailSendQueue)

        # contacts
        contact_rows = session.execute(
            select(CandidateContactVerification.contact_status, func.count())
            .group_by(CandidateContactVerification.contact_status)
        ).all()
        contacts = {str(getattr(s, "value", s)): n for s, n in contact_rows}
        allowed_contacts = _count(
            session, CandidateContactVerification,
            CandidateContactVerification.outreach_contact_allowed.is_(True),
        )

        # leads by country
        country_rows = session.execute(
            select(CandidateBusiness.country, func.count())
            .group_by(CandidateBusiness.country)
        ).all()

        # recent drafts
        recent = session.execute(
            select(
                CandidateBusiness.display_name,
                CandidateBusiness.city,
                CandidateBusiness.country,
                EmailDraftVariant.subject_text,
                EmailDraftVariant.status,
            )
            .join(CandidateBusiness, CandidateBusiness.id == EmailDraftVariant.candidate_business_id)
            .order_by(EmailDraftVariant.id.desc())
            .limit(15)
        ).all()
    finally:
        session.close()

    compliance = CountryComplianceService()
    funnel = "".join([
        _card("سرنخ خام (نقشه آزاد)", raw),
        _card("کاندیدای کسب‌وکار", candidates),
        _card("آمادهٔ تأیید وب", ready_v),
        _card("تأیید حضور وب", verified),
        _card("امتیازخورده", scored),
        _card("آماده برای ایمیل", ready6, "تماس امن + شواهد کافی"),
        _card("پیش‌نویس ایمیل (GPT)", drafts),
        _card("ایمیل بهبودِ سایت", improvement, "کمپین جدا - دارای سایت"),
        _card("در صف بازبینی انسانی", queued),
        _card("در صف ارسال", send_q, "ارسال واقعی خاموش است"),
        _card("تماس امن یافت‌شده", allowed_contacts, "ایمیل کاری/نقش‌محور"),
    ])

    contact_html = "".join(
        f"<tr><td>{label}</td><td>{contacts.get(key, 0)}</td></tr>"
        for key, label in [
            ("ROLE_BASED_EMAIL_FOUND", "ایمیل نقش‌محور (مجاز)"),
            ("PERSONAL_EMAIL_FOUND_BLOCKED", "ایمیل شخصی (مسدود)"),
            ("NEEDS_MANUAL_REVIEW", "نیازمند بازبینی"),
            ("NO_CONTACT_FOUND", "بدون تماس"),
        ]
    )

    country_html = ""
    for country, n in sorted(country_rows, key=lambda r: -r[1]):
        ev = compliance.evaluate(country)
        ok = "مجاز ✅" if ev["allowed"] else "مسدود ⛔"
        cls = "ok" if ev["allowed"] else "no"
        country_html += (
            f"<tr><td>{country or 'نامشخص'}</td><td>{n}</td>"
            f"<td class='{cls}'>{ok}</td><td class='law'>{ev['law']}</td></tr>"
        )

    rows = ""
    for name, city, country, subject, status in recent:
        st = str(getattr(status, "value", status))
        rows += (
            f"<tr><td>{name}</td><td>{city or ''} / {country or ''}</td>"
            f"<td>{subject}</td><td class='st'>{st}</td></tr>"
        )
    if not rows:
        rows = "<tr><td colspan='4' class='muted'>هنوز پیش‌نویسی ساخته نشده. خط‌لوله را اجرا کن.</td></tr>"

    html = f"""<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A2 — نمای کلی</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#0c0e14;color:#e8eaf0;
font-family:Tahoma,'Segoe UI',sans-serif;line-height:1.7}}
.wrap{{max-width:1100px;margin:0 auto;padding:24px}}
h1{{font-size:24px;margin:0 0 4px}} .sub{{color:#8b93a7;margin-bottom:20px;font-size:14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin-bottom:26px}}
.card{{background:#161a24;border:1px solid #232838;border-radius:12px;padding:16px;text-align:center}}
.card .num{{font-size:30px;font-weight:700;color:#e23b4e}} .card .lbl{{font-size:13px;color:#c2c7d6;margin-top:4px}}
.card .hint{{font-size:11px;color:#7b8294;margin-top:3px}}
h2{{font-size:17px;margin:24px 0 10px;border-right:3px solid #e23b4e;padding-right:8px}}
table{{width:100%;border-collapse:collapse;background:#11141d;border-radius:10px;overflow:hidden}}
th,td{{padding:9px 12px;text-align:right;border-bottom:1px solid #1e2330;font-size:13px}}
th{{background:#1a1f2b;color:#aeb4c4}} td.ok{{color:#36c08a}} td.no{{color:#e23b4e}}
td.law{{color:#8b93a7;font-size:12px}} td.st{{color:#d8a23b;font-size:12px}} td.muted{{color:#7b8294;text-align:center}}
.flow{{background:#11141d;border:1px solid #232838;border-radius:12px;padding:16px;color:#c2c7d6;font-size:13px}}
.flow b{{color:#e8eaf0}} a{{color:#5b9bff}}
.steps{{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}}
.step{{background:#1a1f2b;border:1px solid #2a3142;border-radius:20px;padding:4px 12px;font-size:12px}}
</style></head><body><div class="wrap">
<h1>داشبورد A2 — نمای کلی</h1>
<div class="sub">یافتنِ کسب‌وکارهای بدونِ وب‌سایت، نوشتنِ ایمیل با هوش مصنوعی، و آماده‌سازی برای ارسالِ قانونی. ارسالِ واقعی تا تأیید تو خاموش است.</div>
<div class="grid">{funnel}</div>
<h2>مسیرِ کار (چه به چی)</h2>
<div class="flow">هر سرنخ این مسیر را طی می‌کند:
<div class="steps">
<span class="step">۱. جمع‌آوری از نقشهٔ آزاد</span><span class="step">۲. ساخت کاندیدا</span>
<span class="step">۳. تأیید وب‌سایت (پروب)</span><span class="step">۴. یافتن ایمیل (Tavily)</span>
<span class="step">۵. امتیازدهی</span><span class="step">۶. پیشنهاد</span>
<span class="step">۷. نوشتن ایمیل (GPT)</span><span class="step">۸. داور + ایجنتِ ارتباط</span>
<span class="step">۹. صف بازبینی انسانی</span><span class="step">۱۰. ارسال (طبق قانونِ کشور)</span>
</div></div>
<h2>یافتنِ تماس</h2><table><tr><th>وضعیت</th><th>تعداد</th></tr>{contact_html}</table>
<h2>سرنخ‌ها و انطباقِ قانونیِ هر کشور</h2>
<table><tr><th>کشور</th><th>سرنخ</th><th>ارسالِ سرد</th><th>قانون</th></tr>{country_html or "<tr><td colspan=4 class=muted>هنوز سرنخی نیست</td></tr>"}</table>
<h2>آخرین ایمیل‌های نوشته‌شده</h2>
<table><tr><th>کسب‌وکار</th><th>شهر/کشور</th><th>موضوع ایمیل</th><th>وضعیت</th></tr>{rows}</table>
<div class="sub" style="margin-top:24px">صفحات دیگر: <a href="/admin/review">صف بازبینی</a> · <a href="/admin/pilot">حاکمیت</a> · <a href="/admin/send">ارسال</a></div>
</div></body></html>"""
    return HTMLResponse(html)
