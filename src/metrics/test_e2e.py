#!/usr/bin/env python3
"""
Test the complete QueryProcessor with end-to-end orchestration
"""

import asyncio
import os
from dotenv import load_dotenv
from llm_interface import OpenAIProvider
from processor import QueryProcessor

load_dotenv()

async def test_processor():
    try:
        # Initialize the complete processor
        provider = OpenAIProvider()
        processor = QueryProcessor(provider)
        
        # Test queries
        test_queries = [
            "Count all open Jira issues",
            "Show me high priority ServiceNow incidents",
            "List Jira projects with their issue counts",
            "How many incidents were resolved this month?"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"🔍 Query: {query}")
            print('='*60)
            
            # Process the complete end-to-end pipeline
            result = await processor.process_query(query)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                if "suggestion" in result:
                    print(f"💡 Suggestion: {result['suggestion']}")
                continue
            
            print(f"✅ Success!")
            print(f"🎯 Domain: {result['domain']}")
            print(f"📝 SQL: {result['sql']}")
            print(f"💭 Explanation: {result['explanation']}")
            print(f"🔒 Confidence: {result['confidence_score']}")
            print(f"🎪 Relevance: {result['relevance_score']}")
            
            # Display results
            if 'results' in result:
                results = result['results']
                print(f"\n📊 Results ({results['row_count']} rows):")
                print(results['formatted_display'])
            
            print()
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_processor())
