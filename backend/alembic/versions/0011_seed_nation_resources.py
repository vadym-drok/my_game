"""seed nation resources"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    raw_data = json.loads(
        (Path(__file__).parents[2] / "data" / "raw_data.json").read_text()
    )
    amounts = raw_data["nation"].get("resources", {})
    bind = op.get_bind()
    nation_id = bind.execute(sa.text("SELECT id FROM nation ORDER BY id LIMIT 1")).scalar_one()
    resource_ids = dict(bind.execute(sa.text("SELECT code, id FROM resource")).all())
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
                "resource_id": resource_id,
                "amount": amounts.get(code, 0),
            }
            for code, resource_id in resource_ids.items()
        ],
    )
