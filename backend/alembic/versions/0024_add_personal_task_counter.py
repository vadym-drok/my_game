"""add personal task counter"""

from alembic import op
import sqlalchemy as sa


revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("personaltask", sa.Column("counter", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("personaltask", "counter", server_default=None)


def downgrade() -> None:
    op.drop_column("personaltask", "counter")
