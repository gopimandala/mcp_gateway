"""
Query Processor - End-to-end orchestration from user query to final results
"""

import psycopg2
from intent_checker import IntentChecker
from sql_validator import SQLValidator  
from relevance_checker import RelevanceChecker
from llm_interface import LLMProvider, build_schema_context

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "metrics_db",
    "user": "metrics_user",
    "password": "metrics_password"
}

class QueryProcessor:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.intent_checker = IntentChecker()
        self.sql_validator = SQLValidator()
        self.relevance_checker = RelevanceChecker()
    
    async def execute_sql(self, sql: str) -> dict:
        """Execute SQL and return results"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute(sql)
            
            # Check if it's a SELECT query
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                # Format results for display
                result = {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows),
                    "formatted_display": self._format_results(columns, rows)
                }
            else:
                # For INSERT, UPDATE, DELETE
                result = {
                    "rows_affected": cursor.rowcount,
                    "message": f"Query executed successfully. {cursor.rowcount} rows affected."
                }
            
            cursor.close()
            conn.close()
            return result
            
        except Exception as e:
            return {
                "error": f"SQL execution failed: {str(e)}",
                "sql": sql
            }
    
    def _format_results(self, columns: list, rows: list) -> str:
        """Format query results for display"""
        if not rows:
            return "No results returned."
        
        # Calculate column widths
        col_widths = [len(col) for col in columns]
        for row in rows:
            for i, value in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(value)))
        
        # Build formatted table
        lines = []
        
        # Header row
        header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
        lines.append(header)
        lines.append("-" * len(header))
        
        # Data rows (limit to first 10 for display)
        for row in rows[:10]:
            row_line = " | ".join(str(value).ljust(col_widths[i]) for i, value in enumerate(row))
            lines.append(row_line)
        
        if len(rows) > 10:
            lines.append(f"... and {len(rows) - 10} more rows")
        
        return "\n".join(lines)
    
    async def process_query(self, user_query: str) -> dict:
        """Complete end-to-end pipeline: user query → final results"""
        
        # Step 1: Intent validation
        if not self.intent_checker.is_metrics_query(user_query):
            return {
                "error": "This doesn't appear to be a metrics query",
                "suggestion": "Try asking about counts, averages, or status of tickets"
            }
        
        # Step 2: Generate SQL with dynamic schema
        schema_context = build_schema_context(user_query)
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
        
        # Step 7: Execute SQL
        execution_result = await self.execute_sql(sql)
        if "error" in execution_result:
            return execution_result
        
        # Step 8: Return final results
        return {
            "success": True,
            "query": user_query,
            "sql": sql,
            "explanation": llm_result["explanation"],
            "confidence_score": llm_result["confidence_score"],
            "relevance_score": relevance_score,
            "domain": self.intent_checker.classify_domain(user_query),
            "results": execution_result
        }
