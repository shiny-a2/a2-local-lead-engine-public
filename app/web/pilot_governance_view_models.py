STATUS_FA = {
    "MVP_CLOSED_READY": "MVP آماده بسته‌شدن",
    "MVP_CLOSED_WITH_FIX_PACKS": "MVP با Fix Packها قابل ادامه است",
    "MVP_NOT_CLOSED_BLOCKED": "MVP مسدود است",
    "MVP_INCONCLUSIVE_NEEDS_MORE_DATA": "داده کافی نیست",
    "PILOT_INCONCLUSIVE": "پایلوت نامشخص",
    "NEEDS_FIX_PACK_BEFORE_SCALE": "قبل از توسعه نیازمند Fix Pack",
}


def status_fa(value: str) -> str:
    return STATUS_FA.get(value, value)
