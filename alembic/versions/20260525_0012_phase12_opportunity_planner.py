"""phase12 opportunity planner

Revision ID: 20260525_0012
Revises: 20260525_0011
Create Date: 2026-05-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260525_0012"
down_revision: str | None = "20260525_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "opportunity_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("source_inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False, unique=True),
        sa.Column("opportunity_status", sa.String(80), nullable=False),
        sa.Column("opportunity_type", sa.String(80), nullable=False),
        sa.Column("priority", sa.String(40), nullable=False),
        sa.Column("estimated_value_band", sa.String(80), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "manual_response_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        sa.Column("response_goal", sa.String(255), nullable=False),
        sa.Column("recommended_tone", sa.String(120), nullable=False),
        sa.Column("key_points_json", sa.JSON(), nullable=False),
        sa.Column("claims_allowed_json", sa.JSON(), nullable=False),
        sa.Column("claims_to_avoid_json", sa.JSON(), nullable=False),
        sa.Column("offer_package", sa.String(120), nullable=False),
        sa.Column("modules_to_mention_json", sa.JSON(), nullable=False),
        sa.Column("pricing_strategy", sa.String(120), nullable=False),
        sa.Column("cta_suggestion", sa.String(255), nullable=False),
        sa.Column("manual_notes_required", sa.Boolean(), nullable=False),
        *_timestamps(),
    )
    for table in ["pricing_guidance_records", "meeting_guidance_records", "response_guidance_records"]:
        cols = [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False),
            sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
            sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        ]
        if table == "pricing_guidance_records":
            cols += [
                sa.Column("pricing_strategy", sa.String(80), nullable=False),
                sa.Column("internal_price_band", sa.String(120), nullable=True),
                sa.Column("show_price_to_user", sa.Boolean(), nullable=False),
                sa.Column("manual_quote_required", sa.Boolean(), nullable=False),
                sa.Column("scope_questions_json", sa.JSON(), nullable=False),
                sa.Column("pricing_notes_json", sa.JSON(), nullable=False),
                sa.Column("blocked_price_claims_json", sa.JSON(), nullable=False),
            ]
        elif table == "meeting_guidance_records":
            cols += [
                sa.Column("meeting_requested", sa.Boolean(), nullable=False),
                sa.Column("automatic_scheduling_allowed", sa.Boolean(), nullable=False),
                sa.Column("recommended_action", sa.String(500), nullable=False),
                sa.Column("suggested_questions_json", sa.JSON(), nullable=False),
                sa.Column("manual_owner", sa.String(120), nullable=True),
            ]
        else:
            cols += [
                sa.Column("response_type", sa.String(80), nullable=False),
                sa.Column("response_goal", sa.String(255), nullable=False),
                sa.Column("key_points_json", sa.JSON(), nullable=False),
                sa.Column("things_to_avoid_json", sa.JSON(), nullable=False),
                sa.Column("recommended_tone", sa.String(120), nullable=False),
                sa.Column("cta_recommendation", sa.String(255), nullable=False),
                sa.Column("manual_review_required", sa.Boolean(), nullable=False),
            ]
        cols.append(sa.Column("created_at", sa.DateTime(), nullable=False))
        op.create_table(table, *cols)
    op.create_table(
        "reply_draft_suggestions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        sa.Column("draft_subject", sa.String(255), nullable=True),
        sa.Column("draft_body", sa.Text(), nullable=False),
        sa.Column("generation_mode", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("risk_flags_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "followup_eligibility_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        sa.Column("eligible", sa.Boolean(), nullable=False),
        sa.Column("followup_type", sa.String(80), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("not_before", sa.DateTime(), nullable=True),
        sa.Column("blocked_reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "phase12_human_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=True),
        sa.Column("task_type", sa.String(80), nullable=False),
        sa.Column("priority", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("assigned_to", sa.String(120), nullable=True),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("recommended_action", sa.String(500), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        *_timestamps(),
    )
    op.create_table(
        "human_sales_control_gates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=False),
        sa.Column("gate_name", sa.String(80), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("severity", sa.String(40), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "phase12_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=True),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        sa.Column("decision", sa.String(80), nullable=False),
        sa.Column("ready_for_phase13", sa.Boolean(), nullable=False),
        sa.Column("manual_action_required", sa.Boolean(), nullable=False),
        sa.Column("closed", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("warnings_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "opportunity_audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunity_records.id"), nullable=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=True),
        sa.Column("actor", sa.String(120), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("before_json", sa.JSON(), nullable=True),
        sa.Column("after_json", sa.JSON(), nullable=True),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "opportunity_audit_events",
        "phase12_decisions",
        "human_sales_control_gates",
        "phase12_human_tasks",
        "followup_eligibility_records",
        "reply_draft_suggestions",
        "response_guidance_records",
        "meeting_guidance_records",
        "pricing_guidance_records",
        "manual_response_plans",
        "opportunity_records",
    ]:
        op.drop_table(table)
