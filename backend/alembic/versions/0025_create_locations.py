"""create locations"""

from alembic import op
import sqlalchemy as sa


revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "location",
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("is_discovered", sa.Boolean(), nullable=False),
        sa.Column("worker_days", sa.Integer(), nullable=False),
        sa.Column("requirements", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_table(
        "locationneighbor",
        sa.Column("location_code", sa.String(), nullable=False),
        sa.Column("neighbor_location_code", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["location_code"], ["location.code"]),
        sa.ForeignKeyConstraint(["neighbor_location_code"], ["location.code"]),
        sa.PrimaryKeyConstraint("location_code", "neighbor_location_code"),
    )


def downgrade() -> None:
    op.drop_table("locationneighbor")
    op.drop_table("location")
