import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


logger = logging.getLogger(__name__)

# Temporary company identity for this learning project.
DEMO_COMPANY_ID = UUID(
    "11111111-1111-4111-8111-111111111111"
)


def create_registry_engine() -> AsyncEngine | None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    password = os.getenv("POSTGRES_PASSWORD")

    # Cloud Run currently has no PostgreSQL database configured.
    # Allow the API to start so /health remains available.
    if not password:
        return None

    database_url = URL.create(
        drivername="postgresql+asyncpg",
        username=os.getenv(
            "POSTGRES_USER",
            "registry_admin",
        ),
        password=password,
        host=os.getenv(
            "POSTGRES_HOST",
            "127.0.0.1",
        ),
        port=int(
            os.getenv(
                "POSTGRES_PORT",
                "55432",
            )
        ),
        database=os.getenv(
            "POSTGRES_DB",
            "mcp_registry",
        ),
    )

    return create_async_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=0,
        pool_timeout=5,
        hide_parameters=True,
        connect_args={
            "timeout": 5,
            "command_timeout": 10,
        },
    )


@asynccontextmanager
async def registry_lifespan(app: FastAPI):
    engine = create_registry_engine()
    app.state.registry_engine = engine

    if engine is None:
        logger.warning(
            "Registry database is not configured. "
            "Registry endpoints will return HTTP 503."
        )

    try:
        yield
    finally:
        if engine is not None:
            await engine.dispose()


def get_registry_engine(
    request: Request,
) -> AsyncEngine:
    engine = getattr(
        request.app.state,
        "registry_engine",
        None,
    )

    if engine is None:
        raise HTTPException(
            status_code=503,
            detail="Registry database is not configured.",
        )

    return engine