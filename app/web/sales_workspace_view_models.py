from dataclasses import dataclass


@dataclass(frozen=True)
class SalesWorkspaceBadge:
    label_fa: str
    css_class: str = "badge"


STATUS_LABELS_FA = {
    "NEEDS_MANUAL_REPLY": "نیازمند پاسخ دستی",
    "WAITING_FOR_SCOPE": "نیازمند دریافت Scope",
    "QUOTE_PREPARATION": "آماده‌سازی قیمت دستی",
    "PROPOSAL_CHECKLIST_READY": "چک‌لیست Proposal",
    "MANUAL_CALL_NEEDED": "تماس دستی لازم است",
    "FOLLOWUP_MANUAL_ELIGIBLE": "پیگیری دستی مجاز",
    "CLOSED_LOST": "بسته‌شده",
    "CLOSED_WON": "برنده‌شده",
}


def status_label(value: str) -> str:
    return STATUS_LABELS_FA.get(value, value)
