"""create MCP connections

Revision ID: efbbd3fa0c10
Revises: d19c4f2a8b01
Create Date: 2026-09-15

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "efbbd3fa0c10"
down_revision: Union[str, Sequence[str], None] = "d19c4f2a8b01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mcp_connections",
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
        sa.Column(
            "server_id",
            sa.Integer(),
            sa.ForeignKey(
                "mcp_servers.id",
                name="fk_mcp_connections_server_id",
            ),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "secret_ref",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_mcp_connections_name_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(secret_ref)) > 0",
            name="ck_mcp_connections_secret_ref_not_blank",
        ),
        sa.UniqueConstraint(
            "company_id",
            "server_id",
            "name",
            name="uq_mcp_connections_company_server_name",
        ),
    )

    op.create_index(
        "ix_mcp_connections_company_id",
        "mcp_connections",
        ["company_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mcp_connections_company_id",
        table_name="mcp_connections",
    )
    op.drop_table("mcp_connections")