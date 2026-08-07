"""replace process name with description and add other work type"""

from alembic import op
import sqlalchemy as sa


revision = "0032"
down_revision = "0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("process", sa.Column("description", sa.String(), nullable=False, server_default=""))
    op.execute("UPDATE process SET description = name")
    op.alter_column("process", "description", server_default=None)
    op.drop_column("process", "name")
    op.execute("INSERT INTO worktypedefinition (code, name, intensity, mode, outputs, image_path) VALUES ('other', 'Other', 'BASE', 'continuous', '{}'::json, NULL) ON CONFLICT (code) DO NOTHING")


def downgrade() -> None:
    op.delete(sa.table("worktypedefinition", sa.column("code", sa.String())), sa.column("code", sa.String()) == "other")
    op.add_column("process", sa.Column("name", sa.String(), nullable=False, server_default=""))
    op.alter_column("process", "name", server_default=None)
    op.drop_column("process", "description")
