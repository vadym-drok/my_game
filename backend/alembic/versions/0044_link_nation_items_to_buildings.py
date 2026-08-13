"""link nation items to buildings"""

from alembic import op
import sqlalchemy as sa


revision = "0044"
down_revision = "0043"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("nationitem", sa.Column("nation_building_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_nationitem_nation_building_id", "nationitem", "nationbuilding", ["nation_building_id"], ["id"])
    op.create_index("ix_nationitem_nation_building_id", "nationitem", ["nation_building_id"])


def downgrade() -> None:
    op.drop_index("ix_nationitem_nation_building_id", table_name="nationitem")
    op.drop_constraint("fk_nationitem_nation_building_id", "nationitem", type_="foreignkey")
    op.drop_column("nationitem", "nation_building_id")
