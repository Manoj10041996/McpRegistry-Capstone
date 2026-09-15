import asyncio
import json
import logging
from typing import Annotated

from asyncpg import PostgresError
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine
from fastapi import Query

from app.registry.repository import list_servers
from app.registry.schemas import ServerListResponse

from app.registry.database import (
    DEMO_COMPANY_ID,
    get_registry_engine,
    registry_lifespan,
)
from app.registry.discovery import discover_tools
from app.registry.repository import (
    DuplicateServerError,
    read_server,
    save_server,
)
from app.registry.schemas import (
    RegisterServerRequest,
    ServerResponse,
    ToolMetadata,
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
):
    return await discover_allowed_tools(
        str(request.endpoint)
    )


@router.post(
    "/servers",
    status_code=201,
    response_model=ServerResponse,
    responses={
        403: {"description": "MCP endpoint is not allowed."},
        409: {"description": "Endpoint is already registered."},
        502: {"description": "MCP discovery failed."},
        503: {"description": "Database operation failed."},
        504: {"description": "MCP discovery timed out."},
    },
)
async def register_server(
    request: RegisterServerRequest,
    engine: EngineDependency,
):
    endpoint = str(request.endpoint)

    # Finish the MCP request before opening a database transaction.
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
):
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
    responses={
        503: {"description": "Database operation failed."},
    },
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
):
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