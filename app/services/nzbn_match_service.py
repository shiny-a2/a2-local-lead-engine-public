from sqlalchemy.orm import Session

from app.db.models.nzbn_entity_match import NzbnEntityMatch
from app.db.models.raw_source_record import RawSourceRecord
from app.db.models.source_run import SourceRun


class NzbnMatchService:
    def __init__(self, session: Session):
        self.session = session

    def store_matches(
        self, source_run: SourceRun, raw_record: RawSourceRecord, matches: list[dict]
    ) -> list[NzbnEntityMatch]:
        rows = [
            NzbnEntityMatch(
                source_run_id=source_run.id,
                raw_source_record_id=raw_record.id,
                **match,
            )
            for match in matches
        ]
        self.session.add_all(rows)
        self.session.commit()
        return rows
