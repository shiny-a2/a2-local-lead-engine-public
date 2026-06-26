from app.core.enums import CampaignStatus, LeadStatus, SourceName
from app.db.base import Base
from app.db.models import Campaign, Lead


def test_models_import():
    assert Campaign.__tablename__ == "campaigns"
    assert Lead.__tablename__ == "leads"


def test_metadata_contains_expected_tables():
    expected = {
        "campaigns",
        "leads",
        "lead_sources",
        "lead_contacts",
        "lead_web_presence",
        "lead_scores",
        "email_drafts",
        "email_judgements",
        "email_sends",
        "suppression_list",
        "audit_logs",
        "source_runs",
        "source_requests",
        "raw_source_records",
        "source_cache",
        "source_rate_limits",
        "nzbn_entity_matches",
        "raw_personalization_evidence",
        "candidate_businesses",
        "candidate_source_links",
        "candidate_aliases",
        "normalized_locations",
        "candidate_categories",
        "candidate_quality_reports",
        "candidate_personalization_evidence",
        "normalization_runs",
        "duplicate_clusters",
        "candidate_manual_review_items",
        "candidate_conflicts",
        "verification_runs",
        "search_queries",
        "search_results",
        "url_probe_results",
        "candidate_web_presence_verifications",
        "contact_candidates",
        "candidate_contact_verifications",
        "phase4_candidate_decisions",
        "verified_personalization_evidence",
        "phase4_manual_review_items",
        "claim_permissions",
    }
    assert expected.issubset(Base.metadata.tables)


def test_enum_values_exist():
    assert CampaignStatus.DRAFT.value == "DRAFT"
    assert LeadStatus.SUPPRESSED.value == "SUPPRESSED"
    assert SourceName.FIXTURE.value == "fixture"
