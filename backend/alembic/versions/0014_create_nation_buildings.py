"""create nation buildings"""

from alembic import op
import sqlalchemy as sa

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("nationbuilding", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("nation_id", sa.Integer(), nullable=False), sa.Column("building_definition_id", sa.Integer(), nullable=False), sa.Column("built_at", sa.Date(), nullable=False), sa.ForeignKeyConstraint(["nation_id"], ["nation.id"]), sa.ForeignKeyConstraint(["building_definition_id"], ["buildingdefinition.id"]))
    op.create_index("ix_nationbuilding_nation_id", "nationbuilding", ["nation_id"])
    op.create_index("ix_nationbuilding_building_definition_id", "nationbuilding", ["building_definition_id"])
