"""create personal tasks"""

from alembic import op
import sqlalchemy as sa


revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "personaltask",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nation_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("reward", sa.Integer(), nullable=False),
        sa.Column("task_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["nation_id"], ["nation.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_personaltask_nation_id"), "personaltask", ["nation_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_personaltask_nation_id"), table_name="personaltask")
    op.drop_table("personaltask")
