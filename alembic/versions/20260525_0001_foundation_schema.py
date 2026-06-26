"""foundation schema

Revision ID: 20260525_0001
Revises:
Create Date: 2026-05-25
"""

import sqlalchemy as sa

from alembic import op

revision = "20260525_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("target_city", sa.String(120), nullable=False),
        sa.Column("target_country", sa.String(120), nullable=False),
        sa.Column("target_categories_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("daily_send_limit", sa.Integer(), nullable=False),
        sa.Column("manual_approval_required", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_campaigns_slug", "campaigns", ["slug"], unique=True)

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("business_name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(120), nullable=False),
        sa.Column("subcategory", sa.String(120), nullable=True),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("suburb", sa.String(120), nullable=True),
        sa.Column("country", sa.String(120), nullable=False),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("source_confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "lead_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("source_external_id", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(1000), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(), nullable=True),
        sa.Column("fingerprint", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "lead_contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("email_type", sa.String(40), nullable=False),
        sa.Column("email_source", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(80), nullable=True),
        sa.Column("website_contact_url", sa.String(1000), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("is_allowed_for_outreach", sa.Boolean(), nullable=False),
        sa.Column("blocked_reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "lead_web_presence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("website_status", sa.String(40), nullable=False),
        sa.Column("official_website_url", sa.String(1000), nullable=True),
        sa.Column("facebook_url", sa.String(1000), nullable=True),
        sa.Column("instagram_url", sa.String(1000), nullable=True),
        sa.Column("linkedin_url", sa.String(1000), nullable=True),
        sa.Column("social_only", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "lead_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("website_score", sa.Float(), nullable=True),
        sa.Column("business_fit_score", sa.Float(), nullable=True),
        sa.Column("contact_quality_score", sa.Float(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("final_score", sa.Float(), nullable=True),
        sa.Column("decision", sa.String(60), nullable=False),
        sa.Column("decision_reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "email_drafts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("offer_type", sa.String(120), nullable=True),
        sa.Column("personalization_points_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "email_judgements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("draft_id", sa.Integer(), sa.ForeignKey("email_drafts.id"), nullable=False),
        sa.Column("judge_score", sa.Float(), nullable=True),
        sa.Column("decision", sa.String(40), nullable=False),
        sa.Column("truthfulness_score", sa.Float(), nullable=True),
        sa.Column("personalization_score", sa.Float(), nullable=True),
        sa.Column("spam_risk_score", sa.Float(), nullable=True),
        sa.Column("legal_risk_score", sa.Float(), nullable=True),
        sa.Column("flags_json", sa.JSON(), nullable=False),
        sa.Column("required_fixes_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "email_sends",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("draft_id", sa.Integer(), sa.ForeignKey("email_drafts.id"), nullable=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("recipient_email", sa.String(255), nullable=False),
        sa.Column("status", sa.String(60), nullable=False),
        sa.Column("provider", sa.String(120), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("blocked_reason", sa.String(255), nullable=True),
        sa.Column("message_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "suppression_list",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("reason", sa.String(40), nullable=False),
        sa.Column("source", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(120), nullable=False),
        sa.Column("entity_id", sa.String(120), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("actor", sa.String(40), nullable=False),
        sa.Column("run_id", sa.String(80), nullable=True),
        sa.Column("before_json", sa.JSON(), nullable=True),
        sa.Column("after_json", sa.JSON(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "audit_logs",
        "suppression_list",
        "email_sends",
        "email_judgements",
        "email_drafts",
        "lead_scores",
        "lead_web_presence",
        "lead_contacts",
        "lead_sources",
        "leads",
        "campaigns",
    ]:
        op.drop_table(table)
