"""create nation items"""

from alembic import op
import sqlalchemy as sa

revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("nationitem", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("nation_id", sa.Integer(), nullable=False), sa.Column("game_item_code", sa.String(), nullable=False), sa.Column("built_at", sa.Date(), nullable=False), sa.ForeignKeyConstraint(["nation_id"], ["nation.id"]), sa.ForeignKeyConstraint(["game_item_code"], ["gameitem.code"]))
    op.create_index(op.f("ix_nationitem_nation_id"), "nationitem", ["nation_id"], unique=False)
    op.create_index(op.f("ix_nationitem_game_item_code"), "nationitem", ["game_item_code"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_nationitem_game_item_code"), table_name="nationitem")
    op.drop_index(op.f("ix_nationitem_nation_id"), table_name="nationitem")
    op.drop_table("nationitem")
