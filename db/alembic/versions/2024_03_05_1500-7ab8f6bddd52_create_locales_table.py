"""create locales table

Revision ID: 7ab8f6bddd52
Revises: d027fcb63b7a
Create Date: 2024-03-05 15:00:17.354896+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7ab8f6bddd52"
down_revision = "d027fcb63b7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "locale",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column("name", sa.VARCHAR, nullable=False),
        sa.Column("locale", sa.VARCHAR, nullable=False),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "modified",
            sa.DateTime(timezone=True),
            server_onupdate=sa.func.now(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_locale", "locale", ["locale"], unique=True)


def downgrade() -> None:
    op.drop_index("idx_locale", table_name="locale", if_exists=True)
    op.drop_table("locale")
