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

    class AddCommentRequest(BaseModel):
        issue_key: str
        comment: str

    @router.post("/issue")
    async def get_jira_issue(req: JiraIssueRequest):
        service = get_service()
        if not service:
            raise HTTPException(status_code=500, detail="Jira service not initialized")

        issue_obj = await service.get_issue(req.issue_key)

        return {
            "issue_key": req.issue_key,
            "details": issue_obj.model_dump()
        }

    @router.post("/comment")
    async def add_comment(req: AddCommentRequest):

        service = get_service()
        if not service:
            raise HTTPException(status_code=500, detail="Jira service not initialized")

        result = await service.add_comment(
            issue_key=req.issue_key,
            comment=req.comment
        )

        return {
            "issue_key": req.issue_key,
            "comment_id": result.get("id"),
            "comment_url": result.get("self")
        }

    return router