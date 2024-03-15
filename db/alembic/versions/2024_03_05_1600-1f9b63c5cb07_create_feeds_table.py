"""create feeds table

Revision ID: 1f9b63c5cb07
Revises: 37a183c90085
Create Date: 2024-03-05 16:00:07.328230+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f9b63c5cb07"
down_revision = "37a183c90085"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feed",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column("url", sa.VARCHAR, nullable=False),
        sa.Column("url_hash", sa.VARCHAR, nullable=False),
        sa.Column(
            "publisher_id",
            sa.BigInteger,
            sa.ForeignKey("publisher.id"),
            nullable=False,
        ),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("category", sa.VARCHAR, nullable=False),
        sa.Column(
            "locale_id", sa.BigInteger, sa.ForeignKey("locale.id"), nullable=False
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
    op.create_index("feed_idx_url_hash", "feed", ["url_hash"], unique=True)
    op.create_index("feed_idx_url", "feed", ["url"], unique=True)
    op.create_index("idx_publisher_id", "feed", ["publisher_id"], unique=False)
    op.create_index("idx_locale_id", "feed", ["locale_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_locale_id", table_name="feed", if_exists=True)
    op.drop_index("idx_publisher_id", table_name="feed", if_exists=True)
    op.drop_index("feed_idx_url", table_name="feed", if_exists=True)
    op.drop_index("feed_idx_url_hash", table_name="feed", if_exists=True)
    op.drop_table("feed")
