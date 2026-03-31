#!/usr/bin/env python3
"""
Debug the exact prompt sent to LLM
"""

import asyncio
import os
from dotenv import load_dotenv
from llm_interface import OpenAIProvider, build_schema_context

load_dotenv()

async def debug_llm_prompt():
    try:
        provider = OpenAIProvider()
        
        query = "how many jira tickets have service now reference values"
        
        print(f"🔍 User Query: {query}")
        print("=" * 60)
        
        # Build schema context
        schema_context = build_schema_context(query)
        
        print("📋 Schema Context Sent to LLM:")
        print("-" * 40)
        print(schema_context)
        print("-" * 40)
        
        # Load system prompt
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_file = os.path.join(current_dir, "system_prompt.md")
        
        with open(prompt_file, 'r') as f:
            system_prompt_template = f.read()
        
        system_prompt = system_prompt_template.format(
            schema_context=schema_context,
            prompt=query
        )
        
        print("\n🤖 Complete System Prompt Sent to LLM:")
        print("=" * 60)
        print(system_prompt)
        print("=" * 60)
        
        # Generate SQL
        llm_result = await provider.generate_sql(query, schema_context)
        
        print(f"\n📝 Generated SQL: {llm_result['sql']}")
        print(f"💭 Explanation: {llm_result['explanation']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_llm_prompt())
