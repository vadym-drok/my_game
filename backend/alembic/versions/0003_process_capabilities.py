"""normalize process requirements and building capabilities"""

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "worktypeitemrequirement",
        sa.Column("work_type_code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("item_code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["item_code"], ["gameitem.code"]),
        sa.ForeignKeyConstraint(["work_type_code"], ["worktypedefinition.code"]),
        sa.PrimaryKeyConstraint("work_type_code", "item_code"),
    )
    op.create_table(
        "buildingworktypecapability",
        sa.Column("building_code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("work_type_code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("output_multiplier", sa.Float(), nullable=True),
        sa.Column("max_workers", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["building_code"], ["buildingdefinition.code"]),
        sa.ForeignKeyConstraint(["work_type_code"], ["worktypedefinition.code"]),
        sa.PrimaryKeyConstraint("building_code", "work_type_code"),
    )
    op.create_table(
        "buildingitemcapability",
        sa.Column("building_code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("item_code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["building_code"], ["buildingdefinition.code"]),
        sa.ForeignKeyConstraint(["item_code"], ["gameitem.code"]),
        sa.PrimaryKeyConstraint("building_code", "item_code"),
    )
    op.create_table(
        "processnationitem",
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("nation_item_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["nation_item_id"], ["nationitem.id"]),
        sa.ForeignKeyConstraint(["process_id"], ["process.id"]),
        sa.PrimaryKeyConstraint("process_id", "nation_item_id"),
    )
    op.execute("""
        INSERT INTO processnationitem (process_id, nation_item_id)
        SELECT process_id, id FROM nationitem WHERE process_id IS NOT NULL
    """)
    op.drop_index("ix_nationitem_process_id", table_name="nationitem")
    op.drop_column("nationitem", "process_id")
    op.execute("""
        INSERT INTO buildingitemcapability (building_code, item_code, capacity)
        SELECT b.code, entry.key, (entry.value #>> '{}')::integer
        FROM buildingdefinition b
        CROSS JOIN LATERAL jsonb_each(b.additional_data::jsonb -> 'boats') AS entry
        WHERE jsonb_typeof(b.additional_data::jsonb -> 'boats') = 'object'
    """)
    op.execute("""
        INSERT INTO buildingworktypecapability (building_code, work_type_code, output_multiplier, max_workers)
        SELECT b.code, entry.key, (entry.value ->> 'multiplier')::float, (entry.value ->> 'workers')::integer
        FROM buildingdefinition b
        CROSS JOIN LATERAL jsonb_each(b.additional_data::jsonb -> 'process') AS entry
        WHERE jsonb_typeof(b.additional_data::jsonb -> 'process') = 'object'
    """)
    op.execute("""
        UPDATE buildingdefinition
        SET additional_data = (additional_data::jsonb - 'boats' - 'process')::json
        WHERE additional_data::jsonb ?| ARRAY['boats', 'process']
    """)
    op.execute("""
        INSERT INTO worktypeitemrequirement (work_type_code, item_code, quantity)
        SELECT 'fishing', 'fishing_boat', 1
        WHERE EXISTS (SELECT 1 FROM worktypedefinition WHERE code = 'fishing')
          AND EXISTS (SELECT 1 FROM gameitem WHERE code = 'fishing_boat')
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.add_column("nationitem", sa.Column("process_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_nationitem_process_id", "nationitem", "process", ["process_id"], ["id"])
    op.create_index("ix_nationitem_process_id", "nationitem", ["process_id"])
    op.execute("""
        UPDATE nationitem item SET process_id = link.process_id
        FROM processnationitem link
        WHERE link.nation_item_id = item.id
    """)
    op.drop_table("processnationitem")
    op.drop_table("buildingitemcapability")
    op.drop_table("buildingworktypecapability")
    op.drop_table("worktypeitemrequirement")
