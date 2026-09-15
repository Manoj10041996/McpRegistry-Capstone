@echo off
cd /d "%~dp0"

echo Starting PostgreSQL...
docker compose up -d --wait db
if errorlevel 1 (
    echo PostgreSQL could not start. Check Docker Desktop.
    exit /b 1
)

netstat -ano | findstr LISTENING | findstr /C:":8001 " >nul
if errorlevel 1 (
    start "MCP - 8001" cmd /k "uv run python examples/demo_mcp_server.py"
) else (
    echo Port 8001 already has a listener. No second MCP process started.
)

netstat -ano | findstr LISTENING | findstr /C:":8000 " >nul
if errorlevel 1 (
    start "FastAPI - 8000" cmd /k "uv run uvicorn app.main:app --reload"
) else (
    echo Port 8000 already has a listener. No second FastAPI process started.
)

echo.
echo Wait for Application startup complete in any newly opened windows.
echo Then open http://127.0.0.1:8000/docs