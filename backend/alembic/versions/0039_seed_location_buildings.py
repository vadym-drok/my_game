"""seed location buildings"""

from alembic import op
import sqlalchemy as sa


revision = "0039"
down_revision = "0038"
branch_labels = None
depends_on = None


location_buildings = [
    {"location_code": "starting_bay", "building_code": "tent"},
    {"location_code": "starting_bay", "building_code": "warehouse"},
    {"location_code": "starting_bay", "building_code": "small_pier"},
    {"location_code": "forest", "building_code": "tent"},
    {"location_code": "forest", "building_code": "warehouse"},
    {"location_code": "high_hill", "building_code": "tent"},
    {"location_code": "high_hill", "building_code": "warehouse"},
    {"location_code": "riverbank", "building_code": "tent"},
    {"location_code": "riverbank", "building_code": "warehouse"},
    {"location_code": "riverbank", "building_code": "small_pier"},
]


def upgrade() -> None:
    op.execute("INSERT INTO buildingdefinition (code, name, building_type, capacity, image_path, construction_cost) VALUES ('small_pier', 'Small Pier', 'pier', 10, '/images/buildings/small_pier.webp', '{\"resources\": {\"wood\": 10}, \"worker_days\": 20}'::json) ON CONFLICT (code) DO NOTHING")
    op.execute("DELETE FROM nationbuilding")
    op.bulk_insert(
        sa.table("locationbuildingdefinition", sa.column("location_code", sa.String()), sa.column("building_code", sa.String())),
        location_buildings,
    )


def downgrade() -> None:
    op.execute("DELETE FROM locationbuildingdefinition")
