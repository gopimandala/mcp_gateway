import base64
import httpx
from fastapi import HTTPException
from langsmith import get_current_run_tree

from ...core.config import settings
from shared.tracing_utils import secure_trace
from .operations import JIRA_OPERATIONS


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

    async def execute(self, operation: str, **params):

        if operation not in JIRA_OPERATIONS:
            raise ValueError(f"Unsupported Jira operation: {operation}")

        op = JIRA_OPERATIONS[operation]

        url = self.base_url + op["path"].format(**params)
        method = op["method"]

        @secure_trace(
            name=op["trace_name"],
            metadata={
                "service": "jira",
                "operation": operation,
            },
        )
        async def _call():

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

                status_code = exc.response.status_code

                if status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail="Jira issue not found or access denied",
                    )

                raise HTTPException(
                    status_code=status_code,
                    detail=f"Jira API error: {exc.response.text}",
                )

            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Jira connection error: {str(exc)}",
                )

            run_tree = get_current_run_tree()
            if run_tree:
                run_tree.metadata["status_code"] = response.status_code
                run_tree.metadata["latency_ms"] = response.elapsed.total_seconds() * 1000

                # Optional but extremely useful for debugging
                if "issue_key" in params:
                    run_tree.metadata["issue_key"] = params["issue_key"]

            return response.json()

        return await _call()