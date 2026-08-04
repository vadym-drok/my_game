"""rename housing definition to tent"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    data = json.loads((Path(__file__).parents[2] / "data" / "raw_data.json").read_text())
    tent = next(building for building in data["buildings"] if building["code"] == "tent")
    table = sa.table(
        "buildingdefinition",
        sa.column("code", sa.String()),
        sa.column("name", sa.String()),
        sa.column("building_type", sa.String()),
        sa.column("capacity", sa.Integer()),
        sa.column("image_path", sa.String()),
        sa.column("construction_cost", sa.JSON()),
    )
    op.get_bind().execute(
        sa.update(table)
        .where(table.c.code == "housing")
        .values(
            code=tent["code"],
            name=tent["name"],
            building_type=tent["building_type"],
            capacity=tent["capacity"],
            image_path=tent["image_path"],
            construction_cost=tent["construction_cost"],
        )
    )


def downgrade() -> None:
    op.execute("UPDATE buildingdefinition SET code = 'housing', image_path = '/images/buildings/housing.png' WHERE code = 'tent'")
