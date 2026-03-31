#!/usr/bin/env python3
"""
Simple test for OpenAI LLM integration with intent-based schema building
"""

import asyncio
import os
from dotenv import load_dotenv
from llm_interface import OpenAIProvider, build_schema_context
from intent_checker import IntentChecker

load_dotenv()

async def test_openai():
    try:
        provider = OpenAIProvider()
        intent_checker = IntentChecker()
        
        # Test different query types
        test_queries = [
            "Count all Jira issues",
            "Show high priority ServiceNow incidents", 
            "List all projects",
            "Show users from both systems"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            
            # Show intent classification
            domain = intent_checker.classify_domain(query)
            print(f"🎯 Intent: {domain}")
            
            print("📋 Schema Context:")
            schema_context = build_schema_context(query)
            print(schema_context[:300] + "..." if len(schema_context) > 300 else schema_context)
            
            result = await provider.generate_sql(query)  # No schema_context provided - will build dynamically
            print(f"Generated SQL: {result['sql']}")
            print(f"Explanation: {result['explanation']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_openai())
