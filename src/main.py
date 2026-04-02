# src/main_mcp.py
import os
from dotenv import load_dotenv
import httpx
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastmcp import FastMCP

from src.core.config import settings
from src.integrations.jira.client import JiraClient
from src.integrations.jira.service import JiraService
from src.integrations.jira.tools import register_jira_tools

load_dotenv()

services: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(mcp: FastMCP):
    """
    MCP lifespan: initializes Jira service inside MCP lifecycle.
    """
    async with httpx.AsyncClient(timeout=15.0) as http_client:
        services["jira"] = JiraService(JiraClient(http_client))
        yield
    services.clear()

# Initialize MCP server
mcp = FastMCP("enterprise-gateway", lifespan=lifespan)

# Register Jira MCP tools
register_jira_tools(mcp, lambda: services.get("jira"))

# ASGI app for MCP
app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.mcp_port, reload=True)