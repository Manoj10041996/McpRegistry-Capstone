from uuid import UUID

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import String

from app.registry.schemas import ServerListResponse, ServerSummary
from app.registry.schemas import ServerResponse, ToolMetadata


class DuplicateServerError(Exception):
    pass


INSERT_SERVER = text("""
    INSERT INTO mcp_servers (company_id, name, endpoint)
    VALUES (:company_id, :name, :endpoint)
    ON CONFLICT ON CONSTRAINT uq_mcp_servers_company_endpoint
    DO NOTHING
    RETURNING id, name, endpoint, created_at
""")


INSERT_TOOL = text("""
    INSERT INTO mcp_tools (
        server_id,
        name,
        description,
        input_schema
    )
    VALUES (
        :server_id,
        :name,
        :description,
        :input_schema
    )
""").bindparams(
    bindparam("input_schema", type_=JSONB)
)


async def save_server(
    engine: AsyncEngine,
    company_id: UUID,
    name: str,
    endpoint: str,
    tools: list[ToolMetadata],
) -> ServerResponse:
    async with engine.begin() as connection:
        result = await connection.execute(
            INSERT_SERVER,
            {
                "company_id": company_id,
                "name": name,
                "endpoint": endpoint,
            },
        )

        row = result.mappings().one_or_none()

        if row is None:
            raise DuplicateServerError

        if tools:
            await connection.execute(
                INSERT_TOOL,
                [
                    {
                        "server_id": row["id"],
                        **tool.model_dump(),
                    }
                    for tool in tools
                ],
            )

        saved = ServerResponse(
            **dict(row),
            tools=tools,
        )

    # The transaction has committed before we return.
    return saved


async def read_server(
    engine: AsyncEngine,
    company_id: UUID,
    server_id: int,
) -> ServerResponse | None:
    query = text("""
        SELECT
            s.id,
            s.name,
            s.endpoint,
            s.created_at,
            t.id AS tool_id,
            t.name AS tool_name,
            t.description,
            t.input_schema
        FROM mcp_servers AS s
        LEFT JOIN mcp_tools AS t
            ON t.server_id = s.id
        WHERE
            s.company_id = :company_id
            AND s.id = :server_id
        ORDER BY t.id
    """)

    async with engine.connect() as connection:
        result = await connection.execute(
            query,
            {
                "company_id": company_id,
                "server_id": server_id,
            },
        )

        rows = result.mappings().all()

    if not rows:
        return None

    return ServerResponse(
        id=rows[0]["id"],
        name=rows[0]["name"],
        endpoint=rows[0]["endpoint"],
        created_at=rows[0]["created_at"],
        tools=[
            ToolMetadata(
                name=row["tool_name"],
                description=row["description"],
                input_schema=row["input_schema"],
            )
            for row in rows
            if row["tool_id"] is not None
        ],
    )
async def list_servers(
    engine: AsyncEngine,
    company_id: UUID,
    search: str,
    after_id: int,
    limit: int,
) -> ServerListResponse:
    query = text("""
        SELECT
            s.id,
            s.name,
            s.endpoint,
            s.created_at,
            (
                SELECT count(*)
                FROM mcp_tools AS t
                WHERE t.server_id = s.id
            ) AS tool_count
        FROM mcp_servers AS s
        WHERE
            s.company_id = :company_id
            AND s.id > :after_id
            AND (
                strpos(lower(s.name), lower(:search)) > 0
                OR strpos(lower(s.endpoint), lower(:search)) > 0
                OR EXISTS (
                    SELECT 1
                    FROM mcp_tools AS matched_tool
                    WHERE
                        matched_tool.server_id = s.id
                        AND strpos(
                            lower(matched_tool.name),
                            lower(:search)
                        ) > 0
                )
            )
        ORDER BY s.id
        LIMIT :fetch_limit
    """).bindparams(
        bindparam("search", type_=String())
    )

    async with engine.connect() as connection:
        result = await connection.execute(
            query,
            {
                "company_id": company_id,
                "search": search.strip(),
                "after_id": after_id,
                "fetch_limit": limit + 1,
            },
        )

        rows = result.mappings().all()

    has_more = len(rows) > limit

    items = [
        ServerSummary(**dict(row))
        for row in rows[:limit]
    ]

    return ServerListResponse(
        items=items,
        next_after_id=items[-1].id if has_more else None,
    )