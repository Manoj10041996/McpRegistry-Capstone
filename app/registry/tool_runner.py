import asyncio
from typing import Any

from mcp import Client

from app.registry.schemas import ExecuteToolResponse


async def execute_tool(
    endpoint: str,
    connection_id: int,
    tool_name: str,
    arguments: dict[str, Any],
) -> ExecuteToolResponse:
    async with asyncio.timeout(20):
        async with Client(endpoint) as client:
            result = await client.call_tool(
                tool_name,
                arguments,
            )

    structured_content = result.structured_content

    if (
        structured_content is not None
        and not isinstance(structured_content, dict)
    ):
        structured_content = {
            "result": structured_content,
        }

    return ExecuteToolResponse(
        connection_id=connection_id,
        tool_name=tool_name,
        is_error=result.is_error,
        structured_content=structured_content,
    )