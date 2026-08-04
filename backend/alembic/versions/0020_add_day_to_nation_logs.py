"""add game day to nation logs"""

from alembic import op
import sqlalchemy as sa


revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("nationlog", sa.Column("day", sa.Integer(), nullable=False, server_default="1"))
    op.execute(
        "UPDATE nationlog SET day = reports.count + 1 "
        "FROM (SELECT nation_id, COUNT(*) AS count FROM dayreport GROUP BY nation_id) reports "
        "WHERE nationlog.nation_id = reports.nation_id"
    )
    op.alter_column("nationlog", "day", server_default=None)


def downgrade() -> None:
    op.drop_column("nationlog", "day")
