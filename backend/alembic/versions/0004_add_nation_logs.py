"""add nation logs"""

from alembic import op
import sqlalchemy as sa


revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "nationlog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nation_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["nation_id"], ["nation.id"]),
    )
    op.create_index("ix_nationlog_nation_id", "nationlog", ["nation_id"])
