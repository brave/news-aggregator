"""create FeedLocales table

Revision ID: c85f87c4196e
Revises: 2a5a15c538e8
Create Date: 2024-03-05 16:07:43.099305+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c85f87c4196e"
down_revision = "2a5a15c538e8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feed_locales",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column(
            "feed_id",
            sa.BigInteger,
            sa.ForeignKey("feeds.id"),
            nullable=False,
        ),
        sa.Column(
            "locale_id",
            sa.BigInteger,
            sa.ForeignKey("locales.id"),
            nullable=False,
        ),
        sa.Column("rank", sa.Integer, nullable=False),
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
    op.create_index("fl_idx_feed_id", "feed_locales", ["feed_id"], unique=False)
    op.create_index("fl_idx_locale_id", "feed_locales", ["locale_id"], unique=False)


def downgrade() -> None:
    op.drop_index("fl_idx_feed_id", table_name="feedLocales")
    op.drop_index("fl_idx_locale_id", table_name="feedLocales")
    op.drop_table("feed_locales")
