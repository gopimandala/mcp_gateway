"""
Relevance validation - Did LLM hallucinate or go off-topic?
"""

class RelevanceChecker:
    def __init__(self):
        self.empty_result_patterns = [
            "SELECT 1", "SELECT NULL", "SELECT ''", 
            "WHERE 1=0", "WHERE FALSE", "LIMIT 0"
        ]
    
    def check_empty_result(self, sql: str) -> tuple[bool, str]:
        """Check if SQL will return empty results"""
        sql_upper = sql.upper().strip()
        
        for pattern in self.empty_result_patterns:
            if pattern in sql_upper:
                return True, f"SQL may return empty results: {pattern}"
        
        # Check for impossible conditions
        if "WHERE 1=0" in sql_upper or "WHERE FALSE" in sql_upper:
            return True, "SQL has impossible condition"
        
        return False, "SQL should return data"
    
    def check_relevance_score(self, user_query: str, sql: str) -> tuple[float, str]:
        """Simple relevance scoring (can be enhanced with LLM later)"""
        query_words = set(user_query.lower().split())
        sql_words = set(sql.lower().split())
        
        # Simple word overlap score
        common_words = query_words.intersection(sql_words)
        score = len(common_words) / max(len(query_words), 1)
        
        # Check if SQL mentions relevant tables
        relevant_tables = ["jira_issues", "sn_incidents", "jira_users", "sn_users"]
        table_mentions = sum(1 for table in relevant_tables if table in sql.lower())
        
        # Bonus points for table mentions
        if table_mentions > 0:
            score += 0.3
        
        # Bonus points for SQL keywords
        sql_keywords = ["count", "select", "from", "where"]
        keyword_matches = sum(1 for kw in sql_keywords if kw in sql.lower())
        score += keyword_matches * 0.1
        
        return min(score, 1.0), f"Relevance score: {score:.2f}"
