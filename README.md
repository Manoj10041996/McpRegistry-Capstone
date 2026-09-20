# MCP Registry and Connections

A FastAPI backend that provides a central registry for Model Context Protocol (MCP) servers.

The application can:

- Register an MCP server.
- Connect to the MCP endpoint.
- Discover the tools provided by that server.
- Store server and tool metadata in PostgreSQL.
- Search registered MCP servers.
- Create connection metadata.
- Test whether a connection can reach its MCP server.
- Execute a registered MCP tool.
- Reject duplicate records.
- Roll back incomplete database operations.
- Run locally with Docker.
- Run automated API tests.
- Build and deploy through GitHub Actions and Google Cloud Run.

---

## 1. Problem Being Solved

Different developers may create or register the same MCP integration multiple times.

This causes:

- Duplicate development work.
- Duplicate MCP server records.
- Difficulty finding existing tools.
- Inconsistent connection configuration.
- Unclear ownership of stored integration metadata.

This project provides one central registry where:

1. An MCP server is registered once.
2. Its tools are discovered automatically.
3. Server and tool metadata are saved in PostgreSQL.
4. Existing integrations can be searched.
5. Connection metadata can be created.
6. The saved connection can be tested.
7. Registered MCP tools can be executed through the API.

---

## 2. Current Project Status

| Capability | Status |
|---|---|
| FastAPI application | Implemented |
| Health endpoint | Implemented |
| Local PostgreSQL database | Implemented |
| Alembic migrations | Implemented |
| MCP server registration | Implemented |
| MCP tool discovery | Implemented |
| Server retrieval | Implemented |
| Server listing and search | Implemented |
| Duplicate server protection | Implemented |
| Transaction rollback | Verified |
| Concurrent duplicate protection | Verified |
| Connection creation | Implemented |
| Connection listing | Implemented |
| Connection testing | Implemented |
| MCP tool invocation | Implemented |
| Automated API tests | Implemented |
| Docker image build | Implemented |
| GitHub Actions CI/CD | Implemented |
| Cloud Run health endpoint | Working |
| Cloud PostgreSQL database | Not configured |
| Cloud MCP server | Not configured |
| Authentication and authorization | Not implemented |
| Secret manager integration | Not implemented |

---

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI web server |
| MCP Python SDK | MCP discovery and tool execution |
| PostgreSQL 17 | Persistent database |
| SQLAlchemy Async | Asynchronous database operations |
| asyncpg | PostgreSQL async driver |
| Alembic | Database schema migrations |
| Pydantic | Request and response validation |
| Docker Compose | Local PostgreSQL startup |
| pytest | Automated testing |
| Ruff | Python syntax and undefined-name checks |
| uv | Python environment and dependency management |
| GitHub Actions | Continuous integration and deployment |
| Google Artifact Registry | Docker image storage |
| Google Cloud Run | Cloud application hosting |

---

## 4. Backend Architecture

The backend is separated into layers.

### API layer

File:

```text
app/registry/routes.py
```

Responsibilities:

- Defines HTTP endpoints.
- Reads request data.
- Validates path and query parameters.
- Calls discovery, repository, and tool execution functions.
- Converts internal failures into HTTP responses.

### Validation layer

File:

```text
app/registry/schemas.py
```

Responsibilities:

- Defines request models.
- Defines response models.
- Removes unwanted surrounding spaces.
- Rejects unknown request fields.
- Validates names, URLs, IDs, and arguments.

### MCP discovery layer

File:

```text
app/registry/discovery.py
```

Responsibilities:

- Connects to an MCP endpoint.
- Starts an MCP client session.
- Requests the available tools.
- Returns tool names, descriptions, and input schemas.

### Server repository layer

File:

```text
app/registry/repository.py
```

Responsibilities:

- Saves MCP servers.
- Saves discovered tools.
- Reads one registered server.
- Lists registered servers.
- Searches by server name, endpoint, or tool name.
- Handles database transactions.
- Detects duplicate server registrations.

### Connection repository layer

File:

```text
app/registry/connection_repository.py
```

Responsibilities:

- Creates connection metadata.
- Lists connections for a server.
- Verifies that the server exists.
- Rejects duplicate connections.
- Reads the endpoint needed for testing and tool execution.

### Tool execution layer

File:

```text
app/registry/tool_runner.py
```

Responsibilities:

- Connects to the registered MCP endpoint.
- Calls the requested MCP tool.
- Sends the supplied arguments.
- Returns structured tool output.
- Reports whether the MCP tool returned an error.

### Database configuration layer

File:

```text
app/registry/database.py
```

Responsibilities:

- Reads database configuration.
- Creates the asynchronous SQLAlchemy engine.
- Makes the engine available to API routes.
- Disposes of the engine during shutdown.
- Returns HTTP 503 when database configuration is unavailable.

### Application entry point

File:

```text
app/main.py
```

Responsibilities:

- Creates the FastAPI application.
- Includes the registry router.
- Provides the `/health` endpoint.

---

## 5. Project Structure

```text
McpRegistry-Capstone/
│
├── app/
│   ├── main.py
│   └── registry/
│       ├── __init__.py
│       ├── connection_repository.py
│       ├── database.py
│       ├── discovery.py
│       ├── repository.py
│       ├── routes.py
│       ├── schemas.py
│       └── tool_runner.py
│
├── examples/
│   └── demo_mcp_server.py
│
├── migrations/
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       ├── c70e07595102_create_registry_tables.py
│       ├── d19c4f2a8b01_unique_registry_endpoint.py
│       └── efbbd3fa0c10_create_mcp_connections.py
│
├── scripts/
│   ├── check_database.py
│   ├── check_registry_concurrency.py
│   ├── check_registry_rollback.py
│   └── discover_demo_tools.py
│
├── tests/
│   └── test_api.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env
├── .gitignore
├── alembic.ini
├── compose.yaml
├── DEMO.md
├── Dockerfile
├── pyproject.toml
├── start_local.cmd
├── uv.lock
└── README.md
```

---

## 6. Main Request Workflows

### 6.1 Registering an MCP Server

Request:

```text
POST /registry/servers
```

Processing order:

1. FastAPI receives the server name and endpoint.
2. Pydantic validates the request.
3. The endpoint is checked against the allowed demo endpoint.
4. The application connects to the MCP server.
5. The MCP server returns its tool catalog.
6. The application validates the discovered tools.
7. A database transaction begins.
8. The MCP server record is inserted.
9. All discovered tool records are inserted.
10. The transaction is committed.
11. The saved server and tools are returned.

If any database insert fails, the complete transaction is rolled back.

That means the database stores either:

- The complete server and all tools, or
- Nothing from that registration attempt.

It does not keep an incomplete registration.

---

### 6.2 Reading a Registered Server

Request:

```text
GET /registry/servers/{server_id}
```

Processing order:

1. FastAPI validates that `server_id` is greater than zero.
2. The repository searches PostgreSQL.
3. The server and its stored tools are loaded.
4. A complete response is returned.
5. HTTP 404 is returned when the record does not exist.

This endpoint reads stored metadata.

The original MCP server does not need to be online because the tool information was stored during registration.

---

### 6.3 Listing and Searching Servers

Request:

```text
GET /registry/servers
```

Optional query parameters:

| Parameter | Purpose |
|---|---|
| `q` | Search text |
| `after_id` | Cursor for the next page |
| `limit` | Maximum number of results |

Examples:

```text
GET /registry/servers
GET /registry/servers?q=count_characters
GET /registry/servers?q=Demo
GET /registry/servers?after_id=1&limit=20
```

Search can match saved server or tool information.

A search with no matching record returns:

```json
{
  "items": [],
  "next_after_id": null
}
```

Invalid values such as `limit=0` return HTTP 422 because the allowed minimum is 1.

---

### 6.4 Creating a Connection

Request:

```text
POST /registry/servers/{server_id}/connections
```

Processing order:

1. FastAPI validates the server ID.
2. Pydantic validates the connection request.
3. The repository verifies that the registered server exists.
4. The repository checks for an existing connection.
5. The connection metadata is saved.
6. The API returns HTTP 201.

Example request:

```json
{
  "name": "Demo connection",
  "secret_ref": "local/demo-token"
}
```

The response does not return the secret reference.

Instead, it returns:

```json
{
  "id": 1,
  "server_id": 1,
  "name": "Demo connection",
  "created_at": "2026-09-15T18:25:04.853314Z",
  "credential_configured": true
}
```

`credential_configured: true` means a secret reference was supplied.

It does not mean that a real secret manager has already been connected.

---

### 6.5 Listing Connections

Request:

```text
GET /registry/servers/{server_id}/connections
```

The endpoint:

1. Verifies that the server exists.
2. Reads its saved connections.
3. Returns connection metadata.
4. Does not expose the stored `secret_ref`.

---

### 6.6 Testing a Connection

Request:

```text
POST /registry/servers/{server_id}/connections/{connection_id}/test
```

Processing order:

1. The application checks the server and connection IDs.
2. It reads the saved MCP endpoint.
3. It connects to the MCP server.
4. It requests the available tools.
5. It returns reachability information.

Example response:

```json
{
  "connection_id": 1,
  "server_id": 1,
  "reachable": true,
  "tool_count": 1
}
```

A successful test proves that the application reached the MCP server and received its tool catalog.

---

### 6.7 Executing an MCP Tool

Request:

```text
POST /registry/servers/{server_id}/connections/{connection_id}/tools/{tool_name}
```

Example request:

```json
{
  "arguments": {
    "text": "hello"
  }
}
```

Processing order:

1. FastAPI validates the IDs and tool name.
2. The application verifies the registered server.
3. It verifies the connection.
4. It verifies that the requested tool was registered.
5. It connects to the MCP server.
6. It sends the tool name and arguments.
7. It receives the MCP result.
8. It returns structured output.

Example response:

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

If required tool arguments are missing, the MCP server can return:

```json
{
  "connection_id": 1,
  "tool_name": "count_characters",
  "is_error": true,
  "structured_content": null
}
```

---

## 7. Database Design

The project currently uses three main application tables and one Alembic table.

### `mcp_servers`

Stores registered MCP servers.

Important columns:

| Column | Purpose |
|---|---|
| `id` | Server identifier |
| `company_id` | Separates company records |
| `name` | Display name |
| `endpoint` | MCP endpoint URL |
| `created_at` | Registration time |

Important rules:

- The name cannot be blank.
- The same endpoint cannot be registered twice for the same company.
- `company_id` is indexed for faster filtering.

---

### `mcp_tools`

Stores tools discovered from an MCP server.

Important columns:

| Column | Purpose |
|---|---|
| `id` | Tool record identifier |
| `server_id` | Parent MCP server |
| `name` | MCP tool name |
| `description` | Tool description |
| `input_schema` | JSON input schema |

Important rules:

- `server_id` references `mcp_servers.id`.
- Tool schema is stored as PostgreSQL JSONB.
- The same tool name cannot be stored twice under one server.

---

### `mcp_connections`

Stores connection metadata.

Important columns:

| Column | Purpose |
|---|---|
| `id` | Connection identifier |
| `company_id` | Company identifier |
| `server_id` | Registered MCP server |
| `name` | Connection name |
| `secret_ref` | Reference to credential storage |
| `created_at` | Creation time |

Important rules:

- The referenced MCP server must exist.
- Duplicate connection records are rejected.
- API responses do not expose `secret_ref`.

---

### `alembic_version`

Created and managed by Alembic.

It stores the migration revision currently applied to PostgreSQL.

Current migration head:

```text
efbbd3fa0c10
```

---

## 8. Alembic Migrations

Alembic records controlled database structure changes.

The migration history is:

### First migration

```text
c70e07595102_create_registry_tables.py
```

Creates:

- `mcp_servers`
- `mcp_tools`
- Foreign keys
- Indexes
- Tool uniqueness rules

### Second migration

```text
d19c4f2a8b01_unique_registry_endpoint.py
```

Adds database-level duplicate endpoint protection.

### Third migration

```text
efbbd3fa0c10_create_mcp_connections.py
```

Creates the MCP connection table and its constraints.

Check the available migration head:

```cmd
uv run alembic heads
```

Check the migration applied to the database:

```cmd
uv run alembic current
```

Apply all pending migrations:

```cmd
uv run alembic upgrade head
```

Expected current result:

```text
efbbd3fa0c10 (head)
```

---

## 9. Requirements

Install the following before running locally:

- Git
- Python supported by the project
- uv
- Docker Desktop
- Docker Compose
- A command prompt or PowerShell terminal

Verify the tools:

```cmd
git --version
uv --version
docker version
docker compose version
```

Docker Desktop must be running before starting PostgreSQL.

---

## 10. Local Installation

Open Command Prompt and move into the repository:

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
```

Install the locked dependencies:

```cmd
uv sync --frozen
```

If the lock file is intentionally being updated, use:

```cmd
uv sync
```

---

## 11. Environment Configuration

Create a `.env` file in the repository root.

Example:

```env
POSTGRES_PASSWORD=choose_a_local_password
```

The local defaults used by the application are:

| Setting | Default |
|---|---|
| Database user | `registry_admin` |
| Database name | `mcp_registry` |
| Database host | `127.0.0.1` |
| Database port | `55432` |

Do not commit `.env`.

Do not commit:

- Database passwords
- API keys
- Cloud service-account keys
- Tokens
- Private credentials

---

## 12. Start PostgreSQL

Start Docker Desktop first.

Then run:

```cmd
docker compose up -d --wait db
```

Confirm that PostgreSQL is healthy:

```cmd
docker compose ps
```

Expected port mapping:

```text
127.0.0.1:55432 -> 5432
```

Test PostgreSQL directly:

```cmd
docker compose exec db psql -U registry_admin -d mcp_registry -c "SELECT current_database(), current_user;"
```

Expected result:

```text
mcp_registry | registry_admin
```

Test the application database connection:

```cmd
uv run python -m scripts.check_database
```

Expected result:

```text
('mcp_registry', 'registry_admin')
```

---

## 13. Apply Database Migrations

Run:

```cmd
uv run alembic upgrade head
```

Verify:

```cmd
uv run alembic current
```

Expected result:

```text
efbbd3fa0c10 (head)
```

View the created tables:

```cmd
docker compose exec db psql -U registry_admin -d mcp_registry -c "\dt"
```

The list should include:

```text
alembic_version
mcp_servers
mcp_tools
mcp_connections
```

---

## 14. Start the Demo MCP Server

Open a separate Command Prompt.

Run:

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
uv run python examples\demo_mcp_server.py
```

Expected output:

```text
Uvicorn running on http://127.0.0.1:8001
```

The MCP endpoint is:

```text
http://127.0.0.1:8001/mcp
```

The demo MCP server provides:

```text
count_characters
```

The tool accepts text and returns its character count.

The demo MCP server does not provide normal web pages for:

```text
/
```

```text
/docs
```

```text
/health
```

Therefore, HTTP 404 responses for those browser paths are expected.

They do not mean the MCP endpoint is broken.

---

## 15. Start the FastAPI Application

Open another Command Prompt.

Run:

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

If port 8000 is already occupied, use another port:

```cmd
uv run uvicorn app.main:app --reload --port 8010
```

Then use:

```text
http://127.0.0.1:8010
```

---

## 16. Local Processes

A complete local demonstration normally requires three running services:

| Service | Port | Purpose |
|---|---:|---|
| PostgreSQL | 55432 | Stores registry data |
| FastAPI | 8000 or 8010 | Provides REST endpoints |
| Demo MCP server | 8001 | Provides the sample MCP tool |

Use separate command windows because the FastAPI and MCP processes remain running while accepting requests.

Closing their command windows stops those processes.

PostgreSQL continues inside Docker until it is stopped.

---

## 17. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application health |
| POST | `/registry/discover` | Discover MCP tools without saving |
| POST | `/registry/servers` | Register a server and its tools |
| GET | `/registry/servers` | List or search servers |
| GET | `/registry/servers/{server_id}` | Read one saved server |
| POST | `/registry/servers/{server_id}/connections` | Create connection metadata |
| GET | `/registry/servers/{server_id}/connections` | List connections |
| POST | `/registry/servers/{server_id}/connections/{connection_id}/test` | Test MCP reachability |
| POST | `/registry/servers/{server_id}/connections/{connection_id}/tools/{tool_name}` | Execute an MCP tool |

---

## 18. API Verification Commands

The following examples use Windows Command Prompt quoting.

### Check health

```cmd
curl.exe --noproxy "*" -i http://127.0.0.1:8000/health
```

### Discover demo tools

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/discover" -H "Content-Type: application/json" -d "{\"name\":\"Demo MCP\",\"endpoint\":\"http://127.0.0.1:8001/mcp\"}"
```

### Register the demo MCP server

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers" -H "Content-Type: application/json" -d "{\"name\":\"Demo MCP\",\"endpoint\":\"http://127.0.0.1:8001/mcp\"}"
```

### List registered servers

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers"
```

### Search by tool name

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers?q=count_characters"
```

### Read server 1

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers/1"
```

### Create a connection

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections" -H "Content-Type: application/json" -d "{\"name\":\"Demo connection\",\"secret_ref\":\"local/demo-token\"}"
```

### List connections

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers/1/connections"
```

### Test connection 1

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections/1/test"
```

### Execute `count_characters`

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections/1/tools/count_characters" -H "Content-Type: application/json" -d "{\"arguments\":{\"text\":\"hello\"}}"
```

Expected tool result:

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

If FastAPI is running on port 8010, replace `8000` with `8010`.

---

## 19. HTTP Response Meanings

| Status | Meaning in This Project |
|---:|---|
| 200 | Request completed successfully |
| 201 | New record created successfully |
| 403 | MCP endpoint is not permitted |
| 404 | Server, connection, or tool not found |
| 409 | Duplicate server or connection |
| 422 | Request validation failed |
| 502 | MCP server could not be reached or discovery failed |
| 503 | Registry database is unavailable or not configured |
| 504 | MCP operation exceeded its timeout |

---

## 20. Duplicate Protection

Duplicate checks exist in application code and PostgreSQL constraints.

For server registration:

```text
company_id + endpoint
```

must be unique.

For tool storage:

```text
server_id + tool name
```

must be unique.

For connection creation, the configured connection identity must also be unique according to the database rule.

If the same server is registered again, the API returns:

```json
{
  "detail": "This MCP endpoint is already registered for the demo company."
}
```

with HTTP 409.

Database constraints are important because two requests can arrive almost simultaneously.

Application-only checking is not enough to stop that race condition.

---

## 21. Transaction Rollback

Server and tool records are saved inside one database transaction.

Example failure:

1. The server insert succeeds.
2. One tool insert succeeds.
3. Another tool insert violates a database rule.
4. PostgreSQL rejects that insert.
5. The transaction is rolled back.
6. The server and earlier tool inserts are removed.

This prevents incomplete registration data.

Run the rollback verification:

```cmd
uv run python -m scripts.check_registry_rollback
```

Expected output:

```text
PASS: PostgreSQL rejected the duplicate tool.
PASS: The server insert was rolled back.
PASS: No partial registration remains.
```

---

## 22. Concurrent Duplicate Protection

Two registration requests may arrive at nearly the same time.

Both requests can initially believe that the endpoint is not registered.

The PostgreSQL unique constraint makes the final decision.

Expected result:

- One request succeeds.
- The competing request is rejected.
- Exactly one server is stored.
- Exactly one copy of its tool is stored.

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

---

## 23. Verification Scripts

Do not run:

```cmd
uv run python -m scripts
```

The `scripts` directory does not contain a `__main__.py` entry point.

Run the individual modules.

### Database check

```cmd
uv run python -m scripts.check_database
```

### MCP discovery check

```cmd
uv run python -m scripts.discover_demo_tools
```

### Rollback check

```cmd
uv run python -m scripts.check_registry_rollback
```

### Concurrency check

```cmd
uv run python -m scripts.check_registry_concurrency
```

---

## 24. Automated Tests

Automated API tests are located in:

```text
tests/test_api.py
```

Run:

```cmd
uv run python -m pytest -q
```

The verified result was:

```text
7 passed
```

A Starlette or AnyIO deprecation warning may appear.

That warning comes from a dependency and does not mean the tests failed.

Use:

```cmd
uv run python -m pytest -q
```

instead of:

```cmd
uv run pytest -q
```

Using `python -m pytest` ensures the repository root is available on Python's import path.

---

## 25. Lint Checks

Run syntax and undefined-name checks:

```cmd
uv run --with ruff ruff check app tests scripts migrations --select E9,F
```

Expected result:

```text
All checks passed!
```

---

## 26. Git Checks

Check modified files:

```cmd
git status --short
```

Check unstaged whitespace problems:

```cmd
git diff --check
```

Check staged whitespace problems:

```cmd
git diff --cached --check
```

Check the most recent commit:

```cmd
git show --check --oneline HEAD
```

A command returning no whitespace error means the check passed.

Messages about LF being replaced by CRLF are Windows line-ending warnings. They are not application failures.

---

## 27. GitHub Actions CI/CD

Workflow file:

```text
.github/workflows/ci.yml
```

The workflow runs after code is pushed to `main`.

### Check stage

The workflow:

1. Downloads the repository.
2. Installs uv.
3. Installs Python.
4. Installs locked dependencies.
5. Runs Ruff.
6. Imports the FastAPI application.
7. Runs automated API tests.
8. Builds a Docker image as a sanity check.

### Deployment stage

If all checks pass, the workflow:

1. Authenticates with Google Cloud.
2. Configures Docker for Artifact Registry.
3. Builds the deployment image.
4. Tags the image with the commit SHA.
5. Tags another copy as `latest`.
6. Pushes the image to Artifact Registry.
7. Deploys the commit image to Cloud Run.
8. Displays the deployed service URL.

A GitHub secret named:

```text
GCP_SA_KEY
```

provides Google Cloud authentication.

The credential file must never be committed to Git.

---

## 28. Cloud Deployment

Current Cloud Run URL:

```text
https://agent-platform-vifyudmsaa-uc.a.run.app
```

Health check:

```cmd
curl.exe -i https://agent-platform-vifyudmsaa-uc.a.run.app/health
```

Expected response:

```json
{
  "status": "ok"
}
```

The cloud service currently starts without PostgreSQL configuration.

Therefore:

```cmd
curl.exe -i https://agent-platform-vifyudmsaa-uc.a.run.app/registry/servers
```

currently returns HTTP 503:

```json
{
  "detail": "Registry database is not configured."
}
```

This is intentional controlled behavior.

The application remains healthy instead of crashing during startup.

---

## 29. Cloud Startup Failure That Was Fixed

The first Cloud Run deployment failed during application startup.

The original database code required:

```python
os.environ["POSTGRES_PASSWORD"]
```

Cloud Run did not have that environment variable.

Python raised:

```text
KeyError: 'POSTGRES_PASSWORD'
```

Because startup failed, Uvicorn never completed startup and Cloud Run could not detect a process listening on port 8000.

The database configuration was changed so that:

1. The password is read safely.
2. Missing cloud database configuration returns no engine.
3. FastAPI is still allowed to start.
4. `/health` returns HTTP 200.
5. Registry endpoints return HTTP 503.

This separates application health from database availability.

Local development continues to use the password from `.env`.

---

## 30. Common Problems and Fixes

### Port 8001 is already occupied

Check:

```cmd
netstat -ano | findstr LISTENING | findstr /C:":8001 "
```

The final number is the process ID.

Stop only the confirmed MCP process:

```cmd
taskkill /PID PROCESS_ID /F
```

Do not stop an unknown process without checking it.

---

### Port 8000 is occupied by another application

Use another port:

```cmd
uv run uvicorn app.main:app --reload --port 8010
```

This avoids disturbing the application already using port 8000.

---

### MCP discovery returns HTTP 502

Check whether port 8001 is listening:

```cmd
netstat -ano | findstr LISTENING | findstr /C:":8001 "
```

Start the demo MCP server if no result appears:

```cmd
uv run python examples\demo_mcp_server.py
```

---

### Registration returns HTTP 409

The endpoint is already registered.

Read the existing record or search the registry instead of registering it again.

---

### Connection creation returns HTTP 404

The requested registered server ID does not exist.

List servers first:

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers"
```

Use an existing server ID.

---

### Tool request returns HTTP 422

In Windows Command Prompt, JSON double quotes must be escaped:

```cmd
-d "{\"arguments\":{\"text\":\"hello\"}}"
```

Single-quote behavior differs between Command Prompt and PowerShell.

---

### Docker reports no Compose configuration

Confirm that the terminal is inside:

```text
C:\capstone-MCPRegistry\McpRegistry-Capstone
```

Then run:

```cmd
docker compose up -d --wait db
```

---

### Alembic cannot find `script_location`

Confirm that `alembic.ini` exists in the repository root.

---

### Alembic cannot find a revision

Confirm that all migration files exist under:

```text
migrations/versions/
```

The current chain requires:

```text
c70e07595102
d19c4f2a8b01
efbbd3fa0c10
```

---

### `POSTGRES_PASSWORD` is missing

Confirm `.env` exists and contains:

```env
POSTGRES_PASSWORD=your_local_password
```

Do not add extra spaces around the key name.

---

### `.pyc` files appear in VS Code

Files under `__pycache__` are generated Python bytecode.

They are not source code.

Do not edit them.

The real source files end with:

```text
.py
```

Generated cache files should remain ignored by Git.

---

## 31. Security Behavior

The implementation already provides:

- Input validation.
- Unknown-field rejection.
- Allowed-endpoint restriction for the demo.
- Discovery timeout handling.
- Tool catalog count limit.
- Tool metadata size limit.
- Duplicate server protection.
- Duplicate connection protection.
- Database transaction rollback.
- Controlled database-unavailable response.
- Responses that do not expose `secret_ref`.
- Ignoring local environment files and credential files.

---

## 32. Current Limitations

This is a functional proof of concept, not a complete production service.

Current limitations:

1. A fixed demo company ID is used.
2. Only the local demo MCP endpoint is allowed.
3. Real user authentication is not implemented.
4. Authorization roles are not implemented.
5. `secret_ref` is stored, but no cloud secret manager resolves it.
6. Tool execution does not yet inject real credentials.
7. Cloud PostgreSQL is not configured.
8. The demo MCP server is not deployed in the cloud.
9. Cloud registry endpoints currently return HTTP 503.
10. Update and delete endpoints are not implemented.
11. Connection update and deletion are not implemented.
12. Audit logging is not implemented.
13. Rate limiting is not implemented.
14. Tool execution history is not stored.
15. Production monitoring and alerting are not configured.

These limitations should be stated clearly during a demonstration.

---

## 33. Production Improvements

The next production-level improvements are:

### Identity

- Add user authentication.
- Read company identity from authenticated claims.
- Remove the fixed demo company ID.

### Authorization

- Define who can register servers.
- Define who can create connections.
- Define who can execute tools.
- Apply authorization checks to every protected endpoint.

### Credential security

- Store actual secrets in Google Secret Manager or another approved secret store.
- Save only the secret identifier in PostgreSQL.
- Resolve credentials only during an authorized request.
- Prevent credentials from appearing in logs or responses.
- Add credential rotation.

### Cloud database

- Create a managed PostgreSQL instance.
- Use private networking or an approved secure connector.
- Store database credentials in Secret Manager.
- Run Alembic migrations during a controlled release.
- Configure backup and recovery.

### MCP deployment

- Deploy an accessible MCP server.
- Replace the fixed local endpoint rule.
- Add an endpoint approval policy.
- Add SSRF protection.
- Restrict private and metadata-network access.
- Add TLS verification.

### Reliability

- Add retries only for safe operations.
- Add structured logs.
- Add request identifiers.
- Add metrics and alerts.
- Add tool execution timeouts.
- Add request-size and concurrency limits.

### Testing

- Add PostgreSQL integration tests.
- Add MCP integration tests.
- Add migration tests.
- Add concurrent API tests.
- Add failure and timeout tests.
- Add Cloud Run smoke tests after deployment.

---

## 34. Complete Local Demonstration Order

Use this order for a clean demonstration.

### Command Prompt 1: PostgreSQL

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
docker compose up -d --wait db
uv run alembic upgrade head
uv run python -m scripts.check_database
```

### Command Prompt 2: Demo MCP server

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
uv run python examples\demo_mcp_server.py
```

Keep this window open.

### Command Prompt 3: FastAPI

```cmd
cd /d C:\capstone-MCPRegistry\McpRegistry-Capstone
uv run uvicorn app.main:app --reload --port 8000
```

Keep this window open.

### Command Prompt 4: API requests

First check health:

```cmd
curl.exe --noproxy "*" -i http://127.0.0.1:8000/health
```

Register the MCP server if it is not already registered:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers" -H "Content-Type: application/json" -d "{\"name\":\"Demo MCP\",\"endpoint\":\"http://127.0.0.1:8001/mcp\"}"
```

List servers:

```cmd
curl.exe --noproxy "*" -i "http://127.0.0.1:8000/registry/servers"
```

Create a connection if one does not already exist:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections" -H "Content-Type: application/json" -d "{\"name\":\"Demo connection\",\"secret_ref\":\"local/demo-token\"}"
```

Test the connection:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections/1/test"
```

Execute the tool:

```cmd
curl.exe --noproxy "*" -i -X POST "http://127.0.0.1:8000/registry/servers/1/connections/1/tools/count_characters" -H "Content-Type: application/json" -d "{\"arguments\":{\"text\":\"hello\"}}"
```

Run automated tests:

```cmd
uv run python -m pytest -q
```

Run lint checks:

```cmd
uv run --with ruff ruff check app tests scripts migrations --select E9,F
```

---

## 35. Stopping the Local Environment

Stop FastAPI with:

```text
CTRL+C
```

Stop the demo MCP server with:

```text
CTRL+C
```

Stop PostgreSQL:

```cmd
docker compose stop db
```

Start it again later:

```cmd
docker compose up -d --wait db
```

Stopping the container does not delete the database volume.

---

## 36. Final Result

The current implementation proves the complete local MCP registry flow:

1. PostgreSQL starts.
2. Alembic creates the database structure.
3. The demo MCP server exposes a tool.
4. FastAPI discovers that tool.
5. The registry saves the server and tool metadata.
6. Duplicate registrations are rejected.
7. Saved metadata remains readable while the MCP server is offline.
8. Failed database writes are rolled back.
9. Concurrent duplicate requests store only one record.
10. Connection metadata can be created and listed.
11. A saved connection can be tested.
12. A registered MCP tool can be executed.
13. Automated API tests verify expected behavior.
14. GitHub Actions validates and deploys the application.
15. Cloud Run stays healthy when cloud database configuration is absent.

The project is ready as a working proof of concept and clearly identifies the remaining work required for production deployment.