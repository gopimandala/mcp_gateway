from typing import List, Dict
from .operations import JIRA_OPERATIONS
from .schemas import JiraIssue, JiraComment
from shared.tool_registry import ToolRegistryService


class JiraService(ToolRegistryService):
    """
    Jira MCP Service.
    Exposes tools dynamically.
    """
    OPERATIONS = JIRA_OPERATIONS

    def __init__(self, jira_client):
        self.client = jira_client

    async def get_issue(self, issue_key: str) -> Dict:
        """
        Fetch a Jira issue by key (only key business fields returned).
        """
        return await self.client.execute("get_issue", issue_key=issue_key)

    async def add_comment(self, issue_key: str, comment: str) -> Dict:
        """
        Add a comment to a Jira issue.
        Returns only key business fields: issue_key, comment_id, body.
        """
        body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment}]
                    }
                ]
            }
        }

        raw = await self.client.execute("add_comment", issue_key=issue_key, body=body)

        return raw
        
    def get_tools_list(self) -> List[Dict]:
        """
        Returns all tools exposed by this MCP server.
        """
        return [
            {
                "name": k,
                "description": v.get("description", ""),
                "method": v.get("method", ""),
                "path": v.get("path", ""),
                "wrapper_path": v.get("wrapper_path", "") 
            }
            for k, v in self.OPERATIONS.items()
        ]