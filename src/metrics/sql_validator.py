"""
SQL validation using established libraries
"""

import sqlparse
from sqlvalidator import sql_validator as sql_validator_lib

class SQLValidator:
    def __init__(self):
        self.dangerous_keywords = [
            "DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", 
            "ALTER", "CREATE", "EXEC", "GRANT", "REVOKE"
        ]
    
    def is_safe(self, sql: str) -> tuple[bool, str]:
        """Check if SQL is safe using sqlparse"""
        try:
            parsed = sqlparse.parse(sql)[0]
            
            # Check dangerous keywords
            sql_upper = sql.upper()
            for keyword in self.dangerous_keywords:
                if keyword in sql_upper:
                    return False, f"Contains dangerous keyword: {keyword}"
            
            # Ensure it's a SELECT query
            if parsed.get_type() != 'SELECT':
                return False, "Only SELECT queries are allowed"
            
            return True, "SQL is safe"
        except Exception as e:
            return False, f"Parse error: {e}"
    
    def is_valid_syntax(self, sql: str) -> tuple[bool, str]:
        """Check syntax using sqlvalidator"""
        try:
            parsed = sql_validator_lib.parse(sql)
            if parsed.is_valid():
                return True, "Valid SQL syntax"
            else:
                return False, f"Invalid SQL: {parsed.get_errors()}"
        except Exception as e:
            return False, f"Syntax error: {e}"
