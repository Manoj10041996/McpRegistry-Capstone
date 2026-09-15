from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.registry.schemas import ConnectionResponse


class RegisteredServerNotFoundError(Exception):
    pass


class DuplicateConnectionError(Exception):
    pass


async def save_connection(
    engine: AsyncEngine,
    company_id: UUID,
    server_id: int,
    name: str,
    secret_ref: str,
) -> ConnectionResponse:
    async with engine.begin() as connection:
        server_result = await connection.execute(
            text(
                """
                SELECT id
                FROM mcp_servers
                WHERE id = :server_id
                  AND company_id = :company_id
                """
            ),
            {
                "server_id": server_id,
                "company_id": company_id,
            },
        )

        if server_result.first() is None:
            raise RegisteredServerNotFoundError

        result = await connection.execute(
            text(
                """
                INSERT INTO mcp_connections (
                    company_id,
                    server_id,
                    name,
                    secret_ref
                )
                VALUES (
                    :company_id,
                    :server_id,
                    :name,
                    :secret_ref
                )
                ON CONFLICT ON CONSTRAINT
                    uq_mcp_connections_company_server_name
                DO NOTHING
                RETURNING id, server_id, name, created_at
                """
            ),
            {
                "company_id": company_id,
                "server_id": server_id,
                "name": name,
                "secret_ref": secret_ref,
            },
        )

        row = result.mappings().one_or_none()

        if row is None:
            raise DuplicateConnectionError

        return ConnectionResponse(
            id=row["id"],
            server_id=row["server_id"],
            name=row["name"],
            created_at=row["created_at"],
            credential_configured=True,
        )


async def list_connections(
    engine: AsyncEngine,
    company_id: UUID,
    server_id: int,
) -> list[ConnectionResponse]:
    async with engine.connect() as connection:
        result = await connection.execute(
            text(
                """
                SELECT id, server_id, name, created_at
                FROM mcp_connections
                WHERE company_id = :company_id
                  AND server_id = :server_id
                ORDER BY id
                """
            ),
            {
                "company_id": company_id,
                "server_id": server_id,
            },
        )

        rows = result.mappings().all()

    return [
        ConnectionResponse(
            id=row["id"],
            server_id=row["server_id"],
            name=row["name"],
            created_at=row["created_at"],
            credential_configured=True,
        )
        for row in rows
    ]