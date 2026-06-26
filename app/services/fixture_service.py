from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import Actor, LeadStatus, SourceName
from app.core.fingerprints import stable_fingerprint
from app.db.models.lead import Lead
from app.db.models.lead_source import LeadSource
from app.services.audit_service import AuditService
from app.settings import Settings

FIXTURE_LEADS = [
    ("Example Auckland Barber Studio", "barber"),
    ("Sample Beauty Lounge Auckland", "beauty_salon"),
    ("Demo Cleaning Services NZ", "cleaning_service"),
]


def seed_fixture_leads(
    session: Session, settings: Settings, run_id: str | None = None
) -> tuple[int, int]:
    created = 0
    skipped = 0
    for name, category in FIXTURE_LEADS:
        normalized = name.lower()
        existing = session.scalar(select(Lead).where(Lead.normalized_name == normalized))
        if existing:
            skipped += 1
            continue
        lead = Lead(
            business_name=name,
            normalized_name=normalized,
            category=category,
            city="Auckland",
            country="New Zealand",
            status=LeadStatus.RAW,
            source_confidence=0.1,
        )
        payload = {"fixture": True, "business_name": name, "send_ready": False}
        lead.sources.append(
            LeadSource(
                source_name=SourceName.FIXTURE,
                raw_payload_json=payload,
                fingerprint=stable_fingerprint(payload),
            )
        )
        session.add(lead)
        created += 1
    session.commit()
    AuditService(session, settings).record(
        entity_type="fixture",
        action="seed_fixture_leads",
        actor=Actor.CLI,
        run_id=run_id,
        metadata={"created": created, "skipped": skipped, "source": SourceName.FIXTURE.value},
    )
    return created, skipped
