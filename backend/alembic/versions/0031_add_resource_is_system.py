"""add resource system marker"""

from alembic import op
import sqlalchemy as sa


revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("resource", sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE resource SET is_system = true WHERE code = 'general_points'")
    op.alter_column("resource", "is_system", server_default=None)


def downgrade() -> None:
    op.drop_column("resource", "is_system")
