"""add resource order"""

from alembic import op
import sqlalchemy as sa


revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("resource", sa.Column("order", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("resource", "order", server_default=None)


def downgrade() -> None:
    op.drop_column("resource", "order")
