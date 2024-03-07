"""create feed lastbuild table

Revision ID: b2d3f1f85e7d
Revises: 038646fcb595
Create Date: 2024-03-06 13:39:08.865390+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2d3f1f85e7d"
down_revision = "038646fcb595"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feed_lastbuild",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column("feed_id", sa.BigInteger, sa.ForeignKey("feeds.id"), nullable=False),
        sa.Column("last_build_timedate", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "last_build_timedalta",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
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
        "feed_lastbuild_idx_feed_id", "feed_lastbuild", ["feed_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index(
        "feed_lastbuild_idx_feed_id", table_name="feed_lastbuild", if_exists=True
    )
    op.drop_table("feed_lastbuild")
