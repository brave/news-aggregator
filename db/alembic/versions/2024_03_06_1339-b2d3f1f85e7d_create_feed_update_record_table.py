"""create feed_update_record table

Revision ID: b2d3f1f85e7d
Revises: 038646fcb595
Create Date: 2024-03-06 13:39:08.865390+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b2d3f1f85e7d"
down_revision = "038646fcb595"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feed_update_record",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column("feed_id", sa.BigInteger, sa.ForeignKey("feed.id"), nullable=False),
        sa.Column("last_build_time", sa.DateTime, nullable=False),
        sa.Column(
            "last_build_timedelta",
            sa.DateTime,
            server_default=sa.func.now(),
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
        "feed_update_record_idx_feed_id",
        "feed_update_record",
        ["feed_id"],
        unique=True,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "feed_update_record_idx_feed_id",
        table_name="feed_update_record",
        if_exists=True,
    )
    op.drop_table(
        "feed_update_record",
        info={"ifexists": True},
    )
