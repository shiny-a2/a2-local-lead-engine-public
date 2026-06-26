from app.core.enums import RawRecordType, SourceName, SourceOperation
from app.services.raw_record_service import RawRecordService
from app.services.source_run_service import SourceRunService


def _source_run(session):
    return SourceRunService(session).start(
        source_name=SourceName.GEOAPIFY,
        operation=SourceOperation.COLLECT_PLACES,
        dry_run=False,
    )


def _record():
    return {
        "source_name": SourceName.GEOAPIFY,
        "source_external_id": "p1",
        "record_type": RawRecordType.PLACE,
        "raw_name": "Example Auckland Barber Studio",
        "raw_category": "commercial.hairdresser",
        "raw_city": "Auckland",
        "raw_payload_json": {"id": "p1"},
    }


def test_raw_record_is_stored(session):
    rows, skipped = RawRecordService(session).store_records(_source_run(session), [_record()])
    assert rows[0].raw_name == "Example Auckland Barber Studio"
    assert skipped == 0


def test_duplicate_fingerprint_updates_last_seen(session):
    service = RawRecordService(session)
    run = _source_run(session)
    service.store_records(run, [_record()])
    rows, skipped = service.store_records(run, [_record()])
    assert skipped == 1
    assert len(rows) == 1


def test_raw_website_missing_does_not_become_no_website_claim(session):
    row = RawRecordService(session).store_records(_source_run(session), [_record()])[0][0]
    assert row.raw_website is None
    assert "NO_WEBSITE" not in str(row.raw_payload_json)


def test_raw_email_present_does_not_set_outreach_permission(session):
    record = _record()
    record["raw_email"] = "raw@example.test"
    row = RawRecordService(session).store_records(_source_run(session), [record])[0][0]
    assert row.raw_email == "raw@example.test"
    assert not hasattr(row, "is_allowed_for_outreach")

