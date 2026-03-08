# src/main_http_wrapper.py
import os
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI

from src.api.jira.jira_http_wrapper import create_jira_router
from src.integrations.jira.service import JiraService
from src.integrations.jira.client import JiraClient

load_dotenv()

services = {}
http_client = httpx.AsyncClient(timeout=15.0)  # <-- keep alive

async def init_services():
    """
    Initialize JiraService at startup, using persistent http_client
    """
    jira_service = JiraService(JiraClient(http_client))
    return {"jira": jira_service}

app = FastAPI(title="Jira HTTP Wrapper")

@app.on_event("startup")
async def startup_event():
    global services
    services = await init_services()

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()  # clean up on app shutdown

jira_router = create_jira_router(lambda: services.get("jira"))
app.include_router(jira_router, prefix="/api/jira", tags=["jira"])