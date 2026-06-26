"""phase 3 candidates

Revision ID: 20260525_0003
Revises: 20260525_0002
Create Date: 2026-05-25
"""

import sqlalchemy as sa

from alembic import op

revision = "20260525_0003"
down_revision = "20260525_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "candidate_businesses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("candidate_identity_fingerprint", sa.String(128), nullable=False, unique=True),
        sa.Column("canonical_name", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False),
        sa.Column("canonical_category", sa.String(120), nullable=False),
        sa.Column("canonical_subcategory", sa.String(120), nullable=True),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("suburb", sa.String(120), nullable=True),
        sa.Column("country", sa.String(120), nullable=False),
        sa.Column("address_line", sa.String(500), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("geo_hash", sa.String(80), nullable=True),
        sa.Column("geo_confidence", sa.Float(), nullable=True),
        sa.Column("identity_confidence", sa.Float(), nullable=False),
        sa.Column("category_confidence", sa.Float(), nullable=False),
        sa.Column("data_quality_score", sa.Float(), nullable=False),
        sa.Column("duplicate_risk_score", sa.Float(), nullable=False),
        sa.Column("chain_risk_score", sa.Float(), nullable=False),
        sa.Column("generic_name_risk_score", sa.Float(), nullable=False),
        sa.Column("verification_readiness_status", sa.String(80), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("created_from_run_id", sa.String(80), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "candidate_source_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_business_id",
            sa.Integer(),
            sa.ForeignKey("candidate_businesses.id"),
            nullable=False,
        ),
        sa.Column(
            "raw_source_record_id",
            sa.Integer(),
            sa.ForeignKey("raw_source_records.id"),
            nullable=False,
        ),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("link_type", sa.String(60), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("match_reasons_json", sa.JSON(), nullable=False),
        sa.Column("risk_flags_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "candidate_aliases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_business_id",
            sa.Integer(),
            sa.ForeignKey("candidate_businesses.id"),
            nullable=False,
        ),
        sa.Column("alias", sa.String(255), nullable=False),
        sa.Column("normalized_alias", sa.String(255), nullable=False),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "normalized_locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_business_id",
            sa.Integer(),
            sa.ForeignKey("candidate_businesses.id"),
            nullable=False,
        ),
        sa.Column("raw_address", sa.String(500), nullable=True),
        sa.Column("normalized_address", sa.String(500), nullable=True),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("suburb", sa.String(120), nullable=True),
        sa.Column("country", sa.String(120), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("geo_hash", sa.String(80), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "candidate_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_business_id",
            sa.Integer(),
            sa.ForeignKey("candidate_businesses.id"),
            nullable=False,
        ),
        sa.Column("raw_category", sa.String(255), nullable=True),
        sa.Column("canonical_category", sa.String(120), nullable=False),
        sa.Column("canonical_subcategory", sa.String(120), nullable=True),
        sa.Column("source_name", sa.String(40), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "candidate_quality_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_business_id",
            sa.Integer(),
            sa.ForeignKey("candidate_businesses.id"),
            nullable=False,
        ),
        sa.Column("quality_score", sa.Float(), nullable=False),
        sa.Column("identity_score", sa.Float(), nullable=False),
        sa.Column("location_score", sa.Float(), nullable=False),
        sa.Column("category_score", sa.Float(), nullable=False),
        sa.Column("contact_hint_score", sa.Float(), nullable=False),
        sa.Column("source_diversity_score", sa.Float(), nullable=False),
        sa.Column("personalization_evidence_score", sa.Float(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("readiness_decision", sa.String(80), nullable=False),
        sa.Column("quality_notes_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "candidate_personalization_evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_business_id",
            sa.Integer(),
            sa.ForeignKey("candidate_businesses.id"),
            nullable=False,
        ),
        sa.Column("evidence_type", sa.String(120), nullable=False),
        sa.Column("evidence_value", sa.String(1000), nullable=False),
        sa.Column("evidence_source", sa.String(120), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("allowed_for_future_copy", sa.Boolean(), nullable=False),
        sa.Column("requires_verification", sa.Boolean(), nullable=False),
        sa.Column("risk_flag", sa.String(255), nullable=True),
        sa.Column("supporting_raw_record_ids_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "normalization_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(80), nullable=False, unique=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("source_run_id", sa.Integer(), sa.ForeignKey("source_runs.id"), nullable=True),
        sa.Column("operation", sa.String(80), nullable=False),
        sa.Column("status", sa.String(60), nullable=False),
        sa.Column("dry_run", sa.Boolean(), nullable=False),
        sa.Column("input_raw_count", sa.Integer(), nullable=False),
        sa.Column("candidate_created_count", sa.Integer(), nullable=False),
        sa.Column("candidate_updated_count", sa.Integer(), nullable=False),
        sa.Column("duplicate_cluster_count", sa.Integer(), nullable=False),
        sa.Column("manual_review_count", sa.Integer(), nullable=False),
        sa.Column("rejected_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "duplicate_clusters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "normalization_run_id",
            sa.Integer(),
            sa.ForeignKey("normalization_runs.id"),
            nullable=False,
        ),
        sa.Column("cluster_key", sa.String(128), nullable=False),
        sa.Column("cluster_status", sa.String(60), nullable=False),
        sa.Column(
            "candidate_business_id",
            sa.Integer(),
            sa.ForeignKey("candidate_businesses.id"),
            nullable=True,
        ),
        sa.Column("raw_record_ids_json", sa.JSON(), nullable=False),
        sa.Column("cluster_score", sa.Float(), nullable=False),
        sa.Column("cluster_reasons_json", sa.JSON(), nullable=False),
        sa.Column("risk_flags_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "candidate_manual_review_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_business_id",
            sa.Integer(),
            sa.ForeignKey("candidate_businesses.id"),
            nullable=True,
        ),
        sa.Column(
            "duplicate_cluster_id",
            sa.Integer(),
            sa.ForeignKey("duplicate_clusters.id"),
            nullable=True,
        ),
        sa.Column("review_type", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(40), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "candidate_conflicts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_business_id",
            sa.Integer(),
            sa.ForeignKey("candidate_businesses.id"),
            nullable=True,
        ),
        sa.Column(
            "duplicate_cluster_id",
            sa.Integer(),
            sa.ForeignKey("duplicate_clusters.id"),
            nullable=True,
        ),
        sa.Column("conflict_type", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(40), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "candidate_conflicts",
        "candidate_manual_review_items",
        "duplicate_clusters",
        "normalization_runs",
        "candidate_personalization_evidence",
        "candidate_quality_reports",
        "candidate_categories",
        "normalized_locations",
        "candidate_aliases",
        "candidate_source_links",
        "candidate_businesses",
    ]:
        op.drop_table(table)
