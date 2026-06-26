import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.enums import SensitiveOperation
from app.core.run_context import RunContext
from app.core.safety import check_all_operations
from app.db.models.campaign import Campaign
from app.settings import Settings

FINAL_VERDICT = "FOUNDATION_READY_FOR_PHASE_2_CONNECTORS"


def database_status(session: Session) -> str:
    try:
        session.execute(text("select 1"))
        return "ok"
    except Exception as exc:  # pragma: no cover - defensive CLI reporting
        return f"error: {exc.__class__.__name__}"


def campaign_seed_status(session: Session) -> str:
    exists = session.scalar(select(Campaign).where(Campaign.slug == "auckland-local-website-pilot"))
    return "present" if exists else "missing"


def build_foundation_report(
    settings: Settings, session: Session, context: RunContext
) -> dict[str, Any]:
    safety = [check.model_dump() for check in check_all_operations(settings)]
    blocked = {item["operation"]: not item["allowed"] for item in safety}
    known_gaps = [
        "Live source connectors are future Phase 2 work.",
        "AI drafting, judging, and email sending are future phases.",
        "PostgreSQL must be configured by the operator for non-test local use.",
    ]
    return {
        "run_id": context.run_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "database_status": database_status(session),
        "campaign_seed_status": campaign_seed_status(session),
        "audit_log_status": "enabled" if settings.audit_log_enabled else "disabled",
        "safety_flag_status": safety,
        "external_api_status": "disabled/not-called",
        "email_sending": "disabled",
        "voice_calls": "disabled",
        "google_maps": "disabled/prohibited for MVP",
        "known_gaps": known_gaps,
        "final_verdict": FINAL_VERDICT
        if all(
            blocked[operation.value]
            for operation in [
                SensitiveOperation.LIVE_API_CALL,
                SensitiveOperation.LEAD_COLLECTION,
                SensitiveOperation.AI_GENERATION,
                SensitiveOperation.EMAIL_SENDING,
                SensitiveOperation.VOICE_CALL,
                SensitiveOperation.GOOGLE_MAPS_USAGE,
                SensitiveOperation.PUBLIC_DASHBOARD,
            ]
        )
        else "FOUNDATION_BLOCKED",
    }


def write_foundation_report(report: dict[str, Any], reports_dir: Path) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    md_path = reports_dir / f"foundation-readiness-{stamp}.md"
    json_path = reports_dir / f"foundation-readiness-{stamp}.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Foundation Readiness Report",
        "",
        f"- run_id: `{report['run_id']}`",
        f"- database_status: `{report['database_status']}`",
        f"- campaign_seed_status: `{report['campaign_seed_status']}`",
        f"- audit_log_status: `{report['audit_log_status']}`",
        f"- external_api_status: `{report['external_api_status']}`",
        f"- email_sending: `{report['email_sending']}`",
        f"- voice_calls: `{report['voice_calls']}`",
        f"- google_maps: `{report['google_maps']}`",
        "",
        "## Safety Flags",
    ]
    lines.extend(
        f"- {item['operation']}: {'ALLOWED' if item['allowed'] else 'BLOCKED'} ({item['reason']})"
        for item in report["safety_flag_status"]
    )
    lines.extend(["", "## Known Gaps"])
    lines.extend(f"- {gap}" for gap in report["known_gaps"])
    lines.extend(["", f"Final verdict: `{report['final_verdict']}`", ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path
