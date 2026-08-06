"""seed game objects"""

from alembic import op
import sqlalchemy as sa


revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


objects = [
    {"code": "fishing_boat", "name": "Fishing Boat", "image_path": None, "description": "A small boat for fishing.", "worker_days": 10, "construction_resources": {}, "additional_data": {}, "max_workers": 3, "outputs": {}},
]


def upgrade() -> None:
    game_object = sa.table(
        "gameobject",
        sa.column("code", sa.String()), sa.column("name", sa.String()), sa.column("image_path", sa.String()),
        sa.column("description", sa.String()), sa.column("worker_days", sa.Integer()),
        sa.column("construction_resources", sa.JSON()), sa.column("additional_data", sa.JSON()),
        sa.column("max_workers", sa.Integer()), sa.column("outputs", sa.JSON()),
    )
    op.bulk_insert(game_object, objects)


def downgrade() -> None:
    op.execute("DELETE FROM gameobject WHERE code = 'fishing_boat'")
