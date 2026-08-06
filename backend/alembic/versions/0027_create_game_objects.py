"""create game objects"""

from alembic import op
import sqlalchemy as sa


revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gameobject",
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("worker_days", sa.Integer(), nullable=False),
        sa.Column("construction_resources", sa.JSON(), nullable=False),
        sa.Column("additional_data", sa.JSON(), nullable=False),
        sa.Column("max_workers", sa.Integer(), nullable=False),
        sa.Column("outputs", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("code"),
    )


def downgrade() -> None:
    op.drop_table("gameobject")
