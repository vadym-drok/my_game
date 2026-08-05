"""add building construction cost"""

from alembic import op
import sqlalchemy as sa


revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "buildingdefinition",
        sa.Column("construction_cost", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.alter_column("buildingdefinition", "construction_cost", server_default=None)


def downgrade() -> None:
    op.drop_column("buildingdefinition", "construction_cost")
