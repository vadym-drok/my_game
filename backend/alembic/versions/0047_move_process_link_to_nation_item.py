"""move process link to nation item"""

from alembic import op
import sqlalchemy as sa


revision = "0047"
down_revision = "0046"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("nationitem", sa.Column("process_id", sa.Integer(), nullable=True))
    op.execute("UPDATE nationitem AS ni SET process_id = (SELECT p.id FROM process AS p WHERE p.nation_item_id = ni.id ORDER BY p.id DESC LIMIT 1) WHERE EXISTS (SELECT 1 FROM process AS p WHERE p.nation_item_id = ni.id)")
    op.create_foreign_key("fk_nationitem_process_id", "nationitem", "process", ["process_id"], ["id"])
    op.create_index("ix_nationitem_process_id", "nationitem", ["process_id"])
    op.drop_constraint("fk_process_nation_item_id", "process", type_="foreignkey")
    op.drop_index("ix_process_nation_item_id", table_name="process")
    op.drop_column("process", "nation_item_id")


def downgrade() -> None:
    raise NotImplementedError("Process item link reversal is not supported")
