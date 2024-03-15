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
        "locale_channel",
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
            sa.ForeignKey("channel.id"),
            nullable=False,
        ),
        sa.Column(
            "locale_id",
            sa.BigInteger,
            sa.ForeignKey("locale.id"),
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
    op.create_index("lc_idx_channel_id", "locale_channel", ["channel_id"], unique=False)
    op.create_index("lc_idx_locale_id", "locale_channel", ["locale_id"], unique=False)


def downgrade() -> None:
    op.drop_index("lc_idx_locale_id", table_name="locale_channel", if_exists=True)
    op.drop_index("lc_idx_channel_id", table_name="locale_channel", if_exists=True)
    op.drop_table("locale_channel")
