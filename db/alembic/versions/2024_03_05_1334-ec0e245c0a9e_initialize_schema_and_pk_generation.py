"""initialize_schema_and_pk_generation

Revision ID: ec0e245c0a9e
Revises: 0bbc2ba8f6b7
Create Date: 2024-03-05 13:34:37.480362+00:00

"""

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "ec0e245c0a9e"
down_revision = "0bbc2ba8f6b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
        -- sequence used by our id generation function
        create sequence id_seq;

        create or replace function id_gen(out result bigint) as $$
        declare
            id_epoch bigint := 1588283627191;
            seq_id bigint;
            now_millis bigint;
            app_db_id int := 20;
        begin
            select nextval('id_seq') %% 16384 into seq_id;

            select floor(extract(epoch from clock_timestamp()) * 1000) into now_millis;

            -- we're starting with a bigint so 64 bits
            -- shifting over 22 bits uses the lower 42 bits of our millis timestamp
            -- 42 bits of millis is ~139 years
            result := (now_millis - id_epoch) << 22;

            -- we have 22 bits left
            -- use 8 to store a app/database id (up to 256)
            -- so 22 - 8 = 14 bit shift
            result := result | (app_db_id << 14);

            -- use the remaining 14 bits to store an identifier
            -- that's unique to this millisecond. That's where the
            -- 16384 comes from (2**14) for calculating seq_id.
            result := result | (seq_id);
        end;
        $$ language plpgsql;
    """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DROP SEQUENCE id_seq;"))
