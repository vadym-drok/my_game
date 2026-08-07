"""add location connection handles"""

from alembic import op
import sqlalchemy as sa


revision = "0035"
down_revision = "0034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("locationneighbor", sa.Column("location_handle", sa.String(), nullable=True))
    op.add_column("locationneighbor", sa.Column("neighbor_handle", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("locationneighbor", "neighbor_handle")
    op.drop_column("locationneighbor", "location_handle")
