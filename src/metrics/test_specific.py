#!/usr/bin/env python3
"""
Test with specific query about Jira issues and ServiceNow assignment
"""

import asyncio
import os
from dotenv import load_dotenv
from llm_interface import OpenAIProvider, build_schema_context
from intent_checker import IntentChecker

load_dotenv()

async def test_specific_query():
    try:
        provider = OpenAIProvider()
        intent_checker = IntentChecker()
        
        # Test the specific query
        query = "how many open jira issues are there which have assignment group as 'IT' in service now"
        
        print(f"🔍 Query: {query}")
        
        # Show intent classification
        domain = intent_checker.classify_domain(query)
        print(f"🎯 Intent: {domain}")
        
        print("📋 Schema Context:")
        schema_context = build_schema_context(query)
        print(schema_context[:500] + "..." if len(schema_context) > 500 else schema_context)
        
        result = await provider.generate_sql(query)
        print(f"\nGenerated SQL: {result['sql']}")
        print(f"Explanation: {result['explanation']}")
        print(f"Confidence: {result['confidence_score']}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_specific_query())
