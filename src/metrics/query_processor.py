"""
Main query processing with all validation layers
"""

from intent_checker import IntentChecker
from sql_validator import SQLValidator  
from relevance_checker import RelevanceChecker
from llm_interface import LLMProvider
from models import GeneratedQuery

class QueryProcessor:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.intent_checker = IntentChecker()
        self.sql_validator = SQLValidator()
        self.relevance_checker = RelevanceChecker()
    
    async def process_query(self, user_query: str) -> dict:
        # Step 1: Intent validation
        if not self.intent_checker.is_metrics_query(user_query):
            return {
                "error": "This doesn't appear to be a metrics query",
                "suggestion": "Try asking about counts, averages, or status of tickets"
            }
        
        # Step 2: Generate SQL
        schema_context = "Jira and ServiceNow tables available"
        llm_result = await self.llm.generate_sql(user_query, schema_context)
        sql = llm_result["sql"]
        
        # Step 3: SQL safety check
        is_safe, safety_msg = self.sql_validator.is_safe(sql)
        if not is_safe:
            return {"error": f"SQL safety check failed: {safety_msg}"}
        
        # Step 4: SQL syntax check
        is_valid, syntax_msg = self.sql_validator.is_valid_syntax(sql)
        if not is_valid:
            return {"error": f"SQL syntax error: {syntax_msg}"}
        
        # Step 5: Empty result guardrail
        is_empty, empty_msg = self.relevance_checker.check_empty_result(sql)
        if is_empty:
            return {"error": f"SQL may return empty results: {empty_msg}"}
        
        # Step 6: Relevance check
        relevance_score, relevance_msg = self.relevance_checker.check_relevance_score(user_query, sql)
        if relevance_score < 0.3:
            return {"error": f"SQL doesn't match your question: {relevance_msg}"}
        
        return {
            "success": True,
            "sql": sql,
            "explanation": llm_result["explanation"],
            "confidence_score": llm_result["confidence_score"],
            "relevance_score": relevance_score,
            "domain": self.intent_checker.classify_domain(user_query)
        }
