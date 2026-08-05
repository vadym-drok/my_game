"""create building definitions"""

from alembic import op
import sqlalchemy as sa


revision = "0012"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "buildingdefinition",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("building_type", sa.String(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_buildingdefinition_code", "buildingdefinition", ["code"])
