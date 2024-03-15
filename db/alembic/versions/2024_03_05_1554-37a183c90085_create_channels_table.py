"""create channels table

Revision ID: 37a183c90085
Revises: 7ab8f6bddd52
Create Date: 2024-03-05 15:54:33.199168+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "37a183c90085"
down_revision = "7ab8f6bddd52"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "channel",
        sa.Column(
            "id",
            sa.BigInteger,
            primary_key=True,
            nullable=False,
            server_default=sa.text("id_gen()"),
        ),
        sa.Column("name", sa.VARCHAR, nullable=False),
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
    op.create_index("ch_idx_name", "channel", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ch_idx_name", table_name="channel", if_exists=True)
    op.drop_table("channel")
