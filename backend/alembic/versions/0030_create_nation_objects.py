"""create nation objects"""

from alembic import op
import sqlalchemy as sa


revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "nationobject",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nation_id", sa.Integer(), nullable=False),
        sa.Column("game_object_code", sa.String(), nullable=False),
        sa.Column("built_at", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["nation_id"], ["nation.id"]),
        sa.ForeignKeyConstraint(["game_object_code"], ["gameobject.code"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_nationobject_nation_id"), "nationobject", ["nation_id"], unique=False)
    op.create_index(op.f("ix_nationobject_game_object_code"), "nationobject", ["game_object_code"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_nationobject_game_object_code"), table_name="nationobject")
    op.drop_index(op.f("ix_nationobject_nation_id"), table_name="nationobject")
    op.drop_table("nationobject")
