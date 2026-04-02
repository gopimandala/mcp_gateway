# brain/brain.py
import asyncio
import json
import aiohttp
from openai import OpenAI
from dotenv import load_dotenv
import os

# --- load environment ---
load_dotenv()

# --- brain configuration ---
from config import brain_settings

OPENAI_KEY = brain_settings.openai_key
client = OpenAI(api_key=OPENAI_KEY)

MCP_GATEWAY_URL = brain_settings.mcp_gateway_url
TOOLS_URL = f"{MCP_GATEWAY_URL}/api/jira/tools"

# fetch tools dynamically
async def fetch_tools():
    async with aiohttp.ClientSession() as session:
        async with session.get(TOOLS_URL) as resp:
            return await resp.json()

# load prompts
def load_prompt(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()

# run LLM brain
async def run_brain(user_request: str):
    tools = await fetch_tools()
    tools_json = json.dumps(tools)
    print("Tools received by brain:", tools)

    system_prompt = load_prompt("system_prompt.md")
    user_prompt_template = load_prompt("user_prompt.md")
    user_prompt = user_prompt_template.format(user_request=user_request, tools_json=tools_json)

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    plan_str = resp.choices[0].message.content.strip()

    # remove ```json blocks if present
    if plan_str.startswith("```"):
        plan_str = "\n".join(plan_str.split("\n")[1:-1]).strip()

    try:
        plan = json.loads(plan_str)
    except Exception:
        print("Failed to parse LLM output:", plan_str)
        return None

    return plan, tools

# execute plan via MCP wrapper endpoints
async def execute_plan(plan, tools_list):
    tools_map = {t["name"]: t for t in tools_list}

    async with aiohttp.ClientSession() as session:
        for step in plan:
            tool_name = step["tool"]
            input_data = step["input"]

            tool_meta = tools_map.get(tool_name)
            if not tool_meta:
                print("Unknown tool:", tool_name)
                continue

            url = f"{MCP_GATEWAY_URL}{tool_meta['wrapper_path']}"
            # method = tool_meta.get("method", "POST").upper()
            method = "POST"

            async with session.request(method, url, json=input_data) as resp:
                try:
                    result = await resp.json()
                except Exception:
                    result = await resp.text()
                print(f"Executed {tool_name} ({method} {url}):", result)

# main
async def main():
    user_request = "Check KAN-30 and comment that it will be done in the next 4.5 hours"
    plan_tools = await run_brain(user_request)
    if plan_tools:
        plan, tools = plan_tools
        print("LLM Plan:", json.dumps(plan, indent=2))
        await execute_plan(plan, tools)

if __name__ == "__main__":
    asyncio.run(main())