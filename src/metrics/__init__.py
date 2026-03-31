"""
Metrics Module - Business intelligence for Jira and ServiceNow
"""

__version__ = "0.1.0"

# Main exports
from .models import MetricsRequest, GeneratedQuery, QueryResult
from .llm_interface import LLMProvider
from .query_processor import QueryProcessor

__all__ = ["MetricsRequest", "GeneratedQuery", "QueryResult", "LLMProvider", "QueryProcessor"]
