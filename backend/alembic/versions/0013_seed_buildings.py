"""seed building definitions"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None

def upgrade() -> None:
    data = json.loads((Path(__file__).parents[2] / "data" / "raw_data.json").read_text())
    table = sa.table("buildingdefinition", sa.column("code", sa.String()), sa.column("name", sa.String()), sa.column("building_type", sa.String()), sa.column("capacity", sa.Integer()))
    op.bulk_insert(table, data["buildings"])
