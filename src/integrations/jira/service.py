import re
from .schemas import JiraIssue
from .client import JiraClient
from shared.tracing_utils import secure_trace

class JiraService:
    def __init__(self, client: JiraClient):
        self.client = client

    @secure_trace(name="Jira: Get Issue")
    async def get_issue(self, issue_key: str) -> JiraIssue:
        # 1. Input Validation
        issue_key = issue_key.strip().upper()
        if not re.match(r"^[A-Z0-9]+-\d+$", issue_key):
            raise ValueError(f"Invalid Jira key format: {issue_key}")

        # 2. Network Call via Client
        data = await self.client.fetch_issue_raw(issue_key)
        
        # 3. Data Transformation
        fields = data.get("fields", {})
        return JiraIssue(
            key=issue_key,
            summary=fields.get("summary", "N/A"),
            status=fields.get("status", {}).get("name", "Unknown"),
            description=fields.get("description") or "No description."
        )
