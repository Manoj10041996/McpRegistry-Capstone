"""create registry tables

Revision ID: c70e07595102
Revises:
Create Date: 2026-09-15 03:42:31.579495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c70e07595102'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mcp_servers",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(),
            primary_key=True,
        ),
        sa.Column(
            "company_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_mcp_servers_name_not_blank",
        ),
    )

    op.create_index(
        "ix_mcp_servers_company_id",
        "mcp_servers",
        ["company_id"],
    )

    op.create_table(
        "mcp_tools",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(),
            primary_key=True,
        ),
        sa.Column(
            "server_id",
            sa.Integer(),
            sa.ForeignKey(
                "mcp_servers.id",
                name="fk_mcp_tools_server_id",
            ),
            nullable=False,
        ),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "input_schema",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "server_id",
            "name",
            name="uq_mcp_tools_server_name",
        ),
    )


def downgrade() -> None:
    op.drop_table("mcp_tools")
    op.drop_index(
        "ix_mcp_servers_company_id",
        table_name="mcp_servers",
    )
    op.drop_table("mcp_servers")