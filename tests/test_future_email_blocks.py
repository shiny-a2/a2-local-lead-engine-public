from app.core.enums import OfferPackage
from app.db.models.candidate_offer_match import CandidateOfferMatch
from app.services.economic_value_angle_service import EconomicValueAngleService
from app.services.future_email_block_service import FutureEmailBlockService


def test_blocks_are_fragments_not_full_email():
    offer = CandidateOfferMatch(
        candidate_business_id=1,
        insight_run_id=1,
        playbook_id=1,
        offer_package=OfferPackage.LOCAL_TRUST_SITE,
        offer_fit_score=90,
        offer_confidence=0.8,
        offer_summary="summary",
        internal_offer_analysis="analysis",
        email_safe_offer_summary="A lightweight owned web presence focused on clearer customer action.",
        primary_value_angle="direct action",
        secondary_value_angles_json=[],
        selected_module_ids_json=[],
        excluded_module_ids_json=[],
    )
    angles, _ = EconomicValueAngleService().build(1, 1, OfferPackage.LOCAL_TRUST_SITE)
    blocks = FutureEmailBlockService().build(1, 1, offer, angles)
    text = "\n".join(block.block_text.lower() for block in blocks)
    assert "subject:" not in text
    assert not text.startswith("hi ")
    assert "regards" not in text
    assert all(block.supporting_evidence_json for block in blocks)
