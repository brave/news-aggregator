"""create FeedLocalesChannel table

Revision ID: c85f87c4196e
Revises: 2a5a15c538e8
Create Date: 2024-03-05 16:07:43.099305+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c85f87c4196e"
down_revision = "2a5a15c538e8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feed_locale_channel",
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
            "feed_locale_id",
            sa.BigInteger,
            sa.ForeignKey("feed_locale.id"),
            nullable=False,
        ),
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
        "lc_idx_channel_id",
        "feed_locale_channel",
        ["channel_id"],
        unique=False,
        if_not_exists=True,
    )
    op.create_index(
        "lc_idx_locale_id",
        "feed_locale_channel",
        ["feed_locale_id"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("lc_idx_locale_id", table_name="feed_locale_channel", if_exists=True)
    op.drop_index("lc_idx_channel_id", table_name="feed_locale_channel", if_exists=True)
    op.drop_table(
        "feed_locale_channel",
        info={"ifexists": True},
    )
