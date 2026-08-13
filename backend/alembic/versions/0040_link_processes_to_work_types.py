"""link processes to work types"""

from alembic import op
import sqlalchemy as sa


revision = "0040"
down_revision = "0039"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("process", sa.Column("work_type_id", sa.Integer(), nullable=True))
    op.execute("UPDATE process AS p SET work_type_id = w.id FROM worktypedefinition AS w WHERE p.work_type = w.code")
    op.alter_column("process", "work_type_id", nullable=False)
    op.create_foreign_key("fk_process_work_type_id", "process", "worktypedefinition", ["work_type_id"], ["id"])
    op.create_index("ix_process_work_type_id", "process", ["work_type_id"])
    op.drop_column("process", "work_type")


def downgrade() -> None:
    op.add_column("process", sa.Column("work_type", sa.String(), nullable=True))
    op.execute("UPDATE process AS p SET work_type = w.code FROM worktypedefinition AS w WHERE p.work_type_id = w.id")
    op.alter_column("process", "work_type", nullable=False)
    op.drop_index("ix_process_work_type_id", table_name="process")
    op.drop_constraint("fk_process_work_type_id", "process", type_="foreignkey")
    op.drop_column("process", "work_type_id")
