"""add definition image paths"""

from alembic import op
import sqlalchemy as sa


revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("resource", "worktypedefinition", "buildingdefinition"):
        op.add_column(table, sa.Column("image_path", sa.String(), nullable=True))

def downgrade() -> None:
    for table in ("buildingdefinition", "worktypedefinition", "resource"):
        op.drop_column(table, "image_path")
