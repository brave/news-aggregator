"""create feeds table

Revision ID: 1f9b63c5cb07
Revises: 37a183c90085
Create Date: 2024-03-05 16:00:07.328230+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1f9b63c5cb07"
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
        sa.Column("og_images", sa.Boolean, default=False),
        sa.Column("max_entries", sa.Integer, default=20),
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
        "feed_idx_url_hash", "feed", ["url_hash"], unique=True, if_not_exists=True
    )
    op.create_index(
        "idx_publisher_id", "feed", ["publisher_id"], unique=False, if_not_exists=True
    )


def downgrade() -> None:
    op.drop_index("idx_publisher_id", table_name="feed", if_exists=True)
    op.drop_index("feed_idx_url_hash", table_name="feed", if_exists=True)
    op.drop_table(
        "feed",
        info={"ifexists": True},
    )
