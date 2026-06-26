from app.core.enums import NormalizationOperation
from app.services.candidate_builder_service import CandidateBuilderService
from app.services.candidate_report_service import CandidateReportService
from tests.phase3_helpers import make_raw_record


def test_candidate_report_generated(session, tmp_path):
    raw, _ = make_raw_record(session)
    builder = CandidateBuilderService(session)
    run = builder.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    builder.build_from_raw([raw], run, commit=True)
    md_path, json_path, report = CandidateReportService(session).write_candidate_report(tmp_path)
    text = md_path.read_text(encoding="utf-8")
    assert md_path.exists()
    assert json_path.exists()
    assert "does not verify website absence" in text
    assert report["final_verdict"] in {
        "PHASE_3_CANDIDATE_NORMALIZATION_READY",
        "PHASE_3_READY_WITH_MANUAL_REVIEW_GAPS",
    }


def test_manual_review_report_generated(session, tmp_path):
    md_path, csv_path = CandidateReportService(session).write_manual_review_report(tmp_path)
    assert md_path.exists()
    assert csv_path.exists()
    assert "does not verify website absence" in md_path.read_text(encoding="utf-8")

