"""create work type definitions"""

from alembic import op
import sqlalchemy as sa


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "worktypedefinition",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("intensity", sa.String(), nullable=False),
        sa.Column("outputs", sa.JSON(), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_worktypedefinition_code", "worktypedefinition", ["code"])
