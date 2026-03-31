#!/usr/bin/env python3
"""
Debug the relevance checker issue
"""

import asyncio
import os
from dotenv import load_dotenv
from llm_interface import OpenAIProvider, build_schema_context
from relevance_checker import RelevanceChecker

load_dotenv()

async def debug_relevance():
    try:
        provider = OpenAIProvider()
        checker = RelevanceChecker()
        
        query = "list all assignment groups in service now"
        
        print(f"🔍 Query: {query}")
        
        # Generate SQL
        schema_context = build_schema_context(query)
        llm_result = await provider.generate_sql(query, schema_context)
        sql = llm_result["sql"]
        
        print(f"📝 Generated SQL: {sql}")
        
        # Check relevance
        score, msg = checker.check_relevance_score(query, sql)
        print(f"🎪 Relevance Score: {score}")
        print(f"📝 Message: {msg}")
        
        # Debug word overlap
        query_words = set(query.lower().split())
        sql_words = set(sql.lower().split())
        common_words = query_words.intersection(sql_words)
        
        print(f"\n🔍 Query words: {query_words}")
        print(f"🔍 SQL words: {sql_words}")
        print(f"🔍 Common words: {common_words}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_relevance())
