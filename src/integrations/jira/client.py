import base64
import httpx
from fastapi import HTTPException
from shared.tracing_utils import secure_trace, scrub_pii
from src.core.config import settings
from .operations import JIRA_OPERATIONS
from .schemas import JiraIssue, JiraComment


class JiraClient:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.base_url = settings.jira_url.rstrip("/")

        auth_str = f"{settings.jira_email}:{settings.jira_api_key}"
        encoded = base64.b64encode(auth_str.encode()).decode()

        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @secure_trace(name="jira_client_execute")
    async def execute(self, operation: str, **params) -> dict:
        """
        Execute a Jira operation.
        Returns cleaned business fields only.
        PII is scrubbed in the trace.
        """
        if operation not in JIRA_OPERATIONS:
            raise ValueError(f"Unsupported Jira operation: {operation}")

        op = JIRA_OPERATIONS[operation]
        url = self.base_url + op["path"].format(**params)
        method = op["method"]

        try:
            if method == "GET":
                response = await self.client.get(url, headers=self.headers)
            elif method == "POST":
                body = params.get("body")
                response = await self.client.post(url, headers=self.headers, json=body)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status == 404:
                raise HTTPException(
                    status_code=404, detail="Jira issue not found or access denied"
                )
            raise HTTPException(status_code=status, detail="Jira API error")

        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Jira connection error")

        raw = response.json()

        # Build cleaned business output
        if operation == "get_issue":
            cleaned = JiraIssue.model_validate(raw).dict()
        elif operation == "add_comment":
            raw_with_key = {**raw, "issue_key": params.get("issue_key")}
            cleaned = JiraComment.model_validate(raw_with_key).dict()
        else:
            cleaned = {}

        # scrub PII before returning (and trace will also see this)
        return scrub_pii(cleaned)