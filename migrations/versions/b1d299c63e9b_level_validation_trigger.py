"""Level validation trigger

Revision ID: b1d299c63e9b
Revises: 205506c1fa26
Create Date: 2025-10-22 16:05:53.494624

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b1d299c63e9b'
down_revision: str | Sequence[str] | None = 'add_org_bldg_req'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION check_specialization_depth()
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
    """)

    op.execute("""
        CREATE TRIGGER specialization_depth_check
        BEFORE INSERT OR UPDATE ON specializations
        FOR EACH ROW
        EXECUTE FUNCTION check_specialization_depth();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS specialization_depth_check ON specializations;")
    op.execute("DROP FUNCTION IF EXISTS check_specialization_depth;")
