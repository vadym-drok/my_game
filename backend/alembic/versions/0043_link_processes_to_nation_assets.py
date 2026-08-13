"""link processes to nation buildings and items"""

from alembic import op
import sqlalchemy as sa


revision = "0043"
down_revision = "0042"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("process", sa.Column("nation_building_id", sa.Integer(), nullable=True))
    op.add_column("process", sa.Column("nation_item_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_process_nation_building_id", "process", "nationbuilding", ["nation_building_id"], ["id"])
    op.create_foreign_key("fk_process_nation_item_id", "process", "nationitem", ["nation_item_id"], ["id"])
    op.create_index("ix_process_nation_building_id", "process", ["nation_building_id"])
    op.create_index("ix_process_nation_item_id", "process", ["nation_item_id"])


def downgrade() -> None:
    op.drop_index("ix_process_nation_item_id", table_name="process")
    op.drop_index("ix_process_nation_building_id", table_name="process")
    op.drop_constraint("fk_process_nation_item_id", "process", type_="foreignkey")
    op.drop_constraint("fk_process_nation_building_id", "process", type_="foreignkey")
    op.drop_column("process", "nation_item_id")
    op.drop_column("process", "nation_building_id")
