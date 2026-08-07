"""create game items"""

from alembic import op
import sqlalchemy as sa

revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("gameitem", sa.Column("code", sa.String(), primary_key=True), sa.Column("name", sa.String(), nullable=False), sa.Column("image_path", sa.String(), nullable=True), sa.Column("visual_type", sa.String(), nullable=False), sa.Column("description", sa.String(), nullable=False), sa.Column("worker_days", sa.Integer(), nullable=False), sa.Column("construction_resources", sa.JSON(), nullable=False), sa.Column("additional_data", sa.JSON(), nullable=False), sa.Column("max_workers", sa.Integer(), nullable=False), sa.Column("outputs", sa.JSON(), nullable=False))


def downgrade() -> None:
    op.drop_table("gameitem")
