from alembic_utils import pg_function

ensure_org_has_building = pg_function.PGFunction(
    schema='public',
    signature='ensure_org_has_building()',
    definition="""
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
    """,
)

check_specialization_depth = pg_function.PGFunction(
    schema='public',
    signature='check_specialization_depth()',
    definition="""
        RETURNS TRIGGER AS $$
        DECLARE
            current_parent_id INT;
            depth INT := 1;
        BEGIN
            current_parent_id := NEW.parent_id;

            WHILE current_parent_id IS NOT NULL LOOP
                depth := depth + 1;
                IF depth > 3 THEN
                    RAISE EXCEPTION 'Specialization nesting level cannot exceed 3' USING ERRCODE = 'P0001';
                END IF;

                SELECT parent_id INTO current_parent_id FROM specializations WHERE id = current_parent_id;
            END LOOP;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
""",
)
