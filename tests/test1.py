# test1.py
import asyncio
from fastmcp import MCPClient

async def main():
    async with MCPClient("http://localhost:8020") as client:
        # Call the tool
        result = await client.call("jira_get_issue", issue_key="KAN-30")
        print(result)

# Run the async main function
asyncio.run(main())