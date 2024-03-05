"""create feeds table

Revision ID: 7ab8f6bddd52
Revises: d027fcb63b7a
Create Date: 2024-03-05 15:00:17.354896+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7ab8f6bddd52"
down_revision = "d027fcb63b7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news.feeds",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            default=sa.text("news.id_gen()"),
        ),
        sa.Column("name", sa.VARCHAR, nullable=False),
        sa.Column("url", sa.VARCHAR, nullable=False),
        sa.Column("url_hash", sa.VARCHAR, nullable=False, unique=True),
        sa.Column(
            "publisher_id",
            sa.BigInteger,
            sa.ForeignKey("news.publishers.id"),
            nullable=False,
        ),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("category", sa.VARCHAR, nullable=False),
        sa.Column(
            "locale_id", sa.BigInteger, sa.ForeignKey("news.locales.id"), nullable=False
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
    )
    op.create_index("idx_url_hash", "news.feeds", ["url_hash"], unique=True)
    op.create_index("idx_url", "news.feeds", ["url"], unique=True)
    op.create_index("idx_publisher_id", "news.feeds", ["publisher_id"], unique=False)
    op.create_index("idx_locale_id", "news.feeds", ["locale_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_locale_id", table_name="news.feeds")
    op.drop_index("idx_publisher_id", table_name="news.feeds")
    op.drop_index("idx_url", table_name="news.feeds")
    op.drop_index("idx_url_hash", table_name="news.feeds")
    op.drop_table("news.feeds")
