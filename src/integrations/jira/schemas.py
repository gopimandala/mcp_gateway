from pydantic import BaseModel, Field, model_validator


class JiraIssue(BaseModel):
    key: str = Field(..., description="The Jira issue key (e.g., PROJ-123)")
    summary: str = Field(..., description="Brief summary of the issue")
    status: str = Field(..., description="Current workflow status")
    description: str = Field(default="No description provided.")

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, data):
        if not isinstance(data, dict):
            return data

        fields = data.get("fields", {})

        return {
            "key": data.get("key"),
            "summary": fields.get("summary"),
            "status": (fields.get("status") or {}).get("name"),
            "description": fields.get("description") or "No description provided.",
        }


class JiraComment(BaseModel):
    issue_key: str = Field(..., description="The Jira issue key")
    comment_id: str = Field(..., description="The comment ID")
    body: str = Field(..., description="The comment text content")

    @model_validator(mode="before")
    @classmethod
    def extract_fields(cls, data):
        if not isinstance(data, dict):
            return data

        body = ""
        comment_body = data.get("body", {})
        if isinstance(comment_body, dict):
            content = comment_body.get("content", [])
            if content and isinstance(content, list):
                for content_item in content:
                    if isinstance(content_item, dict):
                        nested_content = content_item.get("content", [])
                        if nested_content and isinstance(nested_content, list):
                            for text_item in nested_content:
                                if isinstance(text_item, dict) and text_item.get("type") == "text":
                                    body += text_item.get("text", "")

        return {
            "issue_key": data.get("issue_key", ""),
            "comment_id": data.get("id", ""),
            "body": body
        }