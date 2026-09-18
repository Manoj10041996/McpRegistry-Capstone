import asyncio
from uuid import uuid4

from sqlalchemy import text

from app.registry.database import create_registry_engine
from app.registry.repository import DuplicateServerError, save_server
from app.registry.schemas import ServerResponse, ToolMetadata


async def check_concurrency() -> None:
    engine = create_registry_engine()
    test_company_id = uuid4()

    tool = ToolMetadata(
        name="concurrency_test_tool",
        description="Temporary test tool.",
        input_schema={"type": "object"},
    )

    try:
        # Schedule two registrations for the same company and endpoint.
        results = await asyncio.gather(
            save_server(
                engine,
                test_company_id,
                "Concurrent registration A",
                "http://127.0.0.1:8001/mcp",
                [tool],
            ),
            save_server(
                engine,
                test_company_id,
                "Concurrent registration B",
                "http://127.0.0.1:8001/mcp",
                [tool],
            ),
            return_exceptions=True,
        )

        successes = sum(
            isinstance(result, ServerResponse)
            for result in results
        )

        duplicates = sum(
            isinstance(result, DuplicateServerError)
            for result in results
        )

        if successes != 1 or duplicates != 1:
            result_types = [
                type(result).__name__
                for result in results
            ]
            raise AssertionError(
                f"Unexpected registration outcomes: {result_types}"
            )

        async with engine.connect() as connection:
            server_count = await connection.scalar(
                text("""
                    SELECT count(*)
                    FROM mcp_servers
                    WHERE company_id = :company_id
                """),
                {"company_id": test_company_id},
            )

            tool_count = await connection.scalar(
                text("""
                    SELECT count(*)
                    FROM mcp_tools AS t
                    JOIN mcp_servers AS s
                        ON s.id = t.server_id
                    WHERE s.company_id = :company_id
                """),
                {"company_id": test_company_id},
            )

        if server_count != 1 or tool_count != 1:
            raise AssertionError(
                f"Expected one server and one tool; "
                f"found {server_count} servers and {tool_count} tools."
            )

        print("PASS: One registration succeeded.")
        print("PASS: The competing registration was rejected.")
        print("PASS: Exactly one server and one tool were saved.")

    finally:
        try:
            async with engine.begin() as connection:
                await connection.execute(
                    text("""
                        DELETE FROM mcp_tools
                        WHERE server_id IN (
                            SELECT id
                            FROM mcp_servers
                            WHERE company_id = :company_id
                        )
                    """),
                    {"company_id": test_company_id},
                )

                await connection.execute(
                    text("""
                        DELETE FROM mcp_servers
                        WHERE company_id = :company_id
                    """),
                    {"company_id": test_company_id},
                )

        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_concurrency())