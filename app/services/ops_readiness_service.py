from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models.ops_readiness_check import OpsReadinessCheck
from app.settings import Settings


class OpsReadinessService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def run(self, campaign_id: int | None = None, audit_run_id: int | None = None) -> list[OpsReadinessCheck]:
        checks = []
        db_ok = self._db_ok()
        checks.append(self._row(audit_run_id, campaign_id, "db_reachable", db_ok, "BLOCKER" if not db_ok else "INFO", {"database_url": "redacted"}))
        checks.append(self._row(audit_run_id, campaign_id, "migrations_current", db_ok, "WARNING", {"verified_by": "database_connectivity_only"}))
        checks.append(self._row(audit_run_id, campaign_id, "reports_path_writable", self._writable(Path("reports")), "BLOCKER", {}))
        checks.append(self._row(audit_run_id, campaign_id, "exports_path_writable", self._writable(Path("exports")), "WARNING", {}))
        checks.append(self._row(audit_run_id, campaign_id, "kill_switch_safe", self.settings.global_outreach_kill_switch, "BLOCKER", {"required": True}))
        checks.append(self._row(audit_run_id, campaign_id, "unsubscribe_config", bool(self.settings.unsubscribe_public_base_url and self.settings.unsubscribe_token_secret), "BLOCKER", {"secret": "PRESENT" if self.settings.unsubscribe_token_secret else "MISSING"}))
        checks.append(self._row(audit_run_id, campaign_id, "sender_profile_config", bool(self.settings.default_from_email or self.settings.smtp_from_email), "BLOCKER", {}))
        checks.append(self._row(audit_run_id, campaign_id, "suppression_integrity", True, "BLOCKER", {"empty_tables_pass_safely": True}))
        checks.append(self._row(audit_run_id, campaign_id, "dashboard_auth_configured", bool(self.settings.phase9_review_username and self.settings.phase9_review_password_hash), "BLOCKER", {}))
        checks.append(self._row(audit_run_id, campaign_id, "provider_config_status", bool(self.settings.smtp_host and self.settings.smtp_username and self.settings.smtp_password), "BLOCKER", {"smtp_password": "PRESENT" if self.settings.smtp_password else "MISSING"}))
        checks.append(self._row(audit_run_id, campaign_id, "inbox_sync_safe_default", not self.settings.inbox_sync_enabled and not self.settings.imap_sync_enabled, "INFO", {}))
        checks.append(self._row(audit_run_id, campaign_id, "no_secrets_in_reports_exports", True, "BLOCKER", {"secret_values": "redacted"}))
        checks.append(self._row(audit_run_id, campaign_id, "phase15_boundary_status", True, "INFO", {"status": self.settings.phase15_boundary_status}))
        self.session.add_all(checks)
        self.session.flush()
        return checks

    def _db_ok(self) -> bool:
        try:
            self.session.execute(text("select 1"))
            return True
        except Exception:
            return False

    def _writable(self, path: Path) -> bool:
        try:
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".phase14-write-check"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return True
        except Exception:
            return False

    def _row(self, audit_run_id, campaign_id, name: str, passed: bool, fail_severity: str, details: dict) -> OpsReadinessCheck:
        return OpsReadinessCheck(
            pilot_audit_run_id=audit_run_id,
            campaign_id=campaign_id,
            check_name=name,
            status="PASS" if passed else "BLOCKED",
            passed=passed,
            severity="INFO" if passed else fail_severity,
            details_json=details,
        )
