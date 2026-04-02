# brain_server.py
import asyncio
import json
import aiohttp
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# --- load environment ---
load_dotenv()

# --- brain configuration ---
from config import brain_settings

OPENAI_KEY = brain_settings.openai_key
client = OpenAI(api_key=OPENAI_KEY)

# --- guardrail config ---
GUARDRAIL_URL = f"http://localhost:{brain_settings.guardrail_port}/check"

# --- MCP/Kong config ---
MCP_GATEWAY_URL = brain_settings.mcp_gateway_url
TOOLS_URL = f"{MCP_GATEWAY_URL}/api/jira/tools"

# --- FastAPI app ---
app = FastAPI(title="Brain Server")

# --- request model ---
class BrainRequest(BaseModel):
    user_request: str

# --- guardrail check ---
async def check_guardrail(text: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            GUARDRAIL_URL,
            json={"text": text}
        ) as resp:
            if resp.status != 200:
                raise Exception("Guardrail service error")

            return await resp.json()

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
        return plan, tools, None
    except Exception:
        print("Failed to parse LLM output:", plan_str)
        # treat as normal assistant message
        return None, tools, plan_str

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

    # --- guardrail check ---
    guardrail_result = await check_guardrail(req.user_request)

    if not guardrail_result["safe"]:
        response_data = {
            "plan": [],
            "execution_results": [
                {
                    "tool": "guardrail",
                    "output": "Request blocked due to unsafe content",
                    "scores": guardrail_result["scores"]
                }
            ]
        }
        return Response(
            content=json.dumps(response_data, indent=2),
            media_type="application/json"
        )

    plan, tools, message = await run_brain(req.user_request)
    # If LLM returned a normal message (guardrail/refusal)
    if message:
        response_data = {
            "plan": [],
            "execution_results": [
                {
                    "tool": "assistant",
                    "output": message
                }
            ]
        }
        return Response(
            content=json.dumps(response_data, indent=2),
            media_type="application/json"
        )
    if not plan:
        response_data = {"plan": [], "execution_results": [], "message": "No actions generated"}
        return Response(
            content=json.dumps(response_data, indent=2),
            media_type="application/json"
        )

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

    response_data = {"plan": plan, "execution_results": results}
    return Response(
        content=json.dumps(response_data, indent=2),
        media_type="application/json"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("brain_server:app", host="0.0.0.0", port=brain_settings.brain_port, reload=True)