"""add hunger"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "nation",
        sa.Column("population_growth_progress", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "nation",
        sa.Column("consecutive_hunger_days", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "dayreport",
        sa.Column("food_shortage", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "dayreport",
        sa.Column("is_hungry", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
