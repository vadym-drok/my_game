"""seed locations"""

from alembic import op
import sqlalchemy as sa


revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


locations = [
    {"code": "starting_bay", "name": "Starting Bay", "description": "The sheltered bay where the ship first made landfall.", "is_discovered": True, "worker_days": 0, "requirements": {}},
    {"code": "forest", "name": "Forest", "description": "A dense forest rich with timber and wild food.", "is_discovered": False, "worker_days": 3, "requirements": {}},
    {"code": "high_hill", "name": "High Hill", "description": "A steep, high hill that rises almost like a small mountain.", "is_discovered": False, "worker_days": 3, "requirements": {}},
    {"code": "riverbank", "name": "Riverbank", "description": "The fertile banks along the river.", "is_discovered": False, "worker_days": 3, "requirements": {}},
]
neighbors = [
    {"location_code": "starting_bay", "neighbor_location_code": "forest"},
    {"location_code": "starting_bay", "neighbor_location_code": "riverbank"},
    {"location_code": "starting_bay", "neighbor_location_code": "high_hill"},
    {"location_code": "forest", "neighbor_location_code": "starting_bay"},
    {"location_code": "forest", "neighbor_location_code": "high_hill"},
    {"location_code": "forest", "neighbor_location_code": "riverbank"},
    {"location_code": "high_hill", "neighbor_location_code": "forest"},
    {"location_code": "high_hill", "neighbor_location_code": "starting_bay"},
    {"location_code": "riverbank", "neighbor_location_code": "starting_bay"},
    {"location_code": "riverbank", "neighbor_location_code": "forest"},
]


def upgrade() -> None:
    location = sa.table(
        "location",
        sa.column("code", sa.String()), sa.column("name", sa.String()),
        sa.column("description", sa.String()), sa.column("is_discovered", sa.Boolean()),
        sa.column("worker_days", sa.Integer()), sa.column("requirements", sa.JSON()),
    )
    neighbor = sa.table(
        "locationneighbor",
        sa.column("location_code", sa.String()), sa.column("neighbor_location_code", sa.String()),
    )
    op.bulk_insert(location, locations)
    op.bulk_insert(neighbor, neighbors)


def downgrade() -> None:
    codes = ", ".join(f"'{location['code']}'" for location in locations)
    op.execute(f"DELETE FROM locationneighbor WHERE location_code IN ({codes}) OR neighbor_location_code IN ({codes})")
    op.execute(f"DELETE FROM location WHERE code IN ({codes})")
