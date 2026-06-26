from dataclasses import dataclass

from app.core.enums import SensitiveOperation
from app.settings import Settings


@dataclass(frozen=True)
class FlagRequirement:
    operation: SensitiveOperation
    flag_name: str
    reason: str


FLAG_REQUIREMENTS: dict[SensitiveOperation, FlagRequirement] = {
    SensitiveOperation.LIVE_API_CALL: FlagRequirement(
        SensitiveOperation.LIVE_API_CALL, "LIVE_API_CALLS_ENABLED", "LIVE_API_CALLS_DISABLED"
    ),
    SensitiveOperation.LEAD_COLLECTION: FlagRequirement(
        SensitiveOperation.LEAD_COLLECTION, "LEAD_COLLECTION_ENABLED", "LEAD_COLLECTION_DISABLED"
    ),
    SensitiveOperation.AI_GENERATION: FlagRequirement(
        SensitiveOperation.AI_GENERATION, "AI_GENERATION_ENABLED", "AI_GENERATION_DISABLED"
    ),
    SensitiveOperation.EMAIL_DRAFTING: FlagRequirement(
        SensitiveOperation.EMAIL_DRAFTING, "EMAIL_DRAFTING_ENABLED", "EMAIL_DRAFTING_DISABLED"
    ),
    SensitiveOperation.EMAIL_SENDING: FlagRequirement(
        SensitiveOperation.EMAIL_SENDING, "EMAIL_SENDING_ENABLED", "EMAIL_SENDING_DISABLED"
    ),
    SensitiveOperation.FOLLOWUP_SENDING: FlagRequirement(
        SensitiveOperation.FOLLOWUP_SENDING, "FOLLOWUP_ENABLED", "FOLLOWUP_DISABLED"
    ),
    SensitiveOperation.VOICE_CALL: FlagRequirement(
        SensitiveOperation.VOICE_CALL, "VOICE_CALLS_ENABLED", "VOICE_CALLS_DISABLED"
    ),
    SensitiveOperation.GOOGLE_MAPS_USAGE: FlagRequirement(
        SensitiveOperation.GOOGLE_MAPS_USAGE,
        "GOOGLE_MAPS_ENABLED",
        "GOOGLE_MAPS_PROHIBITED_FOR_MVP",
    ),
    SensitiveOperation.PUBLIC_DASHBOARD: FlagRequirement(
        SensitiveOperation.PUBLIC_DASHBOARD, "PUBLIC_DASHBOARD_ENABLED", "PUBLIC_DASHBOARD_DISABLED"
    ),
}


def get_flag_value(settings: Settings, flag_name: str) -> bool:
    return bool(getattr(settings, flag_name.lower()))
