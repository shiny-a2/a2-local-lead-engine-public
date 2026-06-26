from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.fingerprints import stable_fingerprint
from app.db.models.raw_source_record import RawSourceRecord
from app.db.models.source_run import SourceRun


class RawRecordService:
    def __init__(self, session: Session):
        self.session = session

    def store_records(
        self, source_run: SourceRun, records: list[dict]
    ) -> tuple[list[RawSourceRecord], int]:
        stored: list[RawSourceRecord] = []
        skipped = 0
        for record in records:
            fingerprint = record.get("fingerprint") or stable_fingerprint(
                {
                    "source": record["source_name"].value,
                    "external_id": record.get("source_external_id"),
                    "name": record.get("raw_name"),
                    "lat": record.get("raw_lat"),
                    "lng": record.get("raw_lng"),
                }
            )
            record_hash = stable_fingerprint(record.get("raw_payload_json", record))
            existing = self.session.scalar(
                select(RawSourceRecord).where(RawSourceRecord.fingerprint == fingerprint)
            )
            now = datetime.now(UTC)
            if existing:
                existing.last_seen_at = now
                existing.source_run_id = source_run.id
                existing.record_hash = record_hash
                skipped += 1
                stored.append(existing)
                continue
            raw = RawSourceRecord(
                source_run_id=source_run.id,
                fingerprint=fingerprint,
                record_hash=record_hash,
                **record,
            )
            self.session.add(raw)
            stored.append(raw)
        self.session.commit()
        for item in stored:
            self.session.refresh(item)
        return stored, skipped
