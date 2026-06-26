"""phase11 inbox reply crm

Revision ID: 20260525_0011
Revises: 20260525_0010
Create Date: 2026-05-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260525_0011"
down_revision: str | None = "20260525_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inbox_sync_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(80), nullable=False, unique=True),
        sa.Column("provider_type", sa.String(80), nullable=False),
        sa.Column("mailbox", sa.String(255), nullable=False),
        sa.Column("operation", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("dry_run", sa.Boolean(), nullable=False),
        sa.Column("messages_seen", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("messages_imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("replies_detected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bounces_detected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("auto_replies_detected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "inbound_email_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sync_run_id", sa.Integer(), sa.ForeignKey("inbox_sync_runs.id"), nullable=False),
        sa.Column("provider_type", sa.String(80), nullable=False),
        sa.Column("mailbox", sa.String(255), nullable=False),
        sa.Column("message_uid", sa.String(255), nullable=True),
        sa.Column("message_id_header", sa.String(500), nullable=True),
        sa.Column("in_reply_to_header", sa.String(500), nullable=True),
        sa.Column("references_header", sa.Text(), nullable=True),
        sa.Column("from_email", sa.String(255), nullable=False),
        sa.Column("from_name", sa.String(255), nullable=True),
        sa.Column("to_email", sa.String(255), nullable=True),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("received_at", sa.DateTime(), nullable=False),
        sa.Column("raw_headers_json", sa.JSON(), nullable=False),
        sa.Column("body_text_sanitized", sa.Text(), nullable=False),
        sa.Column("body_hash", sa.String(64), nullable=False),
        sa.Column("raw_header_hash", sa.String(64), nullable=True),
        sa.Column("message_type", sa.String(80), nullable=False),
        sa.Column("matched_send_queue_id", sa.Integer(), sa.ForeignKey("email_send_queue.id"), nullable=True),
        sa.Column("matched_candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=True),
        sa.Column("duplicate_key", sa.String(255), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "inbound_message_parts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        sa.Column("part_type", sa.String(80), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "inbound_attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stored", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("blocked_reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "inbound_thread_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        sa.Column("email_send_queue_id", sa.Integer(), sa.ForeignKey("email_send_queue.id"), nullable=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=True),
        sa.Column("match_method", sa.String(80), nullable=False),
        sa.Column("match_confidence", sa.Float(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("manual_review_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "bounce_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=True),
        sa.Column("delivery_event_id", sa.Integer(), sa.ForeignKey("delivery_events.id"), nullable=True),
        sa.Column("email_send_queue_id", sa.Integer(), sa.ForeignKey("email_send_queue.id"), nullable=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=True),
        sa.Column("recipient_email", sa.String(255), nullable=False),
        sa.Column("bounce_source", sa.String(80), nullable=False),
        sa.Column("bounce_type", sa.String(80), nullable=False),
        sa.Column("bounce_reason", sa.String(500), nullable=False),
        sa.Column("diagnostic_text", sa.Text(), nullable=True),
        sa.Column("suppression_applied", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("manual_review_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "reply_classifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=True),
        sa.Column("classification", sa.String(80), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("classifier_type", sa.String(80), nullable=False),
        sa.Column("signals_json", sa.JSON(), nullable=False),
        sa.Column("manual_override", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "lead_response_statuses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("latest_status", sa.String(80), nullable=False),
        sa.Column("latest_inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=True),
        sa.Column("latest_send_queue_id", sa.Integer(), sa.ForeignKey("email_send_queue.id"), nullable=True),
        sa.Column("human_action_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status_reason", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "human_response_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=True),
        sa.Column("task_type", sa.String(80), nullable=False),
        sa.Column("priority", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "mailbox_readiness_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_slug", sa.String(120), nullable=False, unique=True),
        sa.Column("provider_type", sa.String(80), nullable=False),
        sa.Column("mailbox_email", sa.String(255), nullable=False),
        sa.Column("imap_host", sa.String(255), nullable=True),
        sa.Column("imap_port", sa.Integer(), nullable=True),
        sa.Column("use_ssl", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("last_sync_at", sa.DateTime(), nullable=True),
        sa.Column("last_seen_uid", sa.String(255), nullable=True),
        sa.Column("notes_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "provider_webhook_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider_type", sa.String(80), nullable=False),
        sa.Column("event_type", sa.String(120), nullable=False),
        sa.Column("provider_message_id", sa.String(255), nullable=True),
        sa.Column("recipient_email", sa.String(255), nullable=False),
        sa.Column("signature_valid", sa.Boolean(), nullable=False),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "reply_manual_overrides",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=False),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=True),
        sa.Column("old_classification", sa.String(80), nullable=False),
        sa.Column("new_classification", sa.String(80), nullable=False),
        sa.Column("old_status", sa.String(80), nullable=True),
        sa.Column("new_status", sa.String(80), nullable=True),
        sa.Column("reviewer", sa.String(255), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "lead_response_timeline",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_business_id", sa.Integer(), sa.ForeignKey("candidate_businesses.id"), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("event_source", sa.String(120), nullable=False),
        sa.Column("event_summary", sa.String(500), nullable=False),
        sa.Column("related_send_queue_id", sa.Integer(), sa.ForeignKey("email_send_queue.id"), nullable=True),
        sa.Column("related_inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "inbound_audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inbound_message_id", sa.Integer(), sa.ForeignKey("inbound_email_messages.id"), nullable=True),
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
        "inbound_audit_events",
        "lead_response_timeline",
        "reply_manual_overrides",
        "provider_webhook_events",
        "mailbox_readiness_profiles",
        "human_response_tasks",
        "lead_response_statuses",
        "reply_classifications",
        "bounce_events",
        "inbound_thread_matches",
        "inbound_attachments",
        "inbound_message_parts",
        "inbound_email_messages",
        "inbox_sync_runs",
    ]:
        op.drop_table(table)
