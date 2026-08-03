"""add population growth"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "nation", sa.Column("last_population_growth_date", sa.Date(), nullable=True)
    )
