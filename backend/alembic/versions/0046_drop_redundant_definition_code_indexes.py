"""drop redundant definition code indexes"""

from alembic import op


revision = "0046"
down_revision = "0045"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_resource_code", table_name="resource")
    op.drop_index("ix_worktypedefinition_code", table_name="worktypedefinition")
    op.drop_index("ix_buildingdefinition_code", table_name="buildingdefinition")


def downgrade() -> None:
    raise NotImplementedError("Definition key conversion is irreversible")
