"""use definition codes as keys"""

from alembic import op
import sqlalchemy as sa


revision = "0045"
down_revision = "0044"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("nationresource", sa.Column("resource_code", sa.String(), nullable=True))
    op.execute("UPDATE nationresource AS nr SET resource_code = r.code FROM resource AS r WHERE r.id = nr.resource_id")
    op.alter_column("nationresource", "resource_code", nullable=False)
    op.create_index("ix_nationresource_resource_code", "nationresource", ["resource_code"])
    op.create_unique_constraint("uq_nationresource_nation_resource_code", "nationresource", ["nation_id", "resource_code"])
    op.drop_constraint("nationresource_nation_id_resource_id_key", "nationresource", type_="unique")
    op.drop_constraint("nationresource_resource_id_fkey", "nationresource", type_="foreignkey")
    op.drop_index("ix_nationresource_resource_id", table_name="nationresource")
    op.drop_column("nationresource", "resource_id")

    op.add_column("nationbuilding", sa.Column("building_code", sa.String(), nullable=True))
    op.execute("UPDATE nationbuilding AS nb SET building_code = b.code FROM buildingdefinition AS b WHERE b.id = nb.building_definition_id")
    op.alter_column("nationbuilding", "building_code", nullable=False)
    op.create_index("ix_nationbuilding_building_code", "nationbuilding", ["building_code"])
    op.drop_constraint("nationbuilding_building_definition_id_fkey", "nationbuilding", type_="foreignkey")
    op.drop_index("ix_nationbuilding_building_definition_id", table_name="nationbuilding")
    op.drop_column("nationbuilding", "building_definition_id")
    op.execute("UPDATE process AS p SET details = (p.details::jsonb - 'building_definition_id') || jsonb_build_object('building_code', b.code), outputs = jsonb_set(p.outputs::jsonb, '{building}', jsonb_build_object('code', b.code, 'name', b.name))::json FROM buildingdefinition AS b WHERE (p.details ->> 'building_definition_id')::integer = b.id")

    op.add_column("process", sa.Column("work_type_code", sa.String(), nullable=True))
    op.execute("UPDATE process AS p SET work_type_code = w.code FROM worktypedefinition AS w WHERE w.id = p.work_type_id")
    op.alter_column("process", "work_type_code", nullable=False)
    op.create_index("ix_process_work_type_code", "process", ["work_type_code"])
    op.drop_constraint("fk_process_work_type_id", "process", type_="foreignkey")
    op.drop_index("ix_process_work_type_id", table_name="process")
    op.drop_column("process", "work_type_id")
    op.alter_column("process", "work_type_code", new_column_name="work_type")

    op.drop_constraint("locationbuildingdefinition_building_code_fkey", "locationbuildingdefinition", type_="foreignkey")
    op.drop_constraint("buildingdefinition_pkey", "buildingdefinition", type_="primary")
    op.create_primary_key("buildingdefinition_pkey", "buildingdefinition", ["code"])
    op.drop_constraint("buildingdefinition_code_key", "buildingdefinition", type_="unique")
    op.create_foreign_key("fk_nationbuilding_building_code", "nationbuilding", "buildingdefinition", ["building_code"], ["code"])
    op.create_foreign_key("locationbuildingdefinition_building_code_fkey", "locationbuildingdefinition", "buildingdefinition", ["building_code"], ["code"])
    op.drop_column("buildingdefinition", "id")

    op.drop_constraint("locationworktype_work_type_code_fkey", "locationworktype", type_="foreignkey")
    op.drop_constraint("worktypedefinition_pkey", "worktypedefinition", type_="primary")
    op.create_primary_key("worktypedefinition_pkey", "worktypedefinition", ["code"])
    op.drop_constraint("worktypedefinition_code_key", "worktypedefinition", type_="unique")
    op.create_foreign_key("fk_process_work_type_code", "process", "worktypedefinition", ["work_type"], ["code"])
    op.create_foreign_key("locationworktype_work_type_code_fkey", "locationworktype", "worktypedefinition", ["work_type_code"], ["code"])
    op.drop_column("worktypedefinition", "id")

    op.drop_constraint("resource_pkey", "resource", type_="primary")
    op.create_primary_key("resource_pkey", "resource", ["code"])
    op.drop_constraint("resource_code_key", "resource", type_="unique")
    op.create_foreign_key("fk_nationresource_resource_code", "nationresource", "resource", ["resource_code"], ["code"])
    op.drop_column("resource", "id")


def downgrade() -> None:
    raise NotImplementedError("Definition key conversion is irreversible")
