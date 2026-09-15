"""Reject duplicate endpoints within a company.

Revision ID: d19c4f2a8b01
Revises: c70e07595102
"""

from alembic import op


revision = "d19c4f2a8b01"
down_revision = "c70e07595102"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_mcp_servers_company_endpoint",
        "mcp_servers",
        ["company_id", "endpoint"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_mcp_servers_company_endpoint",
        "mcp_servers",
        type_="unique",
    )