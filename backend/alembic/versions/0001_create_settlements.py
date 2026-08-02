"""create game tables"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "settlement",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("population", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("food", sa.Float(), nullable=False),
        sa.Column("wood", sa.Integer(), nullable=False),
        sa.Column("stone", sa.Integer(), nullable=False),
        sa.Column("influence", sa.Integer(), nullable=False),
        sa.Column("housing_capacity", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "process",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("settlement_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("work_type", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("assigned_workers", sa.Integer(), nullable=False),
        sa.Column("required_worker_days", sa.Integer(), nullable=True),
        sa.Column("completed_worker_days", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.Date(), nullable=False),
        sa.Column("completed_at", sa.Date(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["settlement_id"], ["settlement.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_process_settlement_id", "process", ["settlement_id"])

    op.create_table(
        "dayreport",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("settlement_id", sa.Integer(), nullable=False),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column("population", sa.Integer(), nullable=False),
        sa.Column("food", sa.Float(), nullable=False),
        sa.Column("wood", sa.Integer(), nullable=False),
        sa.Column("stone", sa.Integer(), nullable=False),
        sa.Column("influence", sa.Integer(), nullable=False),
        sa.Column("food_produced", sa.Float(), nullable=False),
        sa.Column("food_consumed", sa.Float(), nullable=False),
        sa.Column("workers_summary", sa.JSON(), nullable=False),
        sa.Column("processes_summary", sa.JSON(), nullable=False),
        sa.Column("notes", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["settlement_id"], ["settlement.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("settlement_id", "report_date"),
    )
    op.create_index("ix_dayreport_settlement_id", "dayreport", ["settlement_id"])


def downgrade() -> None:
    op.drop_table("settlement")
