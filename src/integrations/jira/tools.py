from .service import JiraService


def register_jira_tools(server, jira_service: JiraService):

    @server.tool()
    async def get_issue(issue_key: str):
        """
        Get a Jira issue by key.
        """
        return await jira_service.get_issue(issue_key)