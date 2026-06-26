"""phase9 human review

Revision ID: 20260525_0009
Revises: 20260525_0008
Create Date: 2026-05-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260525_0009"
down_revision: str | None = "20260525_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "human_review_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(80), nullable=False, unique=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("operation", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("input_draft_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("queued_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("approved_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("approved_with_warnings_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("edit_required_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("returned_to_rewrite_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("returned_to_judge_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("held_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rejected_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blocked_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "human_review_queue_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("human_review_run_id", sa.Integer(), sa.ForeignKey("human_review_runs.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("email_draft_variant_id", sa.Integer(), sa.ForeignKey("email_draft_variants.id"), nullable=False),
        sa.Column("phase8_decision_id", sa.Integer(), sa.ForeignKey("email_judge_decisions.id"), nullable=True),
        sa.Column("queue_status", sa.String(80), nullable=False),
        sa.Column("priority_tier", sa.String(80), nullable=True),
        sa.Column("campaign_lane", sa.String(80), nullable=True),
        sa.Column("reviewer", sa.String(120), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_lock_owner", sa.String(120), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lock_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email_draft_variant_id", name="uq_review_queue_draft"),
    )
    op.create_table(
        "human_review_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("human_review_run_id", sa.Integer(), sa.ForeignKey("human_review_runs.id"), nullable=False),
        sa.Column("queue_item_id", sa.Integer(), sa.ForeignKey("human_review_queue_items.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("email_draft_variant_id", sa.Integer(), sa.ForeignKey("email_draft_variants.id"), nullable=False),
        sa.Column("decision", sa.String(120), nullable=False),
        sa.Column("reviewer", sa.String(120), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "email_manual_edit_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("queue_item_id", sa.Integer(), sa.ForeignKey("human_review_queue_items.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("original_email_draft_variant_id", sa.Integer(), sa.ForeignKey("email_draft_variants.id"), nullable=False),
        sa.Column("previous_version_id", sa.Integer(), sa.ForeignKey("email_manual_edit_versions.id"), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("subject_text", sa.String(255), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column("editor", sa.String(120), nullable=False),
        sa.Column("edit_reason", sa.String(500), nullable=False),
        sa.Column("diff_json", sa.JSON(), nullable=True),
        sa.Column("edit_severity", sa.String(80), nullable=False),
        sa.Column("requires_rejudge", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "final_pre_send_checks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("queue_item_id", sa.Integer(), sa.ForeignKey("human_review_queue_items.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("email_manual_edit_version_id", sa.Integer(), sa.ForeignKey("email_manual_edit_versions.id"), nullable=True),
        sa.Column("email_draft_variant_id", sa.Integer(), sa.ForeignKey("email_draft_variants.id"), nullable=True),
        sa.Column("check_status", sa.String(80), nullable=False),
        sa.Column("sender_identity_ok", sa.Boolean(), nullable=False),
        sa.Column("unsubscribe_placeholder_ok", sa.Boolean(), nullable=False),
        sa.Column("recipient_contact_ok", sa.Boolean(), nullable=False),
        sa.Column("suppression_ok", sa.Boolean(), nullable=False),
        sa.Column("claim_safety_ok", sa.Boolean(), nullable=False),
        sa.Column("body_length_ok", sa.Boolean(), nullable=False),
        sa.Column("subject_ok", sa.Boolean(), nullable=False),
        sa.Column("single_cta_ok", sa.Boolean(), nullable=False),
        sa.Column("judge_validity_ok", sa.Boolean(), nullable=False),
        sa.Column("staleness_ok", sa.Boolean(), nullable=False),
        sa.Column("manual_approval_ok", sa.Boolean(), nullable=False),
        sa.Column("mailbox_readiness_ok", sa.Boolean(), nullable=False),
        sa.Column("risk_flags_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "phase9_candidate_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("human_review_run_id", sa.Integer(), sa.ForeignKey("human_review_runs.id"), nullable=False),
        sa.Column("queue_item_id", sa.Integer(), sa.ForeignKey("human_review_queue_items.id"), nullable=False),
        sa.Column("decision", sa.String(120), nullable=False),
        sa.Column("ready_for_phase10", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("manual_edit_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("blocked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("hold_reason", sa.String(500), nullable=True),
        sa.Column("reject_reason", sa.String(500), nullable=True),
        sa.Column("warnings_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "human_review_audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("queue_item_id", sa.Integer(), sa.ForeignKey("human_review_queue_items.id"), nullable=False),
        sa.Column("actor", sa.String(120), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("before_json", sa.JSON(), nullable=True),
        sa.Column("after_json", sa.JSON(), nullable=True),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table("review_users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("username", sa.String(120), nullable=False, unique=True), sa.Column("display_name", sa.String(120), nullable=False), sa.Column("role", sa.String(40), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=True), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_table("review_locks", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("queue_item_id", sa.Integer(), sa.ForeignKey("human_review_queue_items.id"), nullable=False), sa.Column("locked_by", sa.String(120), nullable=False), sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("released_at", sa.DateTime(timezone=True), nullable=True), sa.Column("status", sa.String(40), nullable=False))
    op.create_table("sender_identity_profiles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("profile_slug", sa.String(120), nullable=False, unique=True), sa.Column("provider_type", sa.String(80), nullable=False), sa.Column("from_email", sa.String(255), nullable=False), sa.Column("from_name", sa.String(255), nullable=False), sa.Column("reply_to_email", sa.String(255), nullable=False), sa.Column("domain", sa.String(255), nullable=False), sa.Column("status", sa.String(80), nullable=False), sa.Column("readiness_notes_json", sa.JSON(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=True), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_table("mailbox_readiness_checks", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("sender_profile_id", sa.Integer(), sa.ForeignKey("sender_identity_profiles.id"), nullable=True), sa.Column("reply_to_email", sa.String(255), nullable=False), sa.Column("inbox_monitoring_mode", sa.String(80), nullable=False), sa.Column("bounce_processing_mode", sa.String(80), nullable=False), sa.Column("readiness_status", sa.String(80), nullable=False), sa.Column("notes_json", sa.JSON(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    for table in [
        "mailbox_readiness_checks",
        "sender_identity_profiles",
        "review_locks",
        "review_users",
        "human_review_audit_events",
        "phase9_candidate_decisions",
        "final_pre_send_checks",
        "email_manual_edit_versions",
        "human_review_decisions",
        "human_review_queue_items",
        "human_review_runs",
    ]:
        op.drop_table(table)
