from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RegisterServerRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
        max_length=100,
    )
    endpoint: HttpUrl


class ToolMetadata(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=128,
    )
    description: str | None = None
    input_schema: dict[str, Any]


class ServerResponse(BaseModel):
    id: int
    name: str
    endpoint: str
    created_at: datetime
    tools: list[ToolMetadata]


class ServerSummary(BaseModel):
    id: int
    name: str
    endpoint: str
    created_at: datetime
    tool_count: int


class ServerListResponse(BaseModel):
    items: list[ServerSummary]
    next_after_id: int | None


class CreateConnectionRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
        max_length=100,
    )
    secret_ref: str = Field(
        min_length=1,
        max_length=255,
    )


class ConnectionResponse(BaseModel):
    id: int
    server_id: int
    name: str
    created_at: datetime
    credential_configured: bool


class ConnectionTestResponse(BaseModel):
    connection_id: int
    server_id: int
    reachable: bool
    tool_count: int