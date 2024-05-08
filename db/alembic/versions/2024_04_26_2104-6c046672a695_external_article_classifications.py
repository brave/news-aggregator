"""external_article_classifications

Revision ID: 6c046672a695
Revises: 084a82abff28
Create Date: 2024-04-26 21:04:42.816062+00:00

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "6c046672a695"
down_revision = "084a82abff28"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "external_article_classification",
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
        ),
        # col for channels text array
        sa.Column("channels", sa.ARRAY(sa.Text), nullable=False),
        sa.Column("raw_data", JSONB, nullable=False),
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
        "external_article_classifications_idx_article_id",
        "external_article_classification",
        ["article_id"],
        unique=True,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "external_article_classifications_idx_article_id",
        table_name="external_article_classification",
        if_exists=True,
    )
    op.drop_table("external_article_classification", info={"ifexists": True})
