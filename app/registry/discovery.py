import asyncio
from mcp import Client
from mcp.types import Tool

async def discover_tools(endpoint : str) -> list[Tool]:
    async with asyncio.timeout(10):
        async with Client(endpoint) as client:
            result=await client.list_tools()
            return result.tools
