import os
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


# Temporary company identity for this local learning exercise.
# Replace it with trusted authenticated-user context before multi-user use.
DEMO_COMPANY_ID = UUID("11111111-1111-4111-8111-111111111111")


def create_registry_engine() -> AsyncEngine:
    # This file is app/registry/database.py.
    # parents[2] therefore points to the project root.
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    database_url = URL.create(
        drivername="postgresql+asyncpg",
        username="registry_admin",
        password=os.environ["POSTGRES_PASSWORD"],
        host="127.0.0.1",
        port=55432,
        database="mcp_registry",
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

    try:
        yield
    finally:
        await engine.dispose()


def get_registry_engine(request: Request) -> AsyncEngine:
    return request.app.state.registry_engine