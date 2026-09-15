import asyncio

from app.registry.discovery import discover_tools

async def discover() -> None:
    tools = await discover_tools("http://127.0.0.1:8001/mcp")

    for tool in tools:
        print(tool.name)


if __name__ == "__main__":
    try:
        asyncio.run(discover())
    except TimeoutError:
        print("Discovery timed out.")
        raise SystemExit(1)
    except Exception as error:
        print(f"Discovery failed: {type(error).__name__}")
        raise SystemExit(1)