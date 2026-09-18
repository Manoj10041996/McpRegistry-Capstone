# MCP Registry — Local Demo

## What this version does

- Discovers tools from the local demo MCP server.
- Saves the server and its tools in PostgreSQL.
- Retrieves, lists and searches saved registrations.
- Rejects duplicate registrations.
- Rolls back a registration if saving fails.
- Prevents concurrent duplicate registrations.

## Start the application

Open Docker Desktop.

From the project root, run:

```cmd
start_local.cmd
```

Wait for application startup to complete, then open:

http://127.0.0.1:8000/docs

## Demonstration

### 1. List registered servers

Execute GET /registry/servers.

Expected: Demo MCP appears with tool_count equal to 1.

### 2. Search by tool name

Execute GET /registry/servers with:

q = count_characters

Expected: Demo MCP appears because it provides that tool.

### 3. Retrieve the saved registration

Execute GET /registry/servers/1.

Expected: server details and the saved tool input schema.

### 4. Demonstrate duplicate rejection

Execute POST /registry/servers with:

{
  "name": "Demo MCP",
  "endpoint": "http://127.0.0.1:8001/mcp"
}

Expected: 409 Conflict because this endpoint is already registered.

### 5. Explain persistence and failure handling

The GET endpoints read PostgreSQL, so saved records remain readable
while the MCP server is offline.

Registration contacts MCP first. If discovery fails, registration
does not proceed to database inserts.

Server and tool inserts share one transaction. A failed tool insert
rolls back the registration.

## Database checks already passed

```cmd
uv run python -m scripts