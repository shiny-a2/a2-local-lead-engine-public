from app.db.models.scoring_profile_snapshot import ScoringProfileSnapshot
from app.services.lead_scoring_service import LeadScoringService
from app.services.phase5_report_service import Phase5ReportService
from app.services.scoring_profile_service import SCORE_VERSION, SCORING_PROFILE
from tests.phase5_helpers import make_phase5_candidate


def test_scoring_profile_snapshot_stored(session):
    campaign, _ = make_phase5_candidate(session)
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    snapshot = session.query(ScoringProfileSnapshot).filter_by(scoring_run_id=run.id).one()
    assert snapshot.scoring_profile == SCORING_PROFILE
    assert snapshot.score_version == SCORE_VERSION


def test_report_includes_score_version_and_profile(session):
    campaign, _ = make_phase5_candidate(session)
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    report = Phase5ReportService(session).build(run)
    assert report["score_version"] == SCORE_VERSION
    assert report["scoring_profile"] == SCORING_PROFILE
