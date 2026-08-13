"""link buildings to locations"""

from alembic import op
import sqlalchemy as sa


revision = "0038"
down_revision = "0037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "locationbuildingdefinition",
        sa.Column("location_code", sa.String(), nullable=False),
        sa.Column("building_code", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["location_code"], ["location.code"]),
        sa.ForeignKeyConstraint(["building_code"], ["buildingdefinition.code"]),
        sa.PrimaryKeyConstraint("location_code", "building_code"),
    )
    op.add_column("nationbuilding", sa.Column("location_code", sa.String(), nullable=True))
    op.create_foreign_key("fk_nationbuilding_location_code", "nationbuilding", "location", ["location_code"], ["code"])
    op.create_index("ix_nationbuilding_location_code", "nationbuilding", ["location_code"])


def downgrade() -> None:
    op.drop_index("ix_nationbuilding_location_code", table_name="nationbuilding")
    op.drop_constraint("fk_nationbuilding_location_code", "nationbuilding", type_="foreignkey")
    op.drop_column("nationbuilding", "location_code")
    op.drop_table("locationbuildingdefinition")
