"""seed location work types"""

from alembic import op
import sqlalchemy as sa


revision = "0037"
down_revision = "0036"
branch_labels = None
depends_on = None


location_work_types = [
    {"location_code": "starting_bay", "work_type_code": "building"},
    {"location_code": "starting_bay", "work_type_code": "fishing"},
    {"location_code": "forest", "work_type_code": "investigation"},
    {"location_code": "forest", "work_type_code": "building"},
    {"location_code": "forest", "work_type_code": "hunting"},
    {"location_code": "forest", "work_type_code": "woodcutting"},
    {"location_code": "forest", "work_type_code": "food_gathering"},
    {"location_code": "high_hill", "work_type_code": "investigation"},
    {"location_code": "high_hill", "work_type_code": "building"},
    {"location_code": "high_hill", "work_type_code": "food_gathering"},
    {"location_code": "high_hill", "work_type_code": "mining"},
    {"location_code": "riverbank", "work_type_code": "investigation"},
    {"location_code": "riverbank", "work_type_code": "building"},
    {"location_code": "riverbank", "work_type_code": "woodcutting"},
    {"location_code": "riverbank", "work_type_code": "fishing"},
]


def upgrade() -> None:
    op.execute("DELETE FROM process")
    op.bulk_insert(
        sa.table(
            "locationworktype",
            sa.column("location_code", sa.String()),
            sa.column("work_type_code", sa.String()),
        ),
        location_work_types,
    )


def downgrade() -> None:
    op.execute("DELETE FROM locationworktype")
