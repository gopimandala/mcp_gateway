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
        """Enhanced relevance scoring with semantic matching"""
        query_lower = user_query.lower()
        sql_lower = sql.lower()
        
        # Initialize score
        score = 0.0
        
        # 1. Semantic table matching
        table_mappings = {
            "assignment group": "sn_groups",
            "groups": "sn_groups", 
            "group": "sn_groups",
            "incident": "sn_incidents",
            "incidents": "sn_incidents",
            "issue": "jira_issues",
            "issues": "jira_issues",
            "ticket": "jira_issues",
            "tickets": "jira_issues",
            "project": "jira_projects",
            "projects": "jira_projects",
            "user": "jira_users",
            "users": "jira_users"
        }
        
        # Check for semantic table matches
        for query_term, table_name in table_mappings.items():
            if query_term in query_lower and table_name in sql_lower:
                score += 0.5
                break
        
        # 2. Direct word overlap (reduced weight)
        query_words = set(query_lower.split())
        sql_words = set(sql_lower.split())
        common_words = query_words.intersection(sql_words)
        score += len(common_words) * 0.1
        
        # 3. Bonus for relevant table mentions
        relevant_tables = ["jira_issues", "sn_incidents", "jira_users", "sn_users", "jira_projects", "sn_groups"]
        table_mentions = sum(1 for table in relevant_tables if table in sql_lower)
        score += table_mentions * 0.2
        
        # 4. Bonus for proper SQL structure
        if "select" in sql_lower and "from" in sql_lower:
            score += 0.1
        
        # 5. Bonus for domain-specific keywords
        if any(word in query_lower for word in ["list", "show", "get", "count"]):
            if "select" in sql_lower:
                score += 0.1
        
        return min(score, 1.0), f"Relevance score: {score:.2f}"
