from app.core.enums import Phase4WebsiteStatus
from app.services.claim_permission_service import ClaimPermissionService
from tests.test_candidate_quality import _candidate


def test_conservative_no_website_claim_allowed_only_with_evidence(session):
    rows = ClaimPermissionService().permissions_for_status(
        _candidate(session), Phase4WebsiteStatus.NO_WEBSITE_PROBABLE, 75
    )
    assert any(row["claim_type"] == "can_say_could_not_find_dedicated_website" and row["allowed"] for row in rows)


def test_absolute_no_website_claim_blocked(session):
    rows = ClaimPermissionService().permissions_for_status(_candidate(session), Phase4WebsiteStatus.NO_WEBSITE_PROBABLE, 75)
    assert any("You don't have a website." in row.get("blocked_phrasing_json", []) for row in rows)


def test_google_maps_reference_blocked(session):
    rows = ClaimPermissionService().permissions_for_status(_candidate(session), Phase4WebsiteStatus.SOCIAL_ONLY, 80)
    assert any(row["claim_type"] == "blocked_google_maps_reference" for row in rows)


def test_competitor_loss_pressure_claims_blocked(session):
    rows = ClaimPermissionService().permissions_for_status(_candidate(session), Phase4WebsiteStatus.SOCIAL_ONLY, 80)
    assert any("You are losing customers." in row.get("blocked_phrasing_json", []) for row in rows)


def test_social_only_phrasing_allowed_when_verified(session):
    rows = ClaimPermissionService().permissions_for_status(_candidate(session), Phase4WebsiteStatus.SOCIAL_ONLY, 80)
    assert any(row["claim_type"] == "can_say_social_or_directory_presence" and row["allowed"] for row in rows)

