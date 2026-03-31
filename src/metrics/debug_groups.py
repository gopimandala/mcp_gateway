#!/usr/bin/env python3
"""
Debug why group names are not showing
"""

import asyncio
import os
from dotenv import load_dotenv
from llm_interface import OpenAIProvider, build_schema_context

load_dotenv()

async def debug_group_names():
    try:
        provider = OpenAIProvider()
        
        query = "get count of incidents by each assignment groups in service now"
        
        print(f"🔍 Query: {query}")
        
        # Show schema context
        schema_context = build_schema_context(query)
        print(f"\n📋 Schema Context:")
        print(schema_context[:500] + "..." if len(schema_context) > 500 else schema_context)
        
        # Generate SQL
        llm_result = await provider.generate_sql(query, schema_context)
        sql = llm_result["sql"]
        
        print(f"\n📝 Generated SQL: {sql}")
        
        # What the SQL should be
        expected_sql = """
        SELECT g.name, COUNT(*) AS incident_count
        FROM sn_incidents i
        JOIN sn_groups g ON i.assignment_group = g.sys_id
        GROUP BY g.name
        ORDER BY incident_count DESC;
        """
        
        print(f"\n💡 Expected SQL (with group names):")
        print(expected_sql.strip())
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_group_names())
