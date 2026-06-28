"""rewrite loop columns on email_draft_variants

Revision ID: 20260628_0001
Revises: 20260525_0014
"""

import sqlalchemy as sa

from alembic import op

revision = "20260628_0001"
down_revision = "20260525_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "email_draft_variants",
        sa.Column("rewrite_attempt", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "email_draft_variants",
        sa.Column("origin_email_draft_variant_id", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("email_draft_variants", "origin_email_draft_variant_id")
    op.drop_column("email_draft_variants", "rewrite_attempt")
