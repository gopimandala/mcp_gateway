import os
from dotenv import load_dotenv

load_dotenv()

import httpx
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastmcp import FastMCP

from src.core.config import settings
from src.integrations.jira.client import JiraClient
from src.integrations.jira.service import JiraService
from src.integrations.jira.tools import register_jira_tools # Import Tools

services: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(mcp: FastMCP):
    async with httpx.AsyncClient(timeout=15.0) as http_client:
        # Initialize Jira Domain
        jira_infra = JiraClient(http_client)
        services["jira"] = JiraService(jira_infra)
        yield
    services.clear()

mcp = FastMCP("enterprise-gateway", lifespan=lifespan)

# --- STANDARDIZED REGISTRATION ---
# We pass a lambda so the tool can 'look up' the service when called
register_jira_tools(mcp, lambda: services.get("jira"))

# Future: register_gitlab_tools(mcp, lambda: services.get("gitlab"))

app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9050)
