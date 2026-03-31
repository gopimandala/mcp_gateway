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
        
        # Handle schema-qualified table names
        if '.' in table_name:
            schema, table = table_name.split('.', 1)
        else:
            schema = 'public'
            table = table_name
        
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s 
            ORDER BY ordinal_position
        """, (schema, table))
        
        columns = cursor.fetchall()
        
        # If no columns found, table doesn't exist or is empty
        if not columns:
            cursor.close()
            conn.close()
            return ""
        
        schema_output = f"{table_name}:\n"
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            schema_output += f"  - {col[0]}: {col[1]} {nullable}{default}\n"
        
        cursor.close()
        conn.close()
        return schema_output
        
    except Exception as e:
        return f"Error fetching schema for {table_name}: {e}"

def get_tables_by_domain():
    """Get tables organized by domain from database schemas"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all schemas and their tables
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema IN ('jira', 'servicenow') 
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name
        """)
        schema_tables = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Organize by schema (domain)
        domains = {}
        for schema, table_name in schema_tables:
            if schema not in domains:
                domains[schema] = []
            domains[schema].append(f"{schema}.{table_name}")
        
        return domains
        
    except Exception as e:
        print(f"❌ Error: Schema tables not found. Please run setup_database.py first.")
        print(f"   Details: {e}")
        return {}

def build_schema_context(user_query):
    """Build schema context based on intent checker classification"""
    intent_checker = IntentChecker()
    domain = intent_checker.classify_domain(user_query)
    
    # Get tables organized by domain
    table_domains = get_tables_by_domain()
    
    schema_context = ""
    
    if domain in ["jira", "both"] and "jira" in table_domains:
        schema_context += "\n🔷 Jira Tables:\n"
        for table in table_domains["jira"]:
            schema_context += get_table_schema(table)
    
    if domain in ["servicenow", "both"] and "servicenow" in table_domains:
        schema_context += "\n❄️ ServiceNow Tables:\n"
        for table in table_domains["servicenow"]:
            schema_context += get_table_schema(table)
    
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

            print("\nSystem prompt:", system_prompt)
            print("\nUser prompt:", prompt)

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
