"""move resources to inventory"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    raw_data = json.loads(
        (Path(__file__).parents[2] / "data" / "raw_data.json").read_text()
    )
    resource = sa.table(
        "resource",
        sa.column("code", sa.String()),
        sa.column("name", sa.String()),
        sa.column("storage_coefficient", sa.Float()),
    )
    op.bulk_insert(resource, raw_data["resources"])

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
    op.execute("""
        INSERT INTO nationresource (nation_id, resource_id, amount)
        SELECT nation.id, resource.id,
            CASE resource.code
                WHEN 'general_points' THEN nation.general_points
                WHEN 'food' THEN nation.food
                WHEN 'wood' THEN nation.wood
                WHEN 'stone' THEN nation.stone
            END
        FROM nation CROSS JOIN resource
    """)

    op.add_column(
        "dayreport",
        sa.Column("resources", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.execute("""
        UPDATE dayreport SET resources = json_build_object(
            'general_points', json_build_object('amount', general_points, 'spending', 0, 'income', 0),
            'food', json_build_object('amount', food, 'spending', food_consumed, 'income', food_produced),
            'wood', json_build_object('amount', wood, 'spending', 0, 'income', 0),
            'stone', json_build_object('amount', stone, 'spending', 0, 'income', 0)
        )
    """)
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
