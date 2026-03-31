#!/usr/bin/env python3
"""
CLI interface for the metrics query processor
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
from llm_interface import OpenAIProvider
from processor import QueryProcessor

load_dotenv()

async def run_cli():
    """Run interactive CLI for query processing"""
    try:
        # Initialize the processor
        provider = OpenAIProvider()
        processor = QueryProcessor(provider)
        
        print("🚀 Metrics Query Processor")
        print("=" * 50)
        print("Type your queries about Jira and ServiceNow metrics")
        print("Type 'quit' or 'exit' to stop")
        print("=" * 50)
        
        while True:
            try:
                # Get user input
                query = input("\n🔍 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                print(f"\n⏳ Processing: {query}")
                print("-" * 40)
                
                # Process the query
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
                print(f"🔒 Confidence: {result['confidence_score']:.2f}")
                print(f"🎪 Relevance: {result['relevance_score']:.2f}")
                
                # Display results
                if 'results' in result:
                    results = result['results']
                    print(f"\n📊 Results ({results['row_count']} rows):")
                    print(results['formatted_display'])
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        sys.exit(1)

def run_single_query(query: str):
    """Run a single query and exit"""
    async def _run():
        try:
            provider = OpenAIProvider()
            processor = QueryProcessor(provider)
            
            print(f"🔍 Processing: {query}")
            print("-" * 40)
            
            result = await processor.process_query(query)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                if "suggestion" in result:
                    print(f"💡 Suggestion: {result['suggestion']}")
                return
            
            print(f"✅ Success!")
            print(f"🎯 Domain: {result['domain']}")
            print(f"📝 SQL: {result['sql']}")
            print(f"💭 Explanation: {result['explanation']}")
            print(f"🔒 Confidence: {result['confidence_score']:.2f}")
            print(f"🎪 Relevance: {result['relevance_score']:.2f}")
            
            # Display results
            if 'results' in result:
                results = result['results']
                print(f"\n📊 Results ({results['row_count']} rows):")
                print(results['formatted_display'])
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    asyncio.run(_run())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        run_single_query(query)
    else:
        # Interactive mode
        asyncio.run(run_cli())
