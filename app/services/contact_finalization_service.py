from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.candidate_contact_verification import CandidateContactVerification


class ContactFinalizationService:
    def __init__(self, session: Session):
        self.session = session

    def final_email(self, candidate_id: int) -> tuple[str | None, bool, list[str]]:
        row = self.session.scalar(
            select(CandidateContactVerification)
            .where(CandidateContactVerification.candidate_business_id == candidate_id)
            .order_by(CandidateContactVerification.id.desc())
        )
        if row is None:
            return None, False, ["contact_not_found"]
        if not row.outreach_contact_allowed or not row.best_email or row.manual_review_required:
            return row.best_email, False, ["contact_not_safe_for_phase10_queue"]
        return row.best_email, True, []
