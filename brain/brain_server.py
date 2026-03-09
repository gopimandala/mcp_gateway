# brain_server.py
import asyncio
import json
import aiohttp
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# --- load environment ---
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# --- MCP/Kong config ---
MCP_GATEWAY_URL = "http://localhost:8000"
TOOLS_URL = f"{MCP_GATEWAY_URL}/api/jira/tools"

# --- FastAPI app ---
app = FastAPI(title="Brain Server")

# --- request model ---
class BrainRequest(BaseModel):
    user_request: str

# --- fetch tools dynamically ---
async def fetch_tools():
    async with aiohttp.ClientSession() as session:
        async with session.get(TOOLS_URL) as resp:
            return await resp.json()

# --- load prompts ---
def load_prompt(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()

# --- run LLM brain ---
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

# --- execute plan via MCP wrapper endpoints ---
async def execute_plan(plan, tools_list):
    tools_map = {t["name"]: t for t in tools_list}
    results = []

    async with aiohttp.ClientSession() as session:
        for step in plan:
            tool_name = step["tool"]
            input_data = step["input"]

            tool_meta = tools_map.get(tool_name)
            if not tool_meta:
                print("Unknown tool:", tool_name)
                results.append({"error": f"Unknown tool: {tool_name}"})
                continue

            url = f"{MCP_GATEWAY_URL}{tool_meta['wrapper_path']}"
            method = "POST"

            async with session.request(method, url, json=input_data) as resp:
                # Force parsing as JSON, no fallback to text
                result = await resp.json(content_type=None)  # ignore content-type issues
                print(f"Executed {tool_name} ({method} {url}):", result)
                results.append(result)
    
    return results

# --- FastAPI endpoint ---
@app.post("/run_brain")
async def run_brain_endpoint(req: BrainRequest):
    plan_tools = await run_brain(req.user_request)
    if not plan_tools:
        return {"error": "Failed to generate plan"}

    plan, tools = plan_tools
    results = []

    # Execute plan and capture results
    mcp_results = await execute_plan(plan, tools)
    
    for i, step in enumerate(plan):
        results.append({
            "tool": step["tool"], 
            "input": step["input"],
            "output": mcp_results[i] if i < len(mcp_results) else {"error": "Result not found"}
        })
    
    print("Brain server step output:", mcp_results[i])

    return {"plan": plan, "execution_results": results}

# Run with:
# uvicorn brain_server:app --host 0.0.0.0 --port 9000