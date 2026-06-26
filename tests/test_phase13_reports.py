from app.services.phase13_report_service import Phase13ReportService
from app.services.sales_workspace_service import SalesWorkspaceService
from app.settings import Settings
from tests.phase12_helpers import build_opportunity_from_body


def test_phase13_reports_generated(session, tmp_path):
    campaign, _, _, _ = build_opportunity_from_body(session, "yes interested")
    SalesWorkspaceService(session, Settings(testing=True)).build_for_campaign(campaign.slug, True)
    paths = Phase13ReportService(session).write(tmp_path)
    assert paths[0].exists()
    assert paths[1].exists()
    assert paths[2].exists()
    assert paths[3].exists()
    assert paths[4].exists()
    assert paths[5].exists()
    text = paths[0].read_text(encoding="utf-8")
    assert "Phase 13 does not send replies." in text
    assert "workspace_items_count" in text
