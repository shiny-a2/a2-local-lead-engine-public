"""phase13 sales workspace

Revision ID: 20260525_0013
Revises: 20260525_0012
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa

revision = "20260525_0013"
down_revision = "20260525_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sales_workspace_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(80), nullable=False, unique=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("operation", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("dry_run", sa.Boolean(), nullable=False),
        sa.Column("input_opportunity_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("workspace_item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tasks_created_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("checklists_created_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "sales_workspace_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False, unique=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("workspace_status", sa.String(80), nullable=False),
        sa.Column("priority", sa.String(40), nullable=False),
        sa.Column("owner", sa.String(120), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "scope_checklists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False, unique=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("checklist_type", sa.String(80), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("completeness_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quote_ready", sa.Boolean(), nullable=False),
        sa.Column("proposal_ready", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "scope_checklist_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scope_checklist_id", sa.Integer(), sa.ForeignKey("scope_checklists.id"), nullable=False),
        sa.Column("item_key", sa.String(120), nullable=False),
        sa.Column("question_text", sa.String(500), nullable=False),
        sa.Column("answer_text", sa.String(1000), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("notes", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "proposal_checklists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False, unique=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("proposal_type", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("readiness_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "proposal_checklist_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proposal_checklist_id", sa.Integer(), sa.ForeignKey("proposal_checklists.id"), nullable=False),
        sa.Column("item_key", sa.String(120), nullable=False),
        sa.Column("item_label", sa.String(255), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("notes", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "internal_pricing_worksheets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False, unique=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("pricing_status", sa.String(80), nullable=False),
        sa.Column("base_package", sa.String(120), nullable=True),
        sa.Column("selected_modules_json", sa.JSON(), nullable=False),
        sa.Column("manual_base_price", sa.Float(), nullable=True),
        sa.Column("manual_module_adjustments_json", sa.JSON(), nullable=True),
        sa.Column("manual_discount", sa.Float(), nullable=True),
        sa.Column("manual_notes", sa.String(1000), nullable=True),
        sa.Column("final_manual_quote", sa.Float(), nullable=True),
        sa.Column("quote_approved_by", sa.String(120), nullable=True),
        sa.Column("quote_approved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    for table in ("quote_readiness_gates", "proposal_readiness_gates"):
        op.create_table(
            table,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False),
            sa.Column("gate_name", sa.String(80), nullable=False),
            sa.Column("passed", sa.Boolean(), nullable=False),
            sa.Column("severity", sa.String(40), nullable=False),
            sa.Column("reason", sa.String(500), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
    op.create_table(
        "manual_followup_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False, unique=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("eligible", sa.Boolean(), nullable=False),
        sa.Column("followup_type", sa.String(40), nullable=False),
        sa.Column("not_before", sa.DateTime(), nullable=True),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "sales_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("task_type", sa.String(80), nullable=False),
        sa.Column("priority", sa.String(40), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("assigned_to", sa.String(120), nullable=True),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "manual_communication_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("communication_type", sa.String(80), nullable=False),
        sa.Column("channel", sa.String(40), nullable=False),
        sa.Column("summary", sa.String(1000), nullable=False),
        sa.Column("sent_by_human", sa.Boolean(), nullable=False),
        sa.Column("external_reference", sa.String(255), nullable=True),
        sa.Column("created_by", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table("opportunity_health_snapshots", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False), sa.Column("health_status", sa.String(80), nullable=False), sa.Column("reply_quality_score", sa.Integer(), nullable=False), sa.Column("scope_completeness_score", sa.Integer(), nullable=False), sa.Column("customer_intent_score", sa.Integer(), nullable=False), sa.Column("contact_reliability_score", sa.Integer(), nullable=False), sa.Column("proposal_readiness_score", sa.Integer(), nullable=False), sa.Column("task_overdue_risk_score", sa.Integer(), nullable=False), sa.Column("notes_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("next_human_actions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False), sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False), sa.Column("action_type", sa.String(80), nullable=False), sa.Column("priority", sa.String(40), nullable=False), sa.Column("reason", sa.String(500), nullable=False), sa.Column("due_at", sa.DateTime(), nullable=True), sa.Column("status", sa.String(40), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("opportunity_close_records", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False), sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False), sa.Column("close_reason", sa.String(80), nullable=False), sa.Column("closed_by", sa.String(120), nullable=False), sa.Column("notes", sa.String(1000), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("human_approval_ledger", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False), sa.Column("approval_type", sa.String(80), nullable=False), sa.Column("approved_by", sa.String(120), nullable=False), sa.Column("approved_at", sa.DateTime(), nullable=False), sa.Column("notes", sa.String(1000), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("phase13_decisions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False), sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False), sa.Column("decision", sa.String(80), nullable=False), sa.Column("ready_for_phase14", sa.Boolean(), nullable=False), sa.Column("manual_action_required", sa.Boolean(), nullable=False), sa.Column("closed", sa.Boolean(), nullable=False), sa.Column("reason", sa.String(500), nullable=False), sa.Column("warnings_json", sa.JSON(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("phase13_audit_events", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=True), sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=True), sa.Column("actor", sa.String(120), nullable=False), sa.Column("action", sa.String(80), nullable=False), sa.Column("before_json", sa.JSON(), nullable=True), sa.Column("after_json", sa.JSON(), nullable=True), sa.Column("reason", sa.String(500), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False))


def downgrade() -> None:
    for table in (
        "phase13_audit_events",
        "phase13_decisions",
        "human_approval_ledger",
        "opportunity_close_records",
        "next_human_actions",
        "opportunity_health_snapshots",
        "manual_communication_logs",
        "sales_tasks",
        "manual_followup_plans",
        "proposal_readiness_gates",
        "quote_readiness_gates",
        "internal_pricing_worksheets",
        "proposal_checklist_items",
        "proposal_checklists",
        "scope_checklist_items",
        "scope_checklists",
        "sales_workspace_items",
        "sales_workspace_runs",
    ):
        op.drop_table(table)
