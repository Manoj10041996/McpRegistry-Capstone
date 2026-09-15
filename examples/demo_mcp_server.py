from mcp.server import MCPServer

server = MCPServer("Registry learning server")


@server.tool()
def count_characters(text: str) -> int:
    """Count the characters in the supplied text."""
    return len(text)


if __name__ == "__main__":
    server.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
    )