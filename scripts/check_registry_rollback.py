import asyncio
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.registry.database import create_registry_engine
from app.registry.repository import save_server
from app.registry.schemas import ToolMetadata


async def check_rollback() -> None:
    engine = create_registry_engine()

    # A new test company keeps this check separate from your demo records.
    test_company_id = uuid4()

    tool = ToolMetadata(
        name="rollback_test_tool",
        description="Temporary tool used to check rollback.",
        input_schema={"type": "object"},
    )

    try:
        try:
            await save_server(
                engine=engine,
                company_id=test_company_id,
                name="Rollback test server",
                endpoint="http://127.0.0.1:8001/mcp",
                tools=[tool, tool],
            )

        except IntegrityError as error:
            # PostgreSQL code 23505 means a uniqueness rule was violated.
            if getattr(error.orig, "sqlstate", None) != "23505":
                raise

            print("PASS: PostgreSQL rejected the duplicate tool.")

        else:
            raise AssertionError(
                "FAIL: The duplicate tool was unexpectedly accepted."
            )

        # Use a separate connection after the failed transaction.
        async with engine.connect() as connection:
            remaining_servers = await connection.scalar(
                text("""
                    SELECT count(*)
                    FROM mcp_servers
                    WHERE company_id = :company_id
                """),
                {"company_id": test_company_id},
            )

        if remaining_servers != 0:
            raise AssertionError(
                "FAIL: A server record remained after the tool insert failed."
            )

        print("PASS: The server insert was rolled back.")
        print("PASS: No partial registration remains.")

    finally:
        # Clean up only this check's temporary company records.
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
    asyncio.run(check_rollback())