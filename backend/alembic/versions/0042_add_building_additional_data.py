"""add building additional data"""

from alembic import op
import sqlalchemy as sa


revision = "0042"
down_revision = "0041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "buildingdefinition",
        sa.Column("additional_data", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.execute(
        "UPDATE buildingdefinition SET capacity = 0, additional_data = "
        "'{\"boats\": {\"fishing_boat\": 4}}'::json WHERE code = 'small_pier'"
    )
    op.execute(
        "INSERT INTO buildingdefinition (code, name, building_type, capacity, image_path, construction_cost, additional_data) VALUES "
        "('woodcutters_lodge', 'Woodcutter''s Lodge', 'production', 0, '/images/buildings/woodcutters_lodge.webp', "
        "'{\"resources\": {\"wood\": 20}, \"worker_days\": 15}'::json, "
        "'{\"process\": {\"woodcutting\": {\"multiplier\": 2, \"workers\": 6}}}'::json) "
        "ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, building_type = EXCLUDED.building_type, "
        "capacity = EXCLUDED.capacity, image_path = EXCLUDED.image_path, construction_cost = EXCLUDED.construction_cost, "
        "additional_data = EXCLUDED.additional_data"
    )
    op.execute(
        "INSERT INTO locationbuildingdefinition (location_code, building_code) VALUES ('forest', 'woodcutters_lodge') "
        "ON CONFLICT DO NOTHING"
    )
    op.alter_column("buildingdefinition", "additional_data", server_default=None)


def downgrade() -> None:
    op.execute("DELETE FROM locationbuildingdefinition WHERE building_code = 'woodcutters_lodge'")
    op.execute("DELETE FROM buildingdefinition WHERE code = 'woodcutters_lodge'")
    op.drop_column("buildingdefinition", "additional_data")
