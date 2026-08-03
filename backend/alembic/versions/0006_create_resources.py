"""create resources"""

from alembic import op
import sqlalchemy as sa


revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "resource",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("storage_coefficient", sa.Float(), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_resource_code", "resource", ["code"])
