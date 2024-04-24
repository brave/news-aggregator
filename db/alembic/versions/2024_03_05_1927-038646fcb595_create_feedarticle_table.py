"""create feedArticle table

Revision ID: 038646fcb595
Revises: 6e139e4d2c17
Create Date: 2024-03-05 19:27:24.349042+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "038646fcb595"
down_revision = "6e139e4d2c17"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feed_article",
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
            sa.ForeignKey("feed.id"),
            nullable=False,
        ),
        sa.Column(
            "article_id",
            sa.BigInteger,
            sa.ForeignKey("article.id"),
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
        "idx_feed_id", "feed_article", ["feed_id"], unique=False, if_not_exists=True
    )
    op.create_index(
        "idx_article_id",
        "feed_article",
        ["article_id"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("idx_article_id", table_name="feed_article", if_exists=True)
    op.drop_index("idx_feed_id", table_name="feed_article", if_exists=True)
    op.drop_table(
        "feed_article",
        info={"ifexists": True},
    )
