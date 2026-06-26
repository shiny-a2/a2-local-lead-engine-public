"""phase14 pilot governance

Revision ID: 20260525_0014
Revises: 20260525_0013
"""

from alembic import op
import sqlalchemy as sa


revision = "20260525_0014"
down_revision = "20260525_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pilot_audit_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(80), nullable=False, unique=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("operation", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("dry_run", sa.Boolean(), nullable=False),
        sa.Column("input_candidate_count", sa.Integer(), nullable=False),
        sa.Column("sent_to_provider_count", sa.Integer(), nullable=False),
        sa.Column("replies_count", sa.Integer(), nullable=False),
        sa.Column("opportunities_count", sa.Integer(), nullable=False),
        sa.Column("blockers_count", sa.Integer(), nullable=False),
        sa.Column("warnings_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "pilot_kpi_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("metric_name", sa.String(120), nullable=False),
        sa.Column("metric_value", sa.Integer(), nullable=False),
        sa.Column("metric_context_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "phase_readiness_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=False),
        sa.Column("phase_number", sa.Integer(), nullable=False),
        sa.Column("phase_name", sa.String(160), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("implemented", sa.Boolean(), nullable=False),
        sa.Column("blocker", sa.Boolean(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=True),
        sa.Column("notes", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "risk_register_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=False),
        sa.Column("risk_code", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(40), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("affected_phases_json", sa.JSON(), nullable=False),
        sa.Column("root_cause", sa.String(1000), nullable=False),
        sa.Column("mitigation", sa.String(1000), nullable=False),
        sa.Column("status", sa.String(60), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "scale_decision_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=False),
        sa.Column("decision", sa.String(80), nullable=False),
        sa.Column("ready_for_scale", sa.Boolean(), nullable=False),
        sa.Column("sample_size_ok", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.String(1000), nullable=False),
        sa.Column("limits_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "fix_pack_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=False),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("root_cause", sa.String(1000), nullable=False),
        sa.Column("affected_phases_json", sa.JSON(), nullable=False),
        sa.Column("risk_if_not_fixed", sa.String(1000), nullable=False),
        sa.Column("acceptance_criteria", sa.String(1000), nullable=False),
        sa.Column("codex_ready_summary", sa.String(1000), nullable=False),
        sa.Column("status", sa.String(60), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "ops_readiness_checks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("check_name", sa.String(120), nullable=False),
        sa.Column("status", sa.String(60), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("severity", sa.String(40), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "retention_policy_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=True),
        sa.Column("policy_name", sa.String(120), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("policy_status", sa.String(60), nullable=False),
        sa.Column("notes_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "backup_export_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=True),
        sa.Column("export_type", sa.String(80), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("status", sa.String(60), nullable=False),
        sa.Column("secrets_included", sa.Boolean(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "mvp_closure_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=False),
        sa.Column("decision", sa.String(80), nullable=False),
        sa.Column("ready_for_operator_setup", sa.Boolean(), nullable=False),
        sa.Column("ready_for_controlled_dry_run", sa.Boolean(), nullable=False),
        sa.Column("ready_for_live_pilot", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.String(1000), nullable=False),
        sa.Column("warnings_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "phase14_audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pilot_audit_run_id", sa.Integer(), sa.ForeignKey("pilot_audit_runs.id"), nullable=True),
        sa.Column("actor", sa.String(120), nullable=False),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("before_json", sa.JSON(), nullable=True),
        sa.Column("after_json", sa.JSON(), nullable=True),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "phase14_audit_events",
        "mvp_closure_decisions",
        "backup_export_records",
        "retention_policy_records",
        "ops_readiness_checks",
        "fix_pack_recommendations",
        "scale_decision_records",
        "risk_register_items",
        "phase_readiness_audits",
        "pilot_kpi_snapshots",
        "pilot_audit_runs",
    ]:
        op.drop_table(table)
