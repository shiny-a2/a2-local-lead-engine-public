from sqlalchemy.orm import Session

from app.db.models.raw_personalization_evidence import RawPersonalizationEvidence
from app.db.models.raw_source_record import RawSourceRecord


class PersonalizationEvidenceService:
    def __init__(self, session: Session):
        self.session = session

    def create_for_record(
        self, raw_record: RawSourceRecord, evidence_items: list[dict]
    ) -> list[RawPersonalizationEvidence]:
        rows = [
            RawPersonalizationEvidence(
                raw_source_record_id=raw_record.id,
                source_run_id=raw_record.source_run_id,
                **item,
            )
            for item in evidence_items
        ]
        self.session.add_all(rows)
        self.session.commit()
        return rows
