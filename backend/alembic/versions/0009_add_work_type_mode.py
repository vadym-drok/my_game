"""add work type mode"""

from alembic import op
import sqlalchemy as sa


revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "worktypedefinition",
        sa.Column("mode", sa.String(), nullable=False, server_default="continuous"),
    )
