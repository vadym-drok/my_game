"""add process outputs"""

from alembic import op
import sqlalchemy as sa


revision = "0033"
down_revision = "0032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("process", sa.Column("outputs", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")))
    op.execute("UPDATE process AS p SET outputs = json_build_object('building', json_build_object('id', b.id, 'name', b.name)) FROM buildingdefinition AS b WHERE (p.details ->> 'building_definition_id')::integer = b.id")
    op.alter_column("process", "outputs", server_default=None)


def downgrade() -> None:
    op.drop_column("process", "outputs")
