from sqlalchemy import select

from app.core.enums import LeadStatus, SourceName
from app.db.models.lead import Lead
from app.services.fixture_service import seed_fixture_leads


def test_fixture_seed_creates_only_fake_sample_leads(session, test_settings):
    created, skipped = seed_fixture_leads(session, test_settings, "run-fixture")
    assert created == 3
    assert skipped == 0
    leads = session.scalars(select(Lead)).all()
    assert all(
        lead.business_name.startswith(("Example", "Sample", "Demo"))
        for lead in leads
    )


def test_fixture_source_is_fixture_and_not_send_ready(session, test_settings):
    seed_fixture_leads(session, test_settings, "run-fixture")
    leads = session.scalars(select(Lead)).all()
    assert all(lead.status == LeadStatus.RAW for lead in leads)
    assert all(lead.sources[0].source_name == SourceName.FIXTURE for lead in leads)
