import httpx
import re
from langsmith import traceable
from typing import Any

# ----------------------------
# PII patterns
# ----------------------------
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}', re.I)
TOKEN_REGEX = re.compile(r'[a-zA-Z0-9]{16,}')  # long tokens/keys
PHONE_REGEX = re.compile(r'\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{3,4}')  # flexible phone pattern


def scrub_pii(data: Any) -> Any:
    """Recursively scrub PII from dicts, lists, strings."""
    if isinstance(data, dict):
        return {k: scrub_pii(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [scrub_pii(v) for v in data]
    elif isinstance(data, str):
        s = EMAIL_REGEX.sub('[REDACTED_EMAIL]', data)
        s = TOKEN_REGEX.sub('[REDACTED_SENSITIVE]', s)
        s = PHONE_REGEX.sub('[REDACTED_PHONE]', s)
        return s
    else:
        return data


def mask_sensitive_data(inputs: Any) -> Any:
    """Mask headers/credentials in function inputs."""
    if isinstance(inputs, dict):
        scrubbed = inputs.copy()
        if "headers" in scrubbed and isinstance(scrubbed["headers"], dict):
            h = scrubbed["headers"].copy()
            for key in list(h.keys()):
                if key.lower() in ["authorization", "x-api-key", "cookie", "api-key"]:
                    h[key] = "[MASKED]"
            scrubbed["headers"] = h
        return scrubbed
    return inputs


def extract_business_fields(data: dict) -> dict:
    """
    Extract only business-relevant fields from Jira issue response.
    Avoid dumping huge nested objects (avatars, self-links, timestamps).
    """
    if not isinstance(data, dict):
        return data

    result = {}
    # Only extract these specific top-level fields
    for key in ["key", "id"]:
        if key in data:
            result[key] = data[key]

    # Extract only specific business fields from the nested fields object
    fields = data.get("fields", {})
    if isinstance(fields, dict):
        business_fields = {}
        
        # Basic issue info
        for f in ["summary", "description"]:
            if f in fields:
                business_fields[f] = fields[f]
        
        # Status - extract only the name
        if "status" in fields and isinstance(fields["status"], dict):
            status_obj = fields["status"]
            if "name" in status_obj:
                business_fields["status"] = status_obj["name"]
        
        # Priority - extract only the name
        if "priority" in fields and isinstance(fields["priority"], dict):
            priority_obj = fields["priority"]
            if "name" in priority_obj:
                business_fields["priority"] = priority_obj["name"]
        
        # Assignee - extract only display name
        if "assignee" in fields and isinstance(fields["assignee"], dict):
            assignee_obj = fields["assignee"]
            if "displayName" in assignee_obj:
                business_fields["assignee"] = assignee_obj["displayName"]
        
        # Reporter - extract only display name
        if "reporter" in fields and isinstance(fields["reporter"], dict):
            reporter_obj = fields["reporter"]
            if "displayName" in reporter_obj:
                business_fields["reporter"] = reporter_obj["displayName"]
        
        # Created date (useful for context)
        if "created" in fields:
            business_fields["created"] = fields["created"]
        
        result["fields"] = business_fields
    
    return result


def redact_output(output: Any) -> Any:
    """Scrub PII only, keep the structure as returned by the client."""
    return scrub_pii(output)


def secure_trace(
    name: str,
    metadata: dict | None = None,
    process_inputs=None,
    process_outputs=None
):
    """Decorator to apply centralized security to any traceable function."""
    return traceable(
        name=name,
        run_type="tool",
        metadata=metadata or {},
        process_inputs=mask_sensitive_data,
        process_outputs=redact_output,
    )


def secure_mcp_tool(name: str, service: str = "mcp-gateway"):
    """Decorator for top-level MCP tools, sending only business output."""
    return traceable(
        name=name,
        run_type="tool",
        metadata={"service": service},
        process_outputs=redact_output,
    )