from alembic_utils import pg_trigger

trg_ensure_org_has_building = pg_trigger.PGTrigger(
    schema='public',
    signature='trg_ensure_org_has_building',
    on_entity='public.organizations',
    is_constraint=True,
    definition="""
        AFTER INSERT OR UPDATE ON organizations
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW
        EXECUTE FUNCTION ensure_org_has_building();
    """,
)

trg_specialization_depth_check = pg_trigger.PGTrigger(
    schema='public',
    signature='trg_specialization_depth_check',
    on_entity='public.specializations',
    definition="""
        BEFORE INSERT OR UPDATE ON specializations
        FOR EACH ROW
        EXECUTE FUNCTION check_specialization_depth();
    """,
)

trg_specialization_update_search_vector = pg_trigger.PGTrigger(
    schema='public',
    signature='trg_specialization_update_search_vector',
    on_entity='public.specializations',
    definition="""
        BEFORE INSERT OR UPDATE ON specializations
        FOR EACH ROW
        EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.english', name);
    """,
)

trg_building_update_search_vector = pg_trigger.PGTrigger(
    schema='public',
    signature='trg_building_update_search_vector',
    on_entity='public.buildings',
    definition="""
        BEFORE INSERT OR UPDATE ON buildings
        FOR EACH ROW
        EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.english', address);
    """,
)
