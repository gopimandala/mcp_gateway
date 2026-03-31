"""
LLM Provider Interface
"""

import os
import psycopg2
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from openai import AsyncOpenAI
from intent_checker import IntentChecker

# Load environment variables
load_dotenv()

# Database connection for schema fetching
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "metrics_db",
    "user": "metrics_user",
    "password": "metrics_password"
}

def get_table_schema(table_name):
    """Get schema for a specific table"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        schema = f"{table_name}:\n"
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            schema += f"  - {col[0]}: {col[1]} {nullable}{default}\n"
        
        cursor.close()
        conn.close()
        return schema
        
    except Exception as e:
        return f"Error fetching schema for {table_name}: {e}"

def build_schema_context(user_query):
    """Build schema context based on intent checker classification"""
    intent_checker = IntentChecker()
    domain = intent_checker.classify_domain(user_query)
    
    schema_context = ""
    
    if domain in ["jira", "both"]:
        schema_context += "\n🔷 Jira Tables:\n"
        schema_context += get_table_schema('jira_issues')
        schema_context += get_table_schema('jira_projects')
        schema_context += get_table_schema('jira_users')
    
    if domain in ["servicenow", "both"]:
        schema_context += "\n❄️ ServiceNow Tables:\n"
        schema_context += get_table_schema('sn_incidents')
        schema_context += get_table_schema('sn_groups')
        schema_context += get_table_schema('sn_users')
    
    return schema_context

class LLMProvider(ABC):
    @abstractmethod
    async def generate_sql(self, prompt: str, schema_context: str) -> dict:
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def generate_sql(self, prompt: str, schema_context: str = None) -> dict:
        try:
            # Build schema context dynamically if not provided
            if schema_context is None:
                schema_context = build_schema_context(prompt)
            
            # Load system prompt from file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_file = os.path.join(current_dir, "system_prompt.md")
            
            with open(prompt_file, 'r') as f:
                system_prompt_template = f.read()
            
            system_prompt = system_prompt_template.format(
                schema_context=schema_context,
                prompt=prompt
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the response - remove any markdown formatting
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            sql_query = sql_query.strip()
            
            return {
                "sql": sql_query,
                "explanation": f"Generated SQL query for: {prompt}",
                "confidence_score": 0.85
            }
            
        except Exception as e:
            return {
                "sql": "SELECT 1;",
                "explanation": f"Error generating SQL: {str(e)}",
                "confidence_score": 0.0
            }
    
    async def test_connection(self) -> bool:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception:
            return False
