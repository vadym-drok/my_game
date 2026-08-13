"""link processes to locations"""

from alembic import op
import sqlalchemy as sa


revision = "0036"
down_revision = "0035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "locationworktype",
        sa.Column("location_code", sa.String(), nullable=False),
        sa.Column("work_type_code", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["location_code"], ["location.code"]),
        sa.ForeignKeyConstraint(["work_type_code"], ["worktypedefinition.code"]),
        sa.PrimaryKeyConstraint("location_code", "work_type_code"),
    )
    op.add_column("process", sa.Column("location_code", sa.String(), nullable=True))
    op.create_foreign_key("fk_process_location_code", "process", "location", ["location_code"], ["code"])
    op.create_index("ix_process_location_code", "process", ["location_code"])


def downgrade() -> None:
    op.drop_index("ix_process_location_code", table_name="process")
    op.drop_constraint("fk_process_location_code", "process", type_="foreignkey")
    op.drop_column("process", "location_code")
    op.drop_table("locationworktype")
