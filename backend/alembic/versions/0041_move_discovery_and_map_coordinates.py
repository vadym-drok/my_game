"""move discovery and map coordinates to their owners"""

from alembic import op
import sqlalchemy as sa


revision = "0041"
down_revision = "0040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("location", sa.Column("map_x", sa.Float(), nullable=False, server_default="0"))
    op.add_column("location", sa.Column("map_y", sa.Float(), nullable=False, server_default="0"))
    op.execute("UPDATE location AS l SET map_x = n.x, map_y = n.y FROM locationmapnode AS n WHERE n.location_code = l.code")
    op.alter_column("location", "map_x", server_default=None)
    op.alter_column("location", "map_y", server_default=None)
    op.create_table(
        "nationlocation",
        sa.Column("nation_id", sa.Integer(), nullable=False),
        sa.Column("location_code", sa.String(), nullable=False),
        sa.Column("is_discovered", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["nation_id"], ["nation.id"]),
        sa.ForeignKeyConstraint(["location_code"], ["location.code"]),
        sa.PrimaryKeyConstraint("nation_id", "location_code"),
    )
    op.execute("INSERT INTO nationlocation (nation_id, location_code, is_discovered) SELECT n.id, l.code, l.is_discovered FROM nation AS n CROSS JOIN location AS l")
    op.drop_table("locationmapnode")
    op.drop_column("location", "is_discovered")


def downgrade() -> None:
    op.add_column("location", sa.Column("is_discovered", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE location AS l SET is_discovered = EXISTS (SELECT 1 FROM nationlocation AS nl WHERE nl.location_code = l.code AND nl.is_discovered)")
    op.create_table("locationmapnode", sa.Column("location_code", sa.String(), nullable=False), sa.Column("x", sa.Float(), nullable=False), sa.Column("y", sa.Float(), nullable=False), sa.ForeignKeyConstraint(["location_code"], ["location.code"]), sa.PrimaryKeyConstraint("location_code"))
    op.execute("INSERT INTO locationmapnode (location_code, x, y) SELECT code, map_x, map_y FROM location")
    op.drop_table("nationlocation")
    op.drop_column("location", "map_y")
    op.drop_column("location", "map_x")
