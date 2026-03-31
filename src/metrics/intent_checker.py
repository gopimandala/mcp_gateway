"""
Intent validation - Is this a metrics query?
"""

class IntentChecker:
    def __init__(self):
        self.metrics_keywords = [
            "count", "how many", "total", "average", "show me",
            "list", "get", "what is", "status", "priority"
        ]
    
    def is_metrics_query(self, query: str) -> bool:
        """Check if query is about metrics"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.metrics_keywords)
    
    def classify_domain(self, query: str) -> str:
        """Jira, ServiceNow, or Both"""
        jira_keywords = ["jira", "issue", "ticket", "bug", "story"]
        snow_keywords = ["servicenow", "snow", "service now", "incident", "sn_", "case"]
        
        query_lower = query.lower()
        has_jira = any(kw in query_lower for kw in jira_keywords)
        has_snow = any(kw in query_lower for kw in snow_keywords)
        
        if has_jira and has_snow:
            return "both"
        elif has_jira:
            return "jira"
        elif has_snow:
            return "servicenow"
        else:
            return "both"  # Default to both
