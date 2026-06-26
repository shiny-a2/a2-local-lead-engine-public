import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.blocked_offer_claim import BlockedOfferClaim
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_offer_match import CandidateOfferMatch
from app.db.models.email_generation_input import EmailGenerationInput
from app.db.models.future_email_offer_block import FutureEmailOfferBlock
from app.db.models.phase6_candidate_decision import Phase6CandidateDecision
from app.services.prompt_injection_guard_service import PromptInjectionGuardService
from app.settings import Settings


class EmailInputAssemblerService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def assemble(self, run_id: int, candidate: CandidateBusiness, phase6: Phase6CandidateDecision) -> EmailGenerationInput:
        offer = self.session.scalar(select(CandidateOfferMatch).where(CandidateOfferMatch.candidate_business_id == candidate.id).order_by(CandidateOfferMatch.id.desc()))
        blocks = self.session.scalars(select(FutureEmailOfferBlock).where(FutureEmailOfferBlock.candidate_business_id == candidate.id, FutureEmailOfferBlock.allowed_for_phase7.is_(True))).all()
        blocked = self.session.scalars(select(BlockedOfferClaim).where(BlockedOfferClaim.candidate_business_id == candidate.id)).all()
        snapshot: dict[str, object] = {
            "business_name": candidate.display_name,
            "category": candidate.canonical_category,
            "local_context": candidate.suburb or candidate.city,
            "campaign_lane": offer.offer_package.value if offer else "UNKNOWN",
            "offer_summary": offer.email_safe_offer_summary if offer else "",
            "unsubscribe_placeholder": self.settings.email_unsubscribe_placeholder,
        }
        clean_snapshot, flags = PromptInjectionGuardService().sanitize_mapping(snapshot)
        offer_blocks = [{"id": row.id, "text": row.block_text, "type": row.block_type.value} for row in blocks]
        allowed_claims = [row["text"] for row in offer_blocks]
        blocked_claims = [row.claim_text for row in blocked]
        payload = {
            "input_snapshot": clean_snapshot,
            "offer_blocks": offer_blocks,
            "allowed_claims": allowed_claims,
            "blocked_claims": blocked_claims,
            "risk_flags": flags,
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return EmailGenerationInput(
            email_generation_run_id=run_id,
            candidate_business_id=candidate.id,
            phase6_decision_id=phase6.id,
            input_snapshot_json=clean_snapshot,
            input_snapshot_hash=digest,
            allowed_claims_json=allowed_claims,
            blocked_claims_json=blocked_claims,
            offer_blocks_json=offer_blocks,
            verified_evidence_json=[
                {"type": "business_name", "value": candidate.display_name},
                {"type": "local_context", "value": candidate.suburb or candidate.city},
            ],
            style_constraints_json={
                "min_words": self.settings.email_min_words,
                "max_words": self.settings.email_max_words,
                "no_send": True,
            },
            cta_options_json=["quick_idea", "simple_starter_page_idea", "booking_flow_idea", "quote_flow_idea"],
        )
