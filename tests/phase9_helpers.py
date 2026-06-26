from app.core.enums import ContactStatus, EmailType
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService
from app.services.human_review_queue_service import HumanReviewQueueService
from app.settings import Settings
from tests.phase8_helpers import make_judge_pending_draft


def make_phase9_queue_item(session, sender: bool = True, contact: bool = True):
    campaign, generation_run, draft = make_judge_pending_draft(session)
    judge_run = EmailJudgeOrchestratorService(session, Settings()).judge_emails(campaign.slug, generation_run.run_id, commit=True)
    review_run = HumanReviewQueueService(session, Settings()).build_queue(campaign.slug, judge_run.run_id, commit=True)
    item = session.query(HumanReviewQueueItem).first()
    if contact:
        session.add(
            CandidateContactVerification(
                candidate_business_id=draft.candidate_business_id,
                verification_run_id=1,
                best_email="hello@example.com",
                best_email_type=EmailType.GENERIC_BUSINESS,
                best_email_confidence=0.9,
                contact_status=ContactStatus.GENERIC_BUSINESS_EMAIL_FOUND,
                outreach_contact_allowed=True,
                manual_review_required=False,
                decision_reason="Fixture safe contact.",
                evidence_json={},
            )
        )
    settings = Settings(default_from_email="hello@amiraliyaghouti.com", default_reply_to_email="hello@amiraliyaghouti.com") if sender else Settings()
    session.commit()
    return campaign, judge_run, review_run, item, settings


def approved_judge_decision(session) -> EmailJudgeDecision:
    return session.query(EmailJudgeDecision).first()
