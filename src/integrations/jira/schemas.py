from pydantic import BaseModel, Field

class JiraIssue(BaseModel):
    key: str = Field(..., description="The Jira issue key (e.g., PROJ-123)")
    summary: str = Field(..., description="Brief summary of the issue")
    status: str = Field(..., description="Current workflow status")
    description: str = Field(default="No description provided.")
