"""Add organization building required constraint

Revision ID: add_org_bldg_req
Revises: 4ee07a7b7ea2
Create Date: 2025-10-24 10:00:00.000000

"""
from typing import Sequence

# Note: keeping alembic and typing imports only
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'add_org_bldg_req'
down_revision: str | Sequence[str] | None = '4ee07a7b7ea2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION ensure_org_has_building()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM organization_buildings ob
                WHERE ob.organization_id = NEW.id
            ) THEN
                RAISE EXCEPTION 'Organization (id=%) must have at least one building', NEW.id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE CONSTRAINT TRIGGER trg_ensure_org_has_building
        AFTER INSERT OR UPDATE ON organizations
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW
        EXECUTE FUNCTION ensure_org_has_building();
    """)


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER IF EXISTS trg_ensure_org_has_building ON organizations;
    """)
    op.execute("""
        DROP FUNCTION IF EXISTS ensure_org_has_building;
    """)
