import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import create_async_engine


async def check_database() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(env_path)

    database_url = URL.create(
        drivername="postgresql+asyncpg",
        username="registry_admin",
        password=os.environ["POSTGRES_PASSWORD"],
        host="127.0.0.1",
        port=55432,
        database="mcp_registry",
    )

    engine = create_async_engine(database_url)

    try:
        async with asyncio.timeout(10):
            async with engine.connect() as connection:
                result = await connection.execute(
                    text("SELECT current_database(), current_user")
                )
                print(result.one())
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_database())