from .schemas import JiraIssue


class JiraService:

    def __init__(self, jira_client):
        self.client = jira_client

    async def get_issue(self, issue_key: str):

        raw = await self.client.execute(
            "get_issue",
            issue_key=issue_key
        )

        return JiraIssue(**raw)

    async def add_comment(self, issue_key: str, comment: str):

        body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }

        result = await self.client.execute(
            "add_comment",
            issue_key=issue_key,
            body=body
        )

        return result