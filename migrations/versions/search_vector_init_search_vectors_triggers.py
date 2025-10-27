"""Init search vectors triggers

Revision ID: search_vector
Revises: funcs_trgs
Create Date: 2025-10-27 22:34:21.201074

"""

from collections.abc import Sequence

from alembic import op
from alembic_utils.pg_trigger import PGTrigger

# revision identifiers, used by Alembic.
revision: str = 'search_vector'
down_revision: str | Sequence[str] | None = 'funcs_trgs'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    public_buildings_trg_building_update_search_vector = PGTrigger(
        schema='public',
        signature='trg_building_update_search_vector',
        on_entity='public.buildings',
        is_constraint=False,
        definition="BEFORE INSERT OR UPDATE ON buildings\n        FOR EACH ROW\n        EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.english', address)",
    )
    op.create_entity(public_buildings_trg_building_update_search_vector)

    public_organizations_trg_organizations_update_search_vector = PGTrigger(
        schema='public',
        signature='trg_organizations_update_search_vector',
        on_entity='public.organizations',
        is_constraint=False,
        definition="BEFORE INSERT OR UPDATE ON organizations\n        FOR EACH ROW\n        EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.english', name)",
    )
    op.create_entity(public_organizations_trg_organizations_update_search_vector)



def downgrade() -> None:
    """Downgrade schema."""
    public_organizations_trg_organizations_update_search_vector = PGTrigger(
        schema='public',
        signature='trg_organizations_update_search_vector',
        on_entity='public.organizations',
        is_constraint=False,
        definition="BEFORE INSERT OR UPDATE ON organizations\n        FOR EACH ROW\n        EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.english', name)",
    )
    op.drop_entity(public_organizations_trg_organizations_update_search_vector)

    public_buildings_trg_building_update_search_vector = PGTrigger(
        schema='public',
        signature='trg_building_update_search_vector',
        on_entity='public.buildings',
        is_constraint=False,
        definition="BEFORE INSERT OR UPDATE ON buildings\n        FOR EACH ROW\n        EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.english', address)",
    )
    op.drop_entity(public_buildings_trg_building_update_search_vector)