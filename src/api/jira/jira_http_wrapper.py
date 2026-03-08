# src/api/jira/jira_http_wrapper.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

def create_jira_router(get_service):
    """
    Factory to create Jira HTTP wrapper router.
    get_service: function returning JiraService instance
    """
    router = APIRouter()

    class JiraIssueRequest(BaseModel):
        issue_key: str

    @router.post("/issue")
    async def get_jira_issue(req: JiraIssueRequest):
        service = get_service()
        if not service:
            raise HTTPException(status_code=500, detail="Jira service not initialized")

        # Call Jira service
        issue_obj = await service.get_issue(req.issue_key)
        return {
            "issue_key": req.issue_key,
            "details": issue_obj.model_dump()
        }

    return router