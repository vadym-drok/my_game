"""seed game items"""

from alembic import op
import sqlalchemy as sa

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None

items = [{"code": "fishing_boat", "name": "Fishing Boat", "image_path": "/images/game_items/fishing_boat.png", "visual_type": "illustration", "description": "A small boat for fishing.", "worker_days": 10, "construction_resources": {}, "additional_data": {}, "max_workers": 3, "outputs": {}}, {"code": "merchant_ship", "name": "Merchant Ship", "image_path": "/images/game_items/merchant_ship.png", "visual_type": "illustration", "description": "", "worker_days": 100, "construction_resources": {}, "additional_data": {"warehouse_capacity": 3000}, "max_workers": 60, "outputs": {}}]


def upgrade() -> None:
    game_item = sa.table("gameitem", sa.column("code", sa.String()), sa.column("name", sa.String()), sa.column("image_path", sa.String()), sa.column("visual_type", sa.String()), sa.column("description", sa.String()), sa.column("worker_days", sa.Integer()), sa.column("construction_resources", sa.JSON()), sa.column("additional_data", sa.JSON()), sa.column("max_workers", sa.Integer()), sa.column("outputs", sa.JSON()))
    op.bulk_insert(game_item, items)


def downgrade() -> None:
    op.execute("DELETE FROM gameitem WHERE code IN ('fishing_boat', 'merchant_ship')")
