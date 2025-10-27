"""Init functions and tirggers

Revision ID: funcs_trgs
Revises: init
Create Date: 2025-10-27 19:54:05.933309

"""

from collections.abc import Sequence

from alembic import op
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

# revision identifiers, used by Alembic.
revision: str = 'funcs_trgs'
down_revision: str | Sequence[str] | None = 'init'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    public_check_specialization_depth = PGFunction(
        schema='public',
        signature='check_specialization_depth()',
        definition="RETURNS TRIGGER AS $$\n        DECLARE\n            current_parent_id INT;\n            depth INT := 1;\n        BEGIN\n            current_parent_id := NEW.parent_id;\n\n            WHILE current_parent_id IS NOT NULL LOOP\n                depth := depth + 1;\n                IF depth > 3 THEN\n                    RAISE EXCEPTION 'Specialization nesting level cannot exceed 3' USING ERRCODE = 'P0001';\n                END IF;\n\n                SELECT parent_id INTO current_parent_id FROM specializations WHERE id = current_parent_id;\n            END LOOP;\n\n            RETURN NEW;\n        END;\n        $$ LANGUAGE plpgsql",
    )
    op.create_entity(public_check_specialization_depth)

    public_ensure_org_has_building = PGFunction(
        schema='public',
        signature='ensure_org_has_building()',
        definition="RETURNS TRIGGER AS $$\n        BEGIN\n            IF NOT EXISTS (\n                SELECT 1\n                FROM organization_buildings ob\n                WHERE ob.organization_id = NEW.id\n            ) THEN\n                RAISE EXCEPTION 'Organization (id=%) must have at least one building', NEW.id;\n            END IF;\n            RETURN NEW;\n        END;\n        $$ LANGUAGE plpgsql",
    )
    op.create_entity(public_ensure_org_has_building)

    public_specializations_trg_specialization_depth_check = PGTrigger(
        schema='public',
        signature='trg_specialization_depth_check',
        on_entity='public.specializations',
        is_constraint=False,
        definition='BEFORE INSERT OR UPDATE ON specializations\n        FOR EACH ROW\n        EXECUTE FUNCTION check_specialization_depth()',
    )
    op.create_entity(public_specializations_trg_specialization_depth_check)

    public_organizations_trg_ensure_org_has_building = PGTrigger(
        schema='public',
        signature='trg_ensure_org_has_building',
        on_entity='public.organizations',
        is_constraint=True,
        definition='AFTER INSERT OR UPDATE ON organizations\n        DEFERRABLE INITIALLY DEFERRED\n        FOR EACH ROW\n        EXECUTE FUNCTION ensure_org_has_building()',
    )
    op.create_entity(public_organizations_trg_ensure_org_has_building)


def downgrade() -> None:
    """Downgrade schema."""
    public_organizations_trg_ensure_org_has_building = PGTrigger(
        schema='public',
        signature='trg_ensure_org_has_building',
        on_entity='public.organizations',
        is_constraint=True,
        definition='AFTER INSERT OR UPDATE ON organizations\n        DEFERRABLE INITIALLY DEFERRED\n        FOR EACH ROW\n        EXECUTE FUNCTION ensure_org_has_building()',
    )
    op.drop_entity(public_organizations_trg_ensure_org_has_building)

    public_specializations_trg_specialization_depth_check = PGTrigger(
        schema='public',
        signature='trg_specialization_depth_check',
        on_entity='public.specializations',
        is_constraint=False,
        definition='BEFORE INSERT OR UPDATE ON specializations\n        FOR EACH ROW\n        EXECUTE FUNCTION check_specialization_depth()',
    )
    op.drop_entity(public_specializations_trg_specialization_depth_check)

    public_ensure_org_has_building = PGFunction(
        schema='public',
        signature='ensure_org_has_building()',
        definition="RETURNS TRIGGER AS $$\n        BEGIN\n            IF NOT EXISTS (\n                SELECT 1\n                FROM organization_buildings ob\n                WHERE ob.organization_id = NEW.id\n            ) THEN\n                RAISE EXCEPTION 'Organization (id=%) must have at least one building', NEW.id;\n            END IF;\n            RETURN NEW;\n        END;\n        $$ LANGUAGE plpgsql",
    )
    op.drop_entity(public_ensure_org_has_building)

    public_check_specialization_depth = PGFunction(
        schema='public',
        signature='check_specialization_depth()',
        definition="RETURNS TRIGGER AS $$\n        DECLARE\n            current_parent_id INT;\n            depth INT := 1;\n        BEGIN\n            current_parent_id := NEW.parent_id;\n\n            WHILE current_parent_id IS NOT NULL LOOP\n                depth := depth + 1;\n                IF depth > 3 THEN\n                    RAISE EXCEPTION 'Specialization nesting level cannot exceed 3' USING ERRCODE = 'P0001';\n                END IF;\n\n                SELECT parent_id INTO current_parent_id FROM specializations WHERE id = current_parent_id;\n            END LOOP;\n\n            RETURN NEW;\n        END;\n        $$ LANGUAGE plpgsql",
    )
    op.drop_entity(public_check_specialization_depth)
