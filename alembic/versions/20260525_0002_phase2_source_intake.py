"""phase 2 source intake

Revision ID: 20260525_0002
Revises: 20260525_0001
Create Date: 2026-05-25
"""

import sqlalchemy as sa

from alembic import op

revision = "20260525_0002"
down_revision = "20260525_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(80), nullable=False, unique=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("operation", sa.String(40), nullable=False),
        sa.Column("category", sa.String(120), nullable=True),
        sa.Column("city", sa.String(120), nullable=True),
        sa.Column("country", sa.String(120), nullable=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("dry_run", sa.Boolean(), nullable=False),
        sa.Column("requested_limit", sa.Integer(), nullable=True),
        sa.Column("fetched_count", sa.Integer(), nullable=False),
        sa.Column("stored_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("error_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "source_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_run_id", sa.Integer(), sa.ForeignKey("source_runs.id"), nullable=False),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("request_key", sa.String(255), nullable=False),
        sa.Column("request_url_redacted", sa.String(1000), nullable=True),
        sa.Column("request_params_json", sa.JSON(), nullable=True),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column("response_count", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("cache_hit", sa.Boolean(), nullable=False),
        sa.Column("error_type", sa.String(120), nullable=True),
        sa.Column("error_message", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "raw_source_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_run_id", sa.Integer(), sa.ForeignKey("source_runs.id"), nullable=False),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("source_external_id", sa.String(255), nullable=True),
        sa.Column("record_type", sa.String(40), nullable=False),
        sa.Column("raw_name", sa.String(255), nullable=True),
        sa.Column("raw_category", sa.String(255), nullable=True),
        sa.Column("raw_address", sa.String(500), nullable=True),
        sa.Column("raw_city", sa.String(120), nullable=True),
        sa.Column("raw_suburb", sa.String(120), nullable=True),
        sa.Column("raw_country", sa.String(120), nullable=True),
        sa.Column("raw_lat", sa.Float(), nullable=True),
        sa.Column("raw_lng", sa.Float(), nullable=True),
        sa.Column("raw_phone", sa.String(120), nullable=True),
        sa.Column("raw_email", sa.String(255), nullable=True),
        sa.Column("raw_website", sa.String(1000), nullable=True),
        sa.Column("raw_opening_hours_json", sa.JSON(), nullable=True),
        sa.Column("raw_social_links_json", sa.JSON(), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("fingerprint", sa.String(128), nullable=False, unique=True),
        sa.Column("record_hash", sa.String(128), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "source_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("cache_key", sa.String(255), nullable=False, unique=True),
        sa.Column("request_hash", sa.String(128), nullable=False),
        sa.Column("response_json", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "source_rate_limits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("window_key", sa.String(120), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.Column("credit_estimate", sa.Float(), nullable=True),
        sa.Column("window_started_at", sa.DateTime(), nullable=False),
        sa.Column("window_ends_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "nzbn_entity_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "raw_source_record_id",
            sa.Integer(),
            sa.ForeignKey("raw_source_records.id"),
            nullable=False,
        ),
        sa.Column("source_run_id", sa.Integer(), sa.ForeignKey("source_runs.id"), nullable=False),
        sa.Column("query_name", sa.String(255), nullable=False),
        sa.Column("nzbn", sa.String(80), nullable=True),
        sa.Column("entity_name", sa.String(255), nullable=True),
        sa.Column("entity_status", sa.String(120), nullable=True),
        sa.Column("entity_type", sa.String(120), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("match_confidence", sa.Float(), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "raw_personalization_evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "raw_source_record_id",
            sa.Integer(),
            sa.ForeignKey("raw_source_records.id"),
            nullable=False,
        ),
        sa.Column("source_run_id", sa.Integer(), sa.ForeignKey("source_runs.id"), nullable=False),
        sa.Column("evidence_type", sa.String(120), nullable=False),
        sa.Column("evidence_value", sa.String(1000), nullable=False),
        sa.Column("evidence_source", sa.String(120), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("allowed_for_future_copy", sa.Boolean(), nullable=False),
        sa.Column("requires_verification", sa.Boolean(), nullable=False),
        sa.Column("risk_flag", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "raw_personalization_evidence",
        "nzbn_entity_matches",
        "source_rate_limits",
        "source_cache",
        "raw_source_records",
        "source_requests",
        "source_runs",
    ]:
        op.drop_table(table)
