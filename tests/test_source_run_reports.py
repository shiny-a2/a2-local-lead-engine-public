from app.connectors.geoapify import GeoapifyPlacesConnector
from app.core.enums import RawRecordType, SourceName, SourceOperation, SourceRunStatus
from app.services.personalization_evidence_service import PersonalizationEvidenceService
from app.services.raw_record_service import RawRecordService
from app.services.source_quality_service import SourceQualityService, write_source_report
from app.services.source_run_service import SourceRunService


def test_source_run_report_files_generated(session, test_settings, tmp_path):
    run_service = SourceRunService(session)
    source_run = run_service.start(
        source_name=SourceName.GEOAPIFY,
        operation=SourceOperation.COLLECT_PLACES,
        dry_run=False,
    )
    records, _ = RawRecordService(session).store_records(
        source_run,
        [
            {
                "source_name": SourceName.GEOAPIFY,
                "source_external_id": "p1",
                "record_type": RawRecordType.PLACE,
                "raw_name": "Example Auckland Barber Studio",
                "raw_category": "barber",
                "raw_city": "Auckland",
                "raw_payload_json": {"id": "p1"},
            }
        ],
    )
    evidence = GeoapifyPlacesConnector(test_settings).extract_personalization_evidence(
        {"raw_name": "Example Auckland Barber Studio", "raw_category": "barber"}
    )
    PersonalizationEvidenceService(session).create_for_record(records[0], evidence)
    run_service.finish(source_run, SourceRunStatus.COMPLETED, fetched=1, stored=1)
    summary = SourceQualityService(session).build_source_run_summary(source_run)
    md_path, json_path = write_source_report(summary, tmp_path, "source-run")
    text = md_path.read_text(encoding="utf-8")
    assert md_path.exists()
    assert json_path.exists()
    assert "does not authorize outreach" in text
    assert "does not generate email content" in text
    assert "does not confirm that a business has no website" in text
    assert summary["evidence_types_breakdown"]["business_name"] == 1
