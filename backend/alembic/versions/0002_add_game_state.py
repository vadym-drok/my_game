"""add game state"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("settlement", sa.Column("current_day", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("settlement", sa.Column("food", sa.Float(), nullable=False, server_default="0"))
    op.add_column("settlement", sa.Column("wood", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("settlement", sa.Column("stone", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("settlement", sa.Column("influence", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("settlement", sa.Column("housing_capacity", sa.Integer(), nullable=False, server_default="0"))
    op.create_table(
        "dayreport",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("settlement_id", sa.Integer(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("population", sa.Integer(), nullable=False),
        sa.Column("food", sa.Float(), nullable=False),
        sa.Column("wood", sa.Integer(), nullable=False),
        sa.Column("stone", sa.Integer(), nullable=False),
        sa.Column("influence", sa.Integer(), nullable=False),
        sa.Column("food_produced", sa.Float(), nullable=False),
        sa.Column("food_consumed", sa.Float(), nullable=False),
        sa.Column("workers_summary", sa.JSON(), nullable=False),
        sa.Column("notes", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["settlement_id"], ["settlement.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dayreport_settlement_id", "dayreport", ["settlement_id"])


def downgrade() -> None:
    op.drop_index("ix_dayreport_settlement_id", table_name="dayreport")
    op.drop_table("dayreport")
    for column in ("housing_capacity", "influence", "stone", "wood", "food", "current_day"):
        op.drop_column("settlement", column)
