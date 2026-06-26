from app.core.enums import RawRecordType, SourceName, SourceOperation
from app.db.models.raw_personalization_evidence import RawPersonalizationEvidence
from app.services.raw_record_service import RawRecordService
from app.services.source_run_service import SourceRunService


def make_source_run(session):
    return SourceRunService(session).start(
        source_name=SourceName.GEOAPIFY,
        operation=SourceOperation.COLLECT_PLACES,
        dry_run=False,
    )


def make_raw_record(
    session,
    *,
    name="Example Auckland Barber Studio",
    category="commercial.hairdresser",
    city="Auckland",
    suburb="Ponsonby",
    lat=-36.85,
    lng=174.74,
    phone=None,
    website=None,
    email=None,
):
    run = make_source_run(session)
    rows, _ = RawRecordService(session).store_records(
        run,
        [
            {
                "source_name": SourceName.GEOAPIFY,
                "source_external_id": f"{name}:{category}:{lat}:{lng}",
                "record_type": RawRecordType.PLACE,
                "raw_name": name,
                "raw_category": category,
                "raw_city": city,
                "raw_suburb": suburb,
                "raw_country": "New Zealand",
                "raw_lat": lat,
                "raw_lng": lng,
                "raw_phone": phone,
                "raw_website": website,
                "raw_email": email,
                "raw_payload_json": {"name": name},
            }
        ],
    )
    raw = rows[0]
    for evidence_type, value in [
        ("business_name", name),
        ("category_hint", category),
        ("suburb_hint", suburb),
        ("website_field_missing", "missing_in_raw_source"),
        ("email_present_raw", email),
        ("phone_present", phone),
    ]:
        if value:
            session.add(
                RawPersonalizationEvidence(
                    raw_source_record_id=raw.id,
                    source_run_id=run.id,
                    evidence_type=evidence_type,
                    evidence_value=value,
                    evidence_source="fixture",
                    confidence=0.7,
                    allowed_for_future_copy=evidence_type
                    in {"business_name", "category_hint", "suburb_hint"},
                    requires_verification=True,
                    risk_flag="not_outreach_permission"
                    if evidence_type in {"email_present_raw", "phone_present"}
                    else None,
                )
            )
    session.commit()
    return raw, run
