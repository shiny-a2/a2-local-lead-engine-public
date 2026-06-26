from app.core.enums import ContactStatus, Phase4Decision, Phase4WebsiteStatus
from app.services.web_presence_decision_service import WebPresenceDecisionService


def test_ready_for_phase5_when_verification_adequate():
    row = WebPresenceDecisionService().decide(Phase4WebsiteStatus.NO_WEBSITE_PROBABLE, ContactStatus.NO_CONTACT_FOUND)
    assert row["decision"] == Phase4Decision.READY_FOR_PHASE_5_SCORING


def test_manual_review_for_unclear_ownership():
    row = WebPresenceDecisionService().decide(Phase4WebsiteStatus.INSUFFICIENT_EVIDENCE, ContactStatus.NO_CONTACT_FOUND)
    assert row["manual_review_required"] is True


def test_reject_strong_website():
    row = WebPresenceDecisionService().decide(Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL, ContactStatus.NO_CONTACT_FOUND)
    assert row["decision"] == Phase4Decision.REJECT_WEBSITE_ALREADY_STRONG


def test_reject_compliance_risk():
    row = WebPresenceDecisionService().decide(Phase4WebsiteStatus.NO_WEBSITE_PROBABLE, ContactStatus.PERSONAL_EMAIL_FOUND_BLOCKED)
    assert row["decision"] == Phase4Decision.REJECT_COMPLIANCE_RISK
