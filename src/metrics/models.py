"""
Core data models for the metrics system
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DataSource(str, Enum):
    JIRA = "jira"
    SERVICENOW = "servicenow"

class MetricsRequest(BaseModel):
    user_query: str = Field(..., description="Natural language query")
    data_sources: List[DataSource] = Field(default=[DataSource.JIRA, DataSource.SERVICENOW])

class GeneratedQuery(BaseModel):
    sql: str = Field(..., description="Generated SQL query")
    explanation: str = Field(..., description="Natural language explanation")
    tables_used: List[str] = Field(..., description="Tables referenced")
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class QueryResult(BaseModel):
    query: GeneratedQuery
    data: List[Dict[str, Any]]
    total_rows: int
    execution_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
