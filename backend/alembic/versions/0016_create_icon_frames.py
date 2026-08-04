"""create icon frames"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "iconframe",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_iconframe_code", "iconframe", ["code"])
    for table in ("resource", "worktypedefinition", "buildingdefinition"):
        op.add_column(table, sa.Column("icon_frame_id", sa.Integer(), nullable=True))
        op.create_index(f"ix_{table}_icon_frame_id", table, ["icon_frame_id"])
        op.create_foreign_key(f"fk_{table}_icon_frame", table, "iconframe", ["icon_frame_id"], ["id"])

    data = json.loads((Path(__file__).parents[2] / "data" / "raw_data.json").read_text())
    frame_table = sa.table("iconframe", sa.column("code", sa.String()), sa.column("name", sa.String()), sa.column("image_path", sa.String()))
    op.bulk_insert(frame_table, data["icon_frames"])
    bind = op.get_bind()
    frame_ids = dict(bind.execute(sa.text("SELECT code, id FROM iconframe")).all())
    for table, items in (("resource", data["resources"]), ("worktypedefinition", data["work_types"]), ("buildingdefinition", data["buildings"])):
        for item in items:
            bind.execute(
                sa.text(f"UPDATE {table} SET icon_frame_id = :frame_id WHERE code = :code"),
                {"code": item["code"], "frame_id": frame_ids[item["icon_frame_code"]]},
            )


def downgrade() -> None:
    for table in ("buildingdefinition", "worktypedefinition", "resource"):
        op.drop_constraint(f"fk_{table}_icon_frame", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_icon_frame_id", table_name=table)
        op.drop_column(table, "icon_frame_id")
    op.drop_index("ix_iconframe_code", table_name="iconframe")
    op.drop_table("iconframe")
