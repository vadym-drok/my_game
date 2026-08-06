"""seed game items"""

from alembic import op
import sqlalchemy as sa

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None

items = [{"code": "fishing_boat", "name": "Fishing Boat", "image_path": None, "description": "A small boat for fishing.", "worker_days": 10, "construction_resources": {}, "additional_data": {}, "max_workers": 3, "outputs": {}}]


def upgrade() -> None:
    game_item = sa.table("gameitem", sa.column("code", sa.String()), sa.column("name", sa.String()), sa.column("image_path", sa.String()), sa.column("description", sa.String()), sa.column("worker_days", sa.Integer()), sa.column("construction_resources", sa.JSON()), sa.column("additional_data", sa.JSON()), sa.column("max_workers", sa.Integer()), sa.column("outputs", sa.JSON()))
    op.bulk_insert(game_item, items)


def downgrade() -> None:
    op.execute("DELETE FROM gameitem WHERE code = 'fishing_boat'")
