"""Add organization building required constraint

Revision ID: add_org_bldg_req
Revises: 205506c1fa26
Create Date: 2025-10-24 10:00:00.000000

"""
from typing import Sequence

# Note: keeping alembic and typing imports only
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'add_org_bldg_req'
down_revision: str | Sequence[str] | None = '205506c1fa26'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add a check constraint that ensures each organization has at least one building
    # by checking existence in organization_buildings
    op.execute("""
        ALTER TABLE organizations ADD CONSTRAINT chk_organization_has_building
        CHECK (
            id IN (
                SELECT organization_id 
                FROM organization_buildings
            )
        );
    """)


def downgrade() -> None:
    # Remove the check constraint
    op.execute("""
        ALTER TABLE organizations DROP CONSTRAINT chk_organization_has_building;
    """)