"""create Article table

Revision ID: 6e139e4d2c17
Revises: c85f87c4196e
Create Date: 2024-03-05 16:10:17.016911+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6e139e4d2c17"
down_revision: Union[str, None] = "c85f87c4196e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "article",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column("title", sa.VARCHAR, nullable=False),
        sa.Column("publish_time", sa.DateTime(True), nullable=False),
        sa.Column("img_url", sa.VARCHAR, default=""),
        sa.Column("category", sa.VARCHAR, nullable=False),
        sa.Column("description", sa.VARCHAR),
        sa.Column("content_type", sa.VARCHAR, nullable=False, default="article"),
        sa.Column("creative_instance_id", sa.VARCHAR, default=""),
        sa.Column("url", sa.VARCHAR, nullable=False),
        sa.Column("url_hash", sa.VARCHAR, nullable=False),
        sa.Column("pop_score", sa.Float, default=0.0, nullable=False),
        sa.Column("padded_img_url", sa.VARCHAR, default=""),
        sa.Column("score", sa.Float, default=0.0, nullable=False),
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
    op.create_index("idx_url_hash", "article", ["url_hash"], unique=True)
    op.create_index("idx_url", "article", ["url"], unique=True)


def downgrade() -> None:
    op.drop_index("idx_url", table_name="article", if_exists=True)
    op.drop_index("idx_url_hash", table_name="article", if_exists=True)
    op.drop_table("article")
