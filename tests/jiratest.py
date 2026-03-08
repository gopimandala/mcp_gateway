#!/usr/bin/env python3
"""
One-shot Jira MCP test (compact)
"""

import asyncio
import httpx
import json

TARGET_URL = "http://127.0.0.1:8020/mcp"
JIRA_ISSUE_KEY = "KAN-61"

async def main():
    async with httpx.AsyncClient() as client:
        # 1️⃣ Get session ID
        session_id = (await client.get(TARGET_URL, headers={"Accept": "application/json, text/event-stream"})).headers.get("mcp-session-id")
        if not session_id:
            raise RuntimeError("No MCP session ID returned")

        # 2️⃣ Initialize session
        await client.post(
            TARGET_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "jira-test-client", "version": "1.0.0"}
                }
            },
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}
        )

        # 3️⃣ Call tool
        resp = await client.post(
            TARGET_URL,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "jira_get_issue", "arguments": {"issue_key": JIRA_ISSUE_KEY}}
            },
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "mcp-session-id": session_id}
        )

        # Parse SSE-style lines for JSON
        result = next(
            (json.loads(line.split("data:", 1)[1].strip()) for line in resp.text.splitlines() if line.strip().startswith("data:")),
            None
        )
        if not result:
            raise RuntimeError("No valid JSON in MCP response")

        # Print result
        if "result" in result:
            print("✅ Issue details:", result["result"])
        elif "error" in result:
            print("❌ Server error:", result["error"])
        else:
            print("⚠️ Unexpected response:", result)

if __name__ == "__main__":
    asyncio.run(main())