from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SourceName, SourceOperation, SourceRunStatus
from app.core.run_context import new_run_id
from app.db.models.campaign import Campaign
from app.db.models.source_run import SourceRun


class SourceRunService:
    def __init__(self, session: Session):
        self.session = session

    def campaign_id_for_slug(self, slug: str | None) -> int | None:
        if not slug:
            return None
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == slug))
        return campaign.id if campaign else None

    def start(
        self,
        *,
        source_name: SourceName,
        operation: SourceOperation,
        dry_run: bool,
        campaign_slug: str | None = None,
        category: str | None = None,
        city: str | None = None,
        country: str | None = None,
        requested_limit: int | None = None,
        metadata: dict | None = None,
    ) -> SourceRun:
        source_run = SourceRun(
            run_id=new_run_id(),
            campaign_id=self.campaign_id_for_slug(campaign_slug),
            source_name=source_name,
            operation=operation,
            dry_run=dry_run,
            category=category,
            city=city,
            country=country,
            requested_limit=requested_limit,
            metadata_json=metadata,
        )
        self.session.add(source_run)
        self.session.commit()
        self.session.refresh(source_run)
        return source_run

    def finish(
        self,
        source_run: SourceRun,
        status: SourceRunStatus,
        *,
        fetched: int = 0,
        stored: int = 0,
        skipped: int = 0,
        errors: int = 0,
    ) -> SourceRun:
        source_run.status = status
        source_run.fetched_count = fetched
        source_run.stored_count = stored
        source_run.skipped_count = skipped
        source_run.error_count = errors
        source_run.finished_at = datetime.now(UTC)
        self.session.commit()
        self.session.refresh(source_run)
        return source_run
