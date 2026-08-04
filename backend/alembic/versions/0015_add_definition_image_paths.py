"""add definition image paths"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("resource", "worktypedefinition", "buildingdefinition"):
        op.add_column(table, sa.Column("image_path", sa.String(), nullable=True))

    data = json.loads((Path(__file__).parents[2] / "data" / "raw_data.json").read_text())
    bind = op.get_bind()
    for table, items in (("resource", data["resources"]), ("worktypedefinition", data["work_types"]), ("buildingdefinition", data["buildings"])):
        for item in items:
            bind.execute(
                sa.text(f"UPDATE {table} SET image_path = :image_path WHERE code = :code"),
                {"code": item["code"], "image_path": item.get("image_path")},
            )


def downgrade() -> None:
    for table in ("buildingdefinition", "worktypedefinition", "resource"):
        op.drop_column(table, "image_path")
