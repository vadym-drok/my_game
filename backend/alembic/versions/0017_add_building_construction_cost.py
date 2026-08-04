"""add building construction cost"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "buildingdefinition",
        sa.Column("construction_cost", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    data = json.loads((Path(__file__).parents[2] / "data" / "raw_data.json").read_text())
    table = sa.table("buildingdefinition", sa.column("code", sa.String()), sa.column("construction_cost", sa.JSON()))
    bind = op.get_bind()
    for building in data["buildings"]:
        bind.execute(
            sa.update(table)
            .where(table.c.code == building["code"])
            .values(construction_cost=building["construction_cost"])
        )
    op.alter_column("buildingdefinition", "construction_cost", server_default=None)


def downgrade() -> None:
    op.drop_column("buildingdefinition", "construction_cost")
