"""sync definition names from raw data"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    data = json.loads((Path(__file__).parents[2] / "data" / "raw_data.json").read_text())
    bind = op.get_bind()
    frame_ids = dict(bind.execute(sa.text("SELECT code, id FROM iconframe")).all())

    tables = (
        ("iconframe", data["icon_frames"], ("name", "image_path")),
        ("resource", data["resources"], ("name", "storage_coefficient", "image_path")),
        ("worktypedefinition", data["work_types"], ("name", "intensity", "mode", "outputs", "image_path")),
        ("buildingdefinition", data["buildings"], ("name", "building_type", "capacity", "image_path", "construction_cost")),
    )
    for table_name, items, columns in tables:
        typed_columns = [
            sa.column(column, sa.JSON() if column in {"outputs", "construction_cost"} else None)
            for column in columns
        ]
        if table_name != "iconframe":
            typed_columns.append(sa.column("icon_frame_id", sa.Integer()))
        table = sa.table(table_name, sa.column("code", sa.String()), *typed_columns)
        for item in items:
            values = {column: item[column] for column in columns}
            if table_name != "iconframe":
                values["icon_frame_id"] = frame_ids[item["icon_frame_code"]]
            bind.execute(sa.update(table).where(table.c.code == item["code"]).values(**values))

    bind.execute(sa.text("UPDATE nation SET name = :name WHERE id = 1"), {"name": data["nation"]["name"]})


def downgrade() -> None:
    pass
