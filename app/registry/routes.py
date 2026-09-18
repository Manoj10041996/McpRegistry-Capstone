import asyncio
import json
import logging
from typing import Annotated

from asyncpg import PostgresError
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import SQLAlchemyError
from app.registry.tool_runner import execute_tool as call_mcp_tool
from sqlalchemy.ext.asyncio import AsyncEngine

from app.registry.connection_repository import (
    ConnectionNotFoundError,
    DuplicateConnectionError,
    RegisteredServerNotFoundError,
    get_connection_endpoint,
    list_connections,
    save_connection,
)
from app.registry.database import (
    DEMO_COMPANY_ID,
    get_registry_engine,
    registry_lifespan,
)
from app.registry.discovery import discover_tools
from app.registry.repository import (
    DuplicateServerError,
    list_servers,
    read_server,
    save_server,
)
from app.registry.schemas import (
    ConnectionResponse,
    ConnectionTestResponse,
    CreateConnectionRequest,
    RegisterServerRequest,
    ServerListResponse,
    ServerResponse,
    ToolMetadata,
    ExecuteToolRequest,
    ExecuteToolResponse,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/registry",
    tags=["Registry"],
    lifespan=registry_lifespan,
)

EngineDependency = Annotated[
    AsyncEngine,
    Depends(get_registry_engine),
]

ALLOWED_ENDPOINT = "http://127.0.0.1:8001/mcp"


def only_timeouts(error: BaseException) -> bool:
    if isinstance(error, BaseExceptionGroup):
        return all(
            only_timeouts(item)
            for item in error.exceptions
        )

    return isinstance(error, TimeoutError)


async def discover_allowed_tools(
    endpoint: str,
) -> list[ToolMetadata]:
    if endpoint != ALLOWED_ENDPOINT:
        raise HTTPException(
            status_code=403,
            detail="Only the local demo MCP endpoint is enabled.",
        )

    try:
        async with asyncio.timeout(10):
            discovered = await discover_tools(endpoint)

        if len(discovered) > 256:
            raise ValueError("Tool catalog exceeds the demo limit")

        tools = [
            ToolMetadata(
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
            )
            for tool in discovered
        ]

        if len({tool.name for tool in tools}) != len(tools):
            raise ValueError(
                "Tool names must be unique within a server"
            )

        payload = json.dumps(
            [tool.model_dump() for tool in tools],
            allow_nan=False,
        ).encode("utf-8")

        if len(payload) > 1_000_000:
            raise ValueError(
                "Tool metadata exceeds the demo size limit"
            )

        return tools

    except Exception as error:
        logger.warning(
            "MCP discovery failed (%s)",
            type(error).__name__,
        )

        if only_timeouts(error):
            raise HTTPException(
                status_code=504,
                detail="MCP discovery timed out.",
            ) from error

        raise HTTPException(
            status_code=502,
            detail="MCP discovery failed.",
        ) from error


@router.post(
    "/discover",
    response_model=list[ToolMetadata],
)
async def discover_server(
    request: RegisterServerRequest,
) -> list[ToolMetadata]:
    return await discover_allowed_tools(
        str(request.endpoint)
    )


@router.post(
    "/servers",
    status_code=201,
    response_model=ServerResponse,
)
async def register_server(
    request: RegisterServerRequest,
    engine: EngineDependency,
) -> ServerResponse:
    endpoint = str(request.endpoint)
    tools = await discover_allowed_tools(endpoint)

    try:
        return await save_server(
            engine,
            DEMO_COMPANY_ID,
            request.name,
            endpoint,
            tools,
        )

    except DuplicateServerError as error:
        raise HTTPException(
            status_code=409,
            detail=(
                "This MCP endpoint is already registered "
                "for the demo company."
            ),
        ) from error

    except (
        SQLAlchemyError,
        PostgresError,
        TimeoutError,
        OSError,
    ) as error:
        logger.error(
            "Registry write failed (%s)",
            type(error).__name__,
        )

        raise HTTPException(
            status_code=503,
            detail="Registry database operation failed.",
        ) from error


@router.get(
    "/servers/{server_id}",
    response_model=ServerResponse,
)
async def get_server(
    server_id: Annotated[int, Path(gt=0)],
    engine: EngineDependency,
) -> ServerResponse:
    try:
        saved = await read_server(
            engine,
            DEMO_COMPANY_ID,
            server_id,
        )

    except (
        SQLAlchemyError,
        PostgresError,
        TimeoutError,
        OSError,
    ) as error:
        logger.error(
            "Registry read failed (%s)",
            type(error).__name__,
        )

        raise HTTPException(
            status_code=503,
            detail="Registry database operation failed.",
        ) from error

    if saved is None:
        raise HTTPException(
            status_code=404,
            detail="Registered server not found.",
        )

    return saved


@router.get(
    "/servers",
    response_model=ServerListResponse,
)
async def search_servers(
    engine: EngineDependency,
    q: Annotated[str, Query(max_length=100)] = "",
    after_id: Annotated[
        int,
        Query(ge=0, le=2147483647),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> ServerListResponse:
    try:
        return await list_servers(
            engine=engine,
            company_id=DEMO_COMPANY_ID,
            search=q,
            after_id=after_id,
            limit=limit,
        )

    except (
        SQLAlchemyError,
        PostgresError,
        TimeoutError,
        OSError,
    ) as error:
        logger.error(
            "Registry list failed (%s)",
            type(error).__name__,
        )

        raise HTTPException(
            status_code=503,
            detail="Registry database operation failed.",
        ) from error


@router.post(
    "/servers/{server_id}/connections",
    status_code=201,
    response_model=ConnectionResponse,
)
async def create_connection(
    server_id: Annotated[int, Path(gt=0)],
    request: CreateConnectionRequest,
    engine: EngineDependency,
) -> ConnectionResponse:
    try:
        return await save_connection(
            engine,
            DEMO_COMPANY_ID,
            server_id,
            request.name,
            request.secret_ref,
        )

    except RegisteredServerNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Registered MCP server not found.",
        ) from error

    except DuplicateConnectionError as error:
        raise HTTPException(
            status_code=409,
            detail="This connection already exists.",
        ) from error

    except (
        SQLAlchemyError,
        PostgresError,
        TimeoutError,
        OSError,
    ) as error:
        logger.error(
            "Connection save failed (%s)",
            type(error).__name__,
        )

        raise HTTPException(
            status_code=503,
            detail="Connection database operation failed.",
        ) from error


@router.get(
    "/servers/{server_id}/connections",
    response_model=list[ConnectionResponse],
)
async def get_connections(
    server_id: Annotated[int, Path(gt=0)],
    engine: EngineDependency,
) -> list[ConnectionResponse]:
    try:
        server = await read_server(
            engine,
            DEMO_COMPANY_ID,
            server_id,
        )

        if server is None:
            raise HTTPException(
                status_code=404,
                detail="Registered MCP server not found.",
            )

        return await list_connections(
            engine,
            DEMO_COMPANY_ID,
            server_id,
        )

    except HTTPException:
        raise

    except (
        SQLAlchemyError,
        PostgresError,
        TimeoutError,
        OSError,
    ) as error:
        logger.error(
            "Connection list failed (%s)",
            type(error).__name__,
        )

        raise HTTPException(
            status_code=503,
            detail="Connection database operation failed.",
        ) from error


@router.post(
    "/servers/{server_id}/connections/{connection_id}/test",
    response_model=ConnectionTestResponse,
    responses={
        404: {"description": "Connection not found."},
        502: {"description": "MCP server is unreachable."},
        503: {"description": "Database operation failed."},
        504: {"description": "MCP server timed out."},
    },
)
async def test_connection(
    server_id: Annotated[int, Path(gt=0)],
    connection_id: Annotated[int, Path(gt=0)],
    engine: EngineDependency,
) -> ConnectionTestResponse:
    try:
        endpoint = await get_connection_endpoint(
            engine,
            DEMO_COMPANY_ID,
            server_id,
            connection_id,
        )

        tools = await discover_allowed_tools(endpoint)

        return ConnectionTestResponse(
            connection_id=connection_id,
            server_id=server_id,
            reachable=True,
            tool_count=len(tools),
        )

    except ConnectionNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Connection not found.",
        ) from error

    except (
        SQLAlchemyError,
        PostgresError,
        TimeoutError,
        OSError,
    ) as error:
        logger.error(
            "Connection test database operation failed (%s)",
            type(error).__name__,
        )

        raise HTTPException(
            status_code=503,
            detail="Connection database operation failed.",
        ) from error
@router.post(
    (
        "/servers/{server_id}/connections/{connection_id}"
        "/tools/{tool_name}"
    ),
    response_model=ExecuteToolResponse,
    responses={
        404: {"description": "Server, connection, or tool not found."},
        502: {"description": "MCP tool execution failed."},
        503: {"description": "Database operation failed."},
        504: {"description": "MCP tool execution timed out."},
    },
)
async def run_tool(
    server_id: Annotated[int, Path(gt=0)],
    connection_id: Annotated[int, Path(gt=0)],
    tool_name: Annotated[
        str,
        Path(min_length=1, max_length=128),
    ],
    request: ExecuteToolRequest,
    engine: EngineDependency,
) -> ExecuteToolResponse:
    try:
        server = await read_server(
            engine,
            DEMO_COMPANY_ID,
            server_id,
        )

        if server is None:
            raise HTTPException(
                status_code=404,
                detail="Registered MCP server not found.",
            )

        if tool_name not in {
            tool.name for tool in server.tools
        }:
            raise HTTPException(
                status_code=404,
                detail="Registered MCP tool not found.",
            )

        endpoint = await get_connection_endpoint(
            engine,
            DEMO_COMPANY_ID,
            server_id,
            connection_id,
        )

    except HTTPException:
        raise

    except ConnectionNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Connection not found.",
        ) from error

    except (
        SQLAlchemyError,
        PostgresError,
        TimeoutError,
        OSError,
    ) as error:
        logger.error(
            "Tool lookup failed (%s)",
            type(error).__name__,
        )
        raise HTTPException(
            status_code=503,
            detail="Registry database operation failed.",
        ) from error

    try:
        return await call_mcp_tool(
            endpoint=endpoint,
            connection_id=connection_id,
            tool_name=tool_name,
            arguments=request.arguments,
        )

    except Exception as error:
        logger.warning(
            "MCP tool execution failed (%s)",
            type(error).__name__,
        )

        if only_timeouts(error):
            raise HTTPException(
                status_code=504,
                detail="MCP tool execution timed out.",
            ) from error

        raise HTTPException(
            status_code=502,
            detail="MCP tool execution failed.",
        ) from error