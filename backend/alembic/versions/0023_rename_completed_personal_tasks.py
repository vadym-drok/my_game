"""rename completed personal tasks"""

from alembic import op


revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE personaltask SET status = 'done' WHERE status = 'completed'")


def downgrade() -> None:
    op.execute("UPDATE personaltask SET status = 'completed' WHERE status = 'done'")
