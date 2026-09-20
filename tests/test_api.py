from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.registry import routes
from app.registry.database import get_registry_engine
from app.registry.schemas import (
    ExecuteToolResponse,
    ServerResponse,
    ToolMetadata,
)


@pytest.fixture
def client(monkeypatch):
    # Simulate Cloud Run without a configured database.
    monkeypatch.setenv("POSTGRES_PASSWORD", "")

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def database_client(client):
    # Route tests use a fake engine instead of PostgreSQL.
    app.dependency_overrides[get_registry_engine] = (
        lambda: object()
    )
    return client


def registered_server() -> ServerResponse:
    return ServerResponse(
        id=1,
        name="Demo MCP",
        endpoint="http://127.0.0.1:8001/mcp",
        created_at=datetime.now(timezone.utc),
        tools=[
            ToolMetadata(
                name="count_characters",
                description="Count supplied characters.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                    },
                    "required": ["text"],
                },
            )
        ],
    )


def test_health_is_available_without_database(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_registry_returns_503_without_database(client):
    response = client.get("/registry/servers")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Registry database is not configured."
    }


def test_discovery_rejects_unapproved_endpoint(client):
    response = client.post(
        "/registry/discover",
        json={
            "name": "External MCP",
            "endpoint": "https://example.com/mcp",
        },
    )

    assert response.status_code == 403


def test_request_rejects_extra_fields(client):
    response = client.post(
        "/registry/discover",
        json={
            "name": "Demo MCP",
            "endpoint": "http://127.0.0.1:8001/mcp",
            "unexpected": "value",
        },
    )

    assert response.status_code == 422


def test_unknown_server_cannot_execute_tool(
    database_client,
    monkeypatch,
):
    async def fake_read_server(*args, **kwargs):
        return None

    monkeypatch.setattr(
        routes,
        "read_server",
        fake_read_server,
    )

    response = database_client.post(
        (
            "/registry/servers/999/connections/1"
            "/tools/count_characters"
        ),
        json={"arguments": {"text": "hello"}},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Registered MCP server not found."
    }


def test_unknown_tool_cannot_be_executed(
    database_client,
    monkeypatch,
):
    async def fake_read_server(*args, **kwargs):
        return registered_server()

    monkeypatch.setattr(
        routes,
        "read_server",
        fake_read_server,
    )

    response = database_client.post(
        (
            "/registry/servers/1/connections/1"
            "/tools/unknown_tool"
        ),
        json={"arguments": {}},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Registered MCP tool not found."
    }


def test_registered_tool_can_be_executed(
    database_client,
    monkeypatch,
):
    async def fake_read_server(*args, **kwargs):
        return registered_server()

    async def fake_get_endpoint(*args, **kwargs):
        return "http://127.0.0.1:8001/mcp"

    async def fake_call_tool(**kwargs):
        return ExecuteToolResponse(
            connection_id=1,
            tool_name="count_characters",
            is_error=False,
            structured_content={"result": 5},
        )

    monkeypatch.setattr(
        routes,
        "read_server",
        fake_read_server,
    )
    monkeypatch.setattr(
        routes,
        "get_connection_endpoint",
        fake_get_endpoint,
    )
    monkeypatch.setattr(
        routes,
        "call_mcp_tool",
        fake_call_tool,
    )

    response = database_client.post(
        (
            "/registry/servers/1/connections/1"
            "/tools/count_characters"
        ),
        json={"arguments": {"text": "hello"}},
    )

    assert response.status_code == 200
    assert response.json() == {
        "connection_id": 1,
        "tool_name": "count_characters",
        "is_error": False,
        "structured_content": {"result": 5},
    }