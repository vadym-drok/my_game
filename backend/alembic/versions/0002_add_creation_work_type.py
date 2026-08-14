"""add creation work type"""

from alembic import op


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO worktypedefinition (code, name, intensity, mode, outputs, image_path)
        VALUES ('creation', 'Creation', 'LIGHT', 'finite', '{}', '/images/work-types/creation.webp')
        ON CONFLICT (code) DO NOTHING
    """)


def downgrade() -> None:
    pass
