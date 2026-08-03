"""add general points"""

from alembic import op
import sqlalchemy as sa


revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "nation",
        sa.Column("general_points", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "dayreport",
        sa.Column("general_points", sa.Integer(), nullable=False, server_default="0"),
    )
