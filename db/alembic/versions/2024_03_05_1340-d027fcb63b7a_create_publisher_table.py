"""create publisher table

Revision ID: d027fcb63b7a
Revises: ec0e245c0a9e
Create Date: 2024-03-05 13:40:21.010447+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d027fcb63b7a"
down_revision = "ec0e245c0a9e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "publisher",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column("url", sa.VARCHAR, nullable=False),
        sa.Column("favicon_url", sa.VARCHAR, default=None, nullable=True),
        sa.Column("cover_url", sa.VARCHAR, server_default=None, nullable=True),
        sa.Column("background_color", sa.VARCHAR, server_default=None, nullable=True),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("score", sa.Float, default=0.0, nullable=False),
        sa.Column(
            "created",
            sa.DateTime,
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "modified",
            sa.DateTime,
            server_onupdate=sa.func.now(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        info={"ifexists": True},
    )
    op.create_index(
        "pub_idx_url", "publisher", ["url"], unique=True, if_not_exists=True
    )


def downgrade() -> None:
    op.drop_index("pub_idx_url", table_name="publisher", if_exists=True)
    op.drop_index("pub_idx_url_hash", table_name="publisher", if_exists=True)
    op.drop_table(
        "publisher",
        info={"ifexists": True},
    )
