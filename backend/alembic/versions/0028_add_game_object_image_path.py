"""add game object image path"""

from alembic import op
import sqlalchemy as sa


revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("gameobject", sa.Column("image_path", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("gameobject", "image_path")
