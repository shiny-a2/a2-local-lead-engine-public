from sqlalchemy.orm import Session

from app.db.models.retention_policy_record import RetentionPolicyRecord
from app.settings import Settings


class RetentionPolicyService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create(self, audit_run_id: int | None = None) -> list[RetentionPolicyRecord]:
        rows = [
            RetentionPolicyRecord(pilot_audit_run_id=audit_run_id, policy_name="operational_data", retention_days=self.settings.data_retention_days, policy_status="ACTIVE", notes_json={"manual_review_required": True}),
            RetentionPolicyRecord(pilot_audit_run_id=audit_run_id, policy_name="audit_logs", retention_days=self.settings.audit_retention_days, policy_status="ACTIVE", notes_json={"secrets_redacted": True}),
            RetentionPolicyRecord(pilot_audit_run_id=audit_run_id, policy_name="exports", retention_days=30, policy_status="REVIEW_REQUIRED", notes_json={"exclude_env_files": True}),
        ]
        self.session.add_all(rows)
        self.session.flush()
        return rows
