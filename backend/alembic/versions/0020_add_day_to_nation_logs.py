"""add game day to nation logs"""

from alembic import op
import sqlalchemy as sa


revision = "0020"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("nationlog", sa.Column("day", sa.Integer(), nullable=False, server_default="1"))
    op.alter_column("nationlog", "day", server_default=None)


def downgrade() -> None:
    op.drop_column("nationlog", "day")
