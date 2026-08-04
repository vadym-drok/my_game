"""sync building construction costs"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    data = json.loads((Path(__file__).parents[2] / "data" / "raw_data.json").read_text())
    table = sa.table("buildingdefinition", sa.column("code", sa.String()), sa.column("construction_cost", sa.JSON()))
    bind = op.get_bind()
    for building in data["buildings"]:
        bind.execute(
            sa.update(table)
            .where(table.c.code == building["code"])
            .values(construction_cost=building["construction_cost"])
        )


def downgrade() -> None:
    pass
