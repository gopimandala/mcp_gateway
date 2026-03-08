import base64
import httpx
from ...core.config import settings

class JiraClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.base_url = settings.jira_url.rstrip('/')
        
        # Pre-calculate Auth
        auth_str = f"{settings.jira_email}:{settings.jira_api_key}"
        encoded = base64.b64encode(auth_str.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json"
        }

    async def fetch_issue_raw(self, issue_key: str) -> dict:
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
        response = await self.client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
