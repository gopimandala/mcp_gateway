from pydantic import BaseModel, Field, model_validator


class JiraIssue(BaseModel):
    key: str = Field(..., description="The Jira issue key (e.g., PROJ-123)")
    summary: str = Field(..., description="Brief summary of the issue")
    status: str = Field(..., description="Current workflow status")
    description: str = Field(default="No description provided.")

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, data):
        """
        Transform Jira API payload into the flat structure
        expected by this schema.
        """
        if not isinstance(data, dict):
            return data

        fields = data.get("fields", {})

        return {
            "key": data.get("key"),
            "summary": fields.get("summary"),
            "status": (fields.get("status") or {}).get("name"),
            "description": fields.get("description") or "No description provided.",
        }