import html

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
from app.db.models.suppression import SuppressionList
from app.db.session import make_session_factory
from app.services.country_compliance_service import CountryComplianceService
from app.settings import get_settings

router = APIRouter(prefix="/admin/overview")

STYLE = """
*{box-sizing:border-box} body{margin:0;background:#0c0e14;color:#e8eaf0;
font-family:Tahoma,'Segoe UI',sans-serif;line-height:1.8}
.wrap{max-width:1150px;margin:0 auto;padding:24px}
h1{font-size:24px;margin:0 0 4px} .sub{color:#8b93a7;margin-bottom:18px;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(165px,1fr));gap:12px;margin-bottom:22px}
.card{background:#161a24;border:1px solid #232838;border-radius:12px;padding:15px;text-align:center}
.card .num{font-size:28px;font-weight:700;color:#e23b4e} .card .lbl{font-size:12.5px;color:#c2c7d6;margin-top:4px}
.card .hint{font-size:11px;color:#7b8294;margin-top:3px}
h2{font-size:17px;margin:22px 0 10px;border-right:3px solid #e23b4e;padding-right:8px}
table{width:100%;border-collapse:collapse;background:#11141d;border-radius:10px;overflow:hidden}
th,td{padding:9px 12px;text-align:right;border-bottom:1px solid #1e2330;font-size:13px;vertical-align:top}
th{background:#1a1f2b;color:#aeb4c4} td.ok{color:#36c08a} td.no{color:#e23b4e}
td.law{color:#8b93a7;font-size:12px} td.st{color:#d8a23b;font-size:12px} td.muted{color:#7b8294;text-align:center}
.flow{background:#11141d;border:1px solid #232838;border-radius:12px;padding:14px;color:#c2c7d6;font-size:13px}
a{color:#5b9bff;text-decoration:none} a:hover{text-decoration:underline}
.steps{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.step{background:#1a1f2b;border:1px solid #2a3142;border-radius:20px;padding:4px 12px;font-size:12px}
.email{background:#11141d;border:1px solid #232838;border-radius:12px;padding:18px;white-space:pre-wrap;
font-size:13.5px;color:#dfe3ee;direction:ltr;text-align:left}
.meta{display:flex;flex-wrap:wrap;gap:18px;margin-bottom:14px;font-size:13px;color:#c2c7d6}
.meta b{color:#e8eaf0} .pill{background:#1a1f2b;border:1px solid #2a3142;border-radius:6px;padding:2px 9px;font-size:12px}
"""


def _count(session, model, *where) -> int:
    stmt = select(func.count()).select_from(model)
    for clause in where:
        stmt = stmt.where(clause)
    return int(session.scalar(stmt) or 0)


def _card(label, value, hint="") -> str:
    h = f"<div class='hint'>{hint}</div>" if hint else ""
    return f"<div class='card'><div class='num'>{value}</div><div class='lbl'>{label}</div>{h}</div>"


def _esc(v) -> str:
    return html.escape(str(v if v is not None else ""))


@router.get("", response_class=HTMLResponse)
def overview() -> HTMLResponse:
    session = make_session_factory(get_settings())()
    try:
        raw = _count(session, RawSourceRecord)
        candidates = _count(session, CandidateBusiness)
        verified = _count(session, CandidateWebPresenceVerification)
        scored = _count(session, CandidateLeadScore)
        ready6 = _count(session, Phase5CandidateDecision, Phase5CandidateDecision.ready_for_phase6.is_(True))
        drafts = _count(session, EmailDraftVariant)
        improvement = _count(session, EmailDraftVariant, EmailDraftVariant.campaign_lane == "IMPROVEMENT")
        queued = _count(session, HumanReviewQueueItem)
        send_q = _count(session, EmailSendQueue)
        allowed_contacts = _count(session, CandidateContactVerification, CandidateContactVerification.outreach_contact_allowed.is_(True))
        suppressed = _count(session, SuppressionList)

        contact_rows = session.execute(
            select(CandidateContactVerification.contact_status, func.count()).group_by(CandidateContactVerification.contact_status)
        ).all()
        contacts = {str(getattr(s, "value", s)): n for s, n in contact_rows}
        country_rows = session.execute(
            select(CandidateBusiness.country, func.count()).group_by(CandidateBusiness.country)
        ).all()
        recent = session.execute(
            select(EmailDraftVariant.id, CandidateBusiness.display_name, CandidateBusiness.city,
                   CandidateBusiness.country, EmailDraftVariant.subject_text, EmailDraftVariant.status,
                   EmailDraftVariant.campaign_lane)
            .join(CandidateBusiness, CandidateBusiness.id == EmailDraftVariant.candidate_business_id)
            .order_by(EmailDraftVariant.id.desc()).limit(20)
        ).all()
        supp_rows = session.execute(
            select(SuppressionList.email, SuppressionList.domain, SuppressionList.reason, SuppressionList.source)
            .order_by(SuppressionList.id.desc()).limit(15)
        ).all()
    finally:
        session.close()

    compliance = CountryComplianceService()
    funnel = "".join([
        _card("سرنخ خام (نقشه آزاد)", raw), _card("کاندیدای کسب‌وکار", candidates),
        _card("تأیید حضور وب", verified), _card("امتیازخورده", scored),
        _card("آماده برای ایمیل", ready6, "تماس امن + شواهد"),
        _card("تماس امن یافت‌شده", allowed_contacts, "ایمیل کاری/نقش‌محور"),
        _card("پیش‌نویس ایمیل (GPT)", drafts), _card("ایمیل بهبودِ سایت", improvement, "کمپین جدا"),
        _card("در صف بازبینی", queued), _card("در صف ارسال", send_q, "ارسال خاموش"),
        _card("لغو/سرکوب‌شده", suppressed, "دیگر ایمیل نمی‌شود"),
    ])
    contact_html = "".join(
        f"<tr><td>{label}</td><td>{contacts.get(key, 0)}</td></tr>"
        for key, label in [("ROLE_BASED_EMAIL_FOUND", "ایمیل نقش‌محور (مجاز)"),
                           ("PERSONAL_EMAIL_FOUND_BLOCKED", "ایمیل شخصی (مسدود)"),
                           ("NEEDS_MANUAL_REVIEW", "نیازمند بازبینی"), ("NO_CONTACT_FOUND", "بدون تماس")]
    )
    country_html = ""
    for country, n in sorted(country_rows, key=lambda r: -r[1]):
        ev = compliance.evaluate(country)
        ok = "ارسال با لغو ✅" if ev["allowed"] else "مسدود (رضایت لازم) ⛔"
        country_html += (f"<tr><td>{_esc(country) or 'نامشخص'}</td><td>{n}</td>"
                         f"<td class='{'ok' if ev['allowed'] else 'no'}'>{ok}</td><td class='law'>{_esc(ev['law'])}</td></tr>")
    rows = ""
    for did, name, city, country, subject, status, lane in recent:
        st = str(getattr(status, "value", status))
        tag = "بهبود" if lane == "IMPROVEMENT" else "سایت جدید"
        rows += (f"<tr><td><a href='/admin/overview/email/{did}'>{_esc(name)}</a></td>"
                 f"<td>{_esc(city)} / {_esc(country)}</td><td>{_esc(subject)}</td>"
                 f"<td class='st'>{_esc(st)}</td><td>{tag}</td></tr>")
    if not rows:
        rows = "<tr><td colspan='5' class='muted'>هنوز ایمیلی ساخته نشده.</td></tr>"
    supp_html = ""
    for email, domain, reason, source in supp_rows:
        supp_html += f"<tr><td>{_esc(email or domain)}</td><td>{_esc(getattr(reason,'value',reason))}</td><td>{_esc(source)}</td></tr>"
    if not supp_html:
        supp_html = "<tr><td colspan='3' class='muted'>هنوز کسی لغو نکرده.</td></tr>"

    body = f"""<div class="wrap">
<h1>داشبورد A2 — نمای کلی</h1>
<div class="sub">یافتنِ کسب‌وکارها، نوشتنِ ایمیل با هوش مصنوعی، و آماده‌سازیِ ارسالِ قانونی. ارسالِ واقعی تا تأیید تو خاموش است.</div>
<div class="grid">{funnel}</div>
<h2>مسیرِ کار (چه به چی)</h2>
<div class="flow">هر سرنخ این مسیر را طی می‌کند:
<div class="steps"><span class="step">۱. نقشهٔ آزاد</span><span class="step">۲. کاندیدا</span>
<span class="step">۳. تأیید وب</span><span class="step">۴. یافتن ایمیل (Tavily)</span><span class="step">۵. امتیاز</span>
<span class="step">۶. پیشنهاد</span><span class="step">۷. نوشتن (GPT)</span><span class="step">۸. داور + ارتباط</span>
<span class="step">۹. بازبینی انسانی</span><span class="step">۱۰. ارسال طبق قانونِ کشور + لغو</span></div></div>
<h2>یافتنِ تماس</h2><table><tr><th>وضعیت</th><th>تعداد</th></tr>{contact_html}</table>
<h2>سرنخ‌ها و قانونِ هر کشور</h2><table><tr><th>کشور</th><th>سرنخ</th><th>ارسالِ سرد</th><th>قانون</th></tr>{country_html or "<tr><td colspan=4 class=muted>—</td></tr>"}</table>
<h2>لیستِ لغو / سرکوب (دیگر ارسال و فالو‌آپ نمی‌شوند)</h2><table><tr><th>ایمیل/دامنه</th><th>دلیل</th><th>منبع</th></tr>{supp_html}</table>
<h2>آخرین ایمیل‌ها (برای دیدنِ متن کلیک کن)</h2>
<table><tr><th>کسب‌وکار</th><th>شهر/کشور</th><th>موضوع</th><th>وضعیت</th><th>کمپین</th></tr>{rows}</table>
<div class="sub" style="margin-top:24px">صفحات: <a href="/admin/review">صف بازبینی</a> · <a href="/admin/pilot">حاکمیت</a> · <a href="/admin/send">ارسال</a></div>
</div>"""
    return HTMLResponse(f'<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">'
                        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
                        f'<title>A2 — نمای کلی</title><style>{STYLE}</style></head><body>{body}</body></html>')


@router.get("/email/{draft_id}", response_class=HTMLResponse)
def email_detail(draft_id: int) -> HTMLResponse:
    session = make_session_factory(get_settings())()
    try:
        draft = session.get(EmailDraftVariant, draft_id)
        if draft is None:
            return HTMLResponse("<p dir=rtl>یافت نشد</p>", status_code=404)
        candidate = session.get(CandidateBusiness, draft.candidate_business_id)
        contact = session.scalar(
            select(CandidateContactVerification)
            .where(CandidateContactVerification.candidate_business_id == draft.candidate_business_id)
            .order_by(CandidateContactVerification.id.desc())
        )
        recipient = contact.best_email if contact else None
        allowed = bool(contact and contact.outreach_contact_allowed)
    finally:
        session.close()
    country = candidate.country if candidate else None
    ev = CountryComplianceService().evaluate(country)
    lane = "بهبودِ سایتِ موجود" if draft.campaign_lane == "IMPROVEMENT" else "ساختِ سایتِ جدید"
    legal = "مجاز (ارسال با لینکِ لغو)" if ev["allowed"] else "مسدود (کشور رضایتِ قبلی می‌خواهد)"
    rec = _esc(recipient) + (" — مجاز ✅" if allowed else " — بدون تماسِ امن ⛔") if recipient else "بدون تماسِ امن ⛔"
    meta = (f"<div class='meta'><span><b>کسب‌وکار:</b> {_esc(candidate.display_name) if candidate else '?'}</span>"
            f"<span><b>شهر/کشور:</b> {_esc(candidate.city) if candidate else ''} / {_esc(country)}</span>"
            f"<span><b>گیرنده:</b> {rec}</span><span><b>کمپین:</b> <span class='pill'>{lane}</span></span>"
            f"<span><b>وضعیت:</b> {_esc(getattr(draft.status,'value',draft.status))}</span>"
            f"<span><b>قانونِ کشور:</b> {legal}</span></div>")
    body_txt = draft.body_text.replace("{{unsubscribe_url}}",
        "[هنگام ارسال، اینجا روشِ لغو می‌آید: «برای لغو، با کلمهٔ UNSUBSCRIBE پاسخ دهید»]")
    page = (f"<div class='wrap'><h1>متنِ ایمیل</h1>{meta}"
            f"<h2>موضوع</h2><div class='email'>{_esc(draft.subject_text)}</div>"
            f"<h2>متن</h2><div class='email'>{_esc(body_txt)}</div>"
            f"<div class='sub' style='margin-top:20px'><a href='/admin/overview'>بازگشت به نمای کلی</a></div></div>")
    return HTMLResponse(f'<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">'
                        f'<title>متن ایمیل</title><style>{STYLE}</style></head><body>{page}</body></html>')
