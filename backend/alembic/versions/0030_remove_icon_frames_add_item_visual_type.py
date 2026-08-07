"""remove icon frames and add game item visual type"""

from alembic import op
import sqlalchemy as sa


revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "visual_type" not in {column["name"] for column in inspector.get_columns("gameitem")}:
        op.add_column("gameitem", sa.Column("visual_type", sa.String(), nullable=False, server_default="icon"))
        op.alter_column("gameitem", "visual_type", server_default=None)
    op.execute("UPDATE gameitem SET visual_type = 'illustration' WHERE code IN ('fishing_boat', 'merchant_ship')")
    for table in ("resource", "worktypedefinition", "buildingdefinition"):
        if "icon_frame_id" in {column["name"] for column in inspector.get_columns(table)}:
            op.drop_column(table, "icon_frame_id")
    if "iconframe" in inspector.get_table_names():
        op.drop_table("iconframe")


def downgrade() -> None:
    op.add_column("buildingdefinition", sa.Column("icon_frame_id", sa.Integer(), nullable=True))
    op.add_column("worktypedefinition", sa.Column("icon_frame_id", sa.Integer(), nullable=True))
    op.add_column("resource", sa.Column("icon_frame_id", sa.Integer(), nullable=True))
    op.create_table("iconframe", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("code", sa.String(), nullable=False), sa.Column("name", sa.String(), nullable=False), sa.Column("image_path", sa.String(), nullable=True), sa.UniqueConstraint("code"))
    op.drop_column("gameitem", "visual_type")
