"""seed raw data"""

import json
from datetime import date
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    raw_data = json.loads(
        (Path(__file__).parents[2] / "data" / "raw_data.json").read_text()
    )
    work_type = sa.table(
        "worktypedefinition",
        sa.column("code", sa.String()),
        sa.column("name", sa.String()),
        sa.column("intensity", sa.String()),
        sa.column("mode", sa.String()),
        sa.column("outputs", sa.JSON()),
    )
    op.bulk_insert(work_type, raw_data["work_types"])

    nation_data = raw_data["nation"]
    nation = sa.table(
        "nation",
        sa.column("name", sa.String()),
        sa.column("population", sa.Integer()),
        sa.column("start_date", sa.Date()),
        sa.column("influence", sa.Integer()),
        sa.column("housing_capacity", sa.Integer()),
    )
    op.bulk_insert(
        nation,
        [{
            "name": nation_data["name"],
            "population": nation_data["population"],
            "start_date": date.today(),
            "influence": nation_data["influence"],
            "housing_capacity": nation_data["housing_capacity"],
        }],
    )
    bind = op.get_bind()
    nation_id = bind.execute(sa.text("SELECT id FROM nation ORDER BY id LIMIT 1")).scalar_one()
    resource_ids = dict(
        bind.execute(sa.text("SELECT code, id FROM resource")).all()
    )
    nation_resource = sa.table(
        "nationresource",
        sa.column("nation_id", sa.Integer()),
        sa.column("resource_id", sa.Integer()),
        sa.column("amount", sa.Float()),
    )
    op.bulk_insert(
        nation_resource,
        [
            {
                "nation_id": nation_id,
                "resource_id": resource_ids[code],
                "amount": amount,
            }
            for code, amount in nation_data.items()
            if code in resource_ids
        ],
    )
