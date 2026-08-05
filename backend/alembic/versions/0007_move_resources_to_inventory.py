"""move resources to inventory"""

from alembic import op
import sqlalchemy as sa


revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "nationresource",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nation_id", sa.Integer(), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["nation_id"], ["nation.id"]),
        sa.ForeignKeyConstraint(["resource_id"], ["resource.id"]),
        sa.UniqueConstraint("nation_id", "resource_id"),
    )
    op.create_index("ix_nationresource_nation_id", "nationresource", ["nation_id"])
    op.create_index("ix_nationresource_resource_id", "nationresource", ["resource_id"])
    op.add_column(
        "dayreport",
        sa.Column("resources", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.alter_column(
        "nationlog",
        "amount",
        type_=sa.Float(),
        postgresql_using="amount::double precision",
    )
    op.drop_column("nation", "food")
    op.drop_column("nation", "general_points")
    op.drop_column("nation", "wood")
    op.drop_column("nation", "stone")
    op.drop_column("dayreport", "food")
    op.drop_column("dayreport", "general_points")
    op.drop_column("dayreport", "wood")
    op.drop_column("dayreport", "stone")
    op.drop_column("dayreport", "food_produced")
    op.drop_column("dayreport", "food_consumed")
