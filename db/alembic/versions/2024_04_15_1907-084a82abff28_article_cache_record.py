"""article_cache_record

Revision ID: 084a82abff28
Revises: b2d3f1f85e7d
Create Date: 2024-04-15 19:07:15.915352+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "084a82abff28"
down_revision = "b2d3f1f85e7d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "article_cache_record",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column(
            "article_id",
            sa.BigInteger,
            sa.ForeignKey("article.id"),
            nullable=False,
            default=0,
        ),
        sa.Column(
            "locale_id", sa.BigInteger, sa.ForeignKey("locale.id"), nullable=False
        ),
        sa.Column("cache_hit", sa.Integer, nullable=False),
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
        "article_cache_record_idx_article_id",
        "article_cache_record",
        ["article_id"],
        unique=True,
        if_not_exists=True,
    )
    op.create_index(
        "article_cache_record_idx_locale_id",
        "article_cache_record",
        ["locale_id"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "article_cache_record_idx_locale_id",
        table_name="article_cache_record",
        if_exists=True,
    )
    op.drop_index(
        "article_cache_record_idx_article_id",
        table_name="article_cache_record",
        if_exists=True,
    )
    op.drop_table("article_cache_record", if_exists=True)
