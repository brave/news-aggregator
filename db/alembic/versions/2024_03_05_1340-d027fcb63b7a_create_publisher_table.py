"""create publisher table

Revision ID: d027fcb63b7a
Revises: ec0e245c0a9e
Create Date: 2024-03-05 13:40:21.010447+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d027fcb63b7a"
down_revision = "ec0e245c0a9e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news.publishers",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            default=sa.text("news.id_gen()"),
        ),
        sa.Column("name", sa.VARCHAR, nullable=False),
        sa.Column("url", sa.VARCHAR, nullable=False),
        sa.Column("favicon", sa.VARCHAR, default=""),
        sa.Column("cover_image", sa.VARCHAR, default="", nullable=True),
        sa.Column("background_color", sa.VARCHAR, default="", nullable=True),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("score", sa.Float, default=0.0, nullable=False),
        sa.Column("url_hash", sa.VARCHAR, nullable=False, unique=True),
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
    op.create_index("idx_url_hash", "news.publishers", ["url_hash"], unique=True)
    op.create_index("idx_url", "news.publishers", ["url"], unique=True)


def downgrade() -> None:
    op.drop_index("idx_url", table_name="news.publishers")
    op.drop_index("idx_url_hash", table_name="news.publishers")
    op.drop_table("news.publishers")
