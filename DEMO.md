# MCP Registry Demonstration Guide

This guide shows the complete local demonstration of the MCP Registry and Connections backend.

## What This Demonstration Proves

The demonstration proves that the application can:

1. Connect to PostgreSQL.
2. Apply database migrations.
3. Connect to an MCP server.
4. Discover MCP tools.
5. Register an MCP server and its tools.
6. Search stored server and tool metadata.
7. Reject duplicate registration.
8. Create connection metadata.
9. List saved connections.
10. Test MCP server reachability.
11. Execute a registered MCP tool.
12. Roll back incomplete database writes.
13. Protect against concurrent duplicate registration.
14. Run automated API tests.

---

## Required Local Services

The demonstration uses three services:

| Service | Port | Purpose |
|---|---:|---|
| PostgreSQL | 55432 | Stores server, tool, and connection records |
| FastAPI | 8000 | Provides REST API endpoints |
| Demo MCP server | 8001 | Provides the `count_characters` tool |

Use separate command windows because FastAPI and the MCP server must remain running.

---

## Step 1: Open the Project

Open Command Prompt:

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
```

Confirm the current Git branch:

```cmd
git branch --show-current
```

Install the locked dependencies:

```cmd
uv sync --frozen
```

---

## Step 2: Start PostgreSQL

Make sure Docker Desktop is running.

Start PostgreSQL:

```cmd
docker compose up -d --wait db
```

Check the container:

```cmd
docker compose ps
```

Expected status:

```text
healthy
```

Expected port mapping:

```text
127.0.0.1:55432 -> 5432
```

---

## Step 3: Check the Database Connection

Run:

```cmd
uv run python -m scripts.check_database
```

Expected output:

```text
('mcp_registry', 'registry_admin')
```

This proves that Python can connect to PostgreSQL.

---

## Step 4: Apply Database Migrations

Run:

```cmd
uv run alembic upgrade head
```

Check the current revision:

```cmd
uv run alembic current
```

Expected revision:

```text
efbbd3fa0c10 (head)
```

View the database tables:

```cmd
docker compose exec db psql -U registry_admin -d mcp_registry -c "\dt"
```

Expected tables include:

```text
alembic_version
mcp_servers
mcp_tools
mcp_connections
```

---

## Step 5: Start the Demo MCP Server

Open a second Command Prompt:

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
uv run python examples\demo_mcp_server.py
```

Expected output:

```text
Uvicorn running on http://127.0.0.1:8001
```

Keep this command window open.

The MCP endpoint is:

```text
http://127.0.0.1:8001/mcp
```

The demo MCP server provides one tool:

```text
count_characters
```

The tool counts the characters in supplied text.

A browser may return HTTP 404 for:

```text
http://127.0.0.1:8001/
```

```text
http://127.0.0.1:8001/docs
```

This is expected. The MCP endpoint is `/mcp`.

---

## Step 6: Test MCP Tool Discovery

Open another Command Prompt:

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
uv run python -m scripts.discover_demo_tools
```

The output should contain:

```text
count_characters
```

This proves that the MCP client can connect to the demo MCP server and read its tool catalog.

---

## Step 7: Start FastAPI

Open another Command Prompt:

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
uv run uvicorn app.main:app --reload --port 8000
```

Expected output:

```text
Uvicorn running on http://127.0.0.1:8000
```

Keep this command window open.

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Step 8: Check Application Health

Run in another Command Prompt:

```cmd
curl.exe --noproxy "*" -i http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

Expected status:

```text
HTTP/1.1 200 OK
```

---

## Step 9: Discover Tools Without Saving

Run:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/discover" -H "Content-Type: application/json" -d "{\"name\":\"Demo MCP\",\"endpoint\":\"http://127.0.0.1:8001/mcp\"}"
```

Expected tool information:

```json
[
  {
    "name": "count_characters",
    "description": "Count the characters in the supplied text.",
    "input_schema": {
      "type": "object",
      "properties": {
        "text": {
          "type": "string",
          "title": "Text"
        }
      },
      "required": [
        "text"
      ],
      "title": "count_charactersArguments"
    }
  }
]
```

This operation discovers tools but does not register a new server record.

---

## Step 10: Register the MCP Server

Run:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers" -H "Content-Type: application/json" -d "{\"name\":\"Demo MCP\",\"endpoint\":\"http://127.0.0.1:8001/mcp\"}"
```

Expected status for a new record:

```text
HTTP/1.1 201 Created
```

The response contains:

- Server ID
- Server name
- MCP endpoint
- Creation time
- Discovered tools

If the endpoint is already registered, the expected response is:

```text
HTTP/1.1 409 Conflict
```

```json
{
  "detail": "This MCP endpoint is already registered for the demo company."
}
```

The 409 response proves that duplicate registration protection is working.

---

## Step 11: List Registered Servers

Run:

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers"
```

Expected status:

```text
HTTP/1.1 200 OK
```

The response contains registered server summaries and tool counts.

---

## Step 12: Search by Tool Name

Run:

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers?q=count_characters"
```

The demo server should be returned because it provides the `count_characters` tool.

Test a search with no result:

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers?q=does-not-exist"
```

Expected response:

```json
{
  "items": [],
  "next_after_id": null
}
```

---

## Step 13: Read One Registered Server

Run:

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers/1"
```

Expected status:

```text
HTTP/1.1 200 OK
```

The response contains the server and stored tool metadata.

This endpoint reads PostgreSQL data. It does not rediscover the tools.

---

## Step 14: Create Connection Metadata

Run:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections" -H "Content-Type: application/json" -d "{\"name\":\"Demo connection\",\"secret_ref\":\"local/demo-token\"}"
```

Expected status for a new connection:

```text
HTTP/1.1 201 Created
```

Example response:

```json
{
  "id": 1,
  "server_id": 1,
  "name": "Demo connection",
  "created_at": "2026-09-15T18:25:04.853314Z",
  "credential_configured": true
}
```

The API does not expose `secret_ref` in its response.

If the same connection already exists, the API returns:

```text
HTTP/1.1 409 Conflict
```

```json
{
  "detail": "This connection already exists."
}
```

---

## Step 15: List Connections

Run:

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers/1/connections"
```

Expected status:

```text
HTTP/1.1 200 OK
```

The response lists saved connection metadata without exposing the stored secret reference.

---

## Step 16: Test the Connection

Run:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections/1/test"
```

Expected response:

```json
{
  "connection_id": 1,
  "server_id": 1,
  "reachable": true,
  "tool_count": 1
}
```

This proves that the API can use the saved server endpoint to reach the MCP server.

---

## Step 17: Execute the MCP Tool

Run:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections/1/tools/count_characters" -H "Content-Type: application/json" -d "{\"arguments\":{\"text\":\"hello\"}}"
```

Expected response:

```json
{
  "connection_id": 1,
  "tool_name": "count_characters",
  "is_error": false,
  "structured_content": {
    "result": 5
  }
}
```

The result is `5` because `hello` contains five characters.

Test an unknown tool:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections/1/tools/unknown_tool" -H "Content-Type: application/json" -d "{\"arguments\":{}}"
```

Expected status:

```text
HTTP/1.1 404 Not Found
```

Expected response:

```json
{
  "detail": "Registered MCP tool not found."
}
```

---

## Step 18: Verify Stored Data While MCP Is Offline

Stop the demo MCP server using:

```text
CTRL+C
```

Confirm that port 8001 is no longer listening:

```cmd
netstat -ano | findstr LISTENING | findstr /C:":8001 "
```

Read the stored server:

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers/1"
```

Expected result:

```text
HTTP/1.1 200 OK
```

The stored record remains available because the server and tool metadata are stored in PostgreSQL.

Now try a live connection test:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections/1/test"
```

This request should fail because a live MCP connection requires port 8001.

Restart the MCP server before continuing:

```cmd
uv run python examples\demo_mcp_server.py
```

---

## Step 19: Verify Transaction Rollback

Run:

```cmd
uv run python -m scripts.check_registry_rollback
```

Expected output:

```text
PASS: PostgreSQL rejected the duplicate tool.
PASS: The server insert was rolled back.
PASS: No partial registration remains.
```

This proves that one failed insert cancels the complete registration transaction.

---

## Step 20: Verify Concurrent Duplicate Protection

Run:

```cmd
uv run python -m scripts.check_registry_concurrency
```

Expected output:

```text
PASS: One registration succeeded.
PASS: The competing registration was rejected.
PASS: Exactly one server and one tool were saved.
```

This proves that simultaneous duplicate requests cannot create duplicate records.

---

## Step 21: Run Automated Tests

Run:

```cmd
uv run python -m pytest -q
```

Verified result:

```text
7 passed
```

A dependency deprecation warning may appear. The tests still pass when the final result says `7 passed`.

---

## Step 22: Run Lint Checks

Run:

```cmd
uv run --with ruff ruff check app tests scripts migrations --select E9,F
```

Expected result:

```text
All checks passed!
```

---

## Optional: Use Port 8010

If another application is already using port 8000, do not terminate an unknown process.

Start this FastAPI application on port 8010:

```cmd
uv run uvicorn app.main:app --reload --port 8010
```

Then replace:

```text
http://127.0.0.1:8000
```

with:

```text
http://127.0.0.1:8010
```

in the API commands.

---

## Stop the Demonstration

Stop FastAPI:

```text
CTRL+C
```

Stop the demo MCP server:

```text
CTRL+C
```

Stop PostgreSQL:

```cmd
docker compose stop db
```

Stopping the database container does not delete the PostgreSQL volume.

---

## Demonstration Result

A successful demonstration proves:

- The application starts correctly.
- PostgreSQL is connected.
- Database migrations are current.
- The MCP server exposes a discoverable tool.
- Server and tool metadata can be stored.
- Saved metadata can be searched and retrieved.
- Duplicate registration is rejected.
- Incomplete writes are rolled back.
- Concurrent duplicate requests are controlled.
- Connection metadata can be created and listed.
- MCP reachability can be tested.
- A registered MCP tool can be executed.
- Automated tests and lint checks pass.