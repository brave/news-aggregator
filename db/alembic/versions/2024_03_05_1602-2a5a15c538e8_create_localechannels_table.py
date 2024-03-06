"""create localeChannels table

Revision ID: 2a5a15c538e8
Revises: 1f9b63c5cb07
Create Date: 2024-03-05 16:02:51.770998+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a5a15c538e8"
down_revision = "1f9b63c5cb07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "locales_channels",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column(
            "channel_id",
            sa.BigInteger,
            sa.ForeignKey("channels.id"),
            nullable=False,
        ),
        sa.Column(
            "locale_id",
            sa.BigInteger,
            sa.ForeignKey("locales.id"),
            nullable=False,
        ),
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
    op.create_index(
        "lc_idx_channel_id", "locales_channels", ["channel_id"], unique=False
    )
    op.create_index("lc_idx_locale_id", "locales_channels", ["locale_id"], unique=False)


def downgrade() -> None:
    op.drop_index("lc_idx_locale_id", table_name="localeChannels")
    op.drop_index("lc_idx_channel_id", table_name="localeChannels")
    op.drop_table("locales_channels")
