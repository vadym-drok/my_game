"""create location map nodes"""

from alembic import op
import sqlalchemy as sa


revision = "0034"
down_revision = "0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "locationmapnode",
        sa.Column("location_code", sa.String(), nullable=False),
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["location_code"], ["location.code"]),
        sa.PrimaryKeyConstraint("location_code"),
    )
    op.bulk_insert(
        sa.table("locationmapnode", sa.column("location_code", sa.String()), sa.column("x", sa.Float()), sa.column("y", sa.Float())),
        [
            {"location_code": "starting_bay", "x": 0, "y": 0},
            {"location_code": "forest", "x": 320, "y": -160},
            {"location_code": "high_hill", "x": 520, "y": 190},
            {"location_code": "riverbank", "x": -270, "y": 210},
        ],
    )


def downgrade() -> None:
    op.drop_table("locationmapnode")
