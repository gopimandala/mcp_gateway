from fastmcp import FastMCP
from .service import JiraService
from shared.tracing_utils import secure_mcp_tool
from langchain_core.tracers.context import tracing_v2_enabled
from langchain_core.tracers.langchain import wait_for_all_tracers
from src.core.config import settings
from langsmith import Client

ls_client = Client() 

def register_jira_tools(mcp: FastMCP, get_service):
    """
    Registers Jira tools to the provided FastMCP instance.
    'get_service' is a functional way to access the DI container.
    """
    
    @mcp.tool(name="jira_get_issue")
    @secure_mcp_tool(name="jira_get_issue", service="jira-gateway")
    async def jira_get_issue(issue_key: str) -> str:
        """Retrieve details for a Jira issue (e.g., 'CORE-123')."""
        with tracing_v2_enabled(project_name=settings.langchain_project, client=ls_client):
            try:
                service: JiraService = get_service()
                issue = await service.get_issue(issue_key)
                return issue.model_dump_json()
            except Exception as e:
                return f"❌ Jira Error: {str(e)}"
            finally:
                # FORCE FLUSH: This ensures the trace is sent to LangSmith 
                # before the async task finishes.
                wait_for_all_tracers()
