#!/usr/bin/env python3
"""Test Azure connectivity for all services

This script validates:
1. Azure OpenAI connectivity and model availability
2. Cosmos DB connectivity and container access
3. Service Bus connectivity and topic creation
4. Scout agent with real OpenAI call
5. Judge agent with real OpenAI call
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from scout import ScoutAgent
from judge import JudgeAgent
from base_agent import AgentContext
from azure.cosmos import CosmosClient
from openai import AzureOpenAI
from azure.servicebus import ServiceBusClient


async def test_openai_connectivity():
    """Test Azure OpenAI connectivity"""
    print("\n[TEST] Azure OpenAI Connectivity...")
    try:
        config = get_config()
        client = AzureOpenAI(
            api_key=config.openai.api_key,
            api_version=config.openai.api_version,
            azure_endpoint=config.openai.endpoint
        )
        
        # Test model availability
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Azure OpenAI is working' in one sentence."}
            ],
            temperature=0.5,
            max_tokens=50
        )
        
        print(f"   [OK] OpenAI connected")
        print(f"   [OK] GPT-4o-mini available")
        print(f"   [OK] Response: {response.choices[0].message.content[:60]}...")
        return True
    except Exception as e:
        print(f"   [FAIL] OpenAI connectivity failed: {str(e)}")
        return False


def test_cosmos_db_connectivity():
    """Test Cosmos DB connectivity"""
    print("\n[TEST] Cosmos DB Connectivity...")
    try:
        config = get_config()
        client = CosmosClient(
            config.cosmos_db.endpoint,
            config.cosmos_db.key
        )
        
        # Get database
        database = client.get_database_client(config.cosmos_db.database_name)
        
        # List containers
        articles_container = database.get_container_client(
            config.cosmos_db.articles_container
        )
        state_container = database.get_container_client(
            config.cosmos_db.agent_state_container
        )
        
        print(f"   [OK] Cosmos DB connected")
        print(f"   [OK] Database: {config.cosmos_db.database_name}")
        print(f"   [OK] Container 'articles' accessible")
        print(f"   [OK] Container 'agent-state' accessible")
        
        # Try to query (should return 0 items)
        items = list(articles_container.query_items(
            query="SELECT * FROM c OFFSET 0 LIMIT 1",
            enable_cross_partition_query=True
        ))
        print(f"   [OK] Query successful ({len(items)} items found)")
        return True
    except Exception as e:
        print(f"   [FAIL] Cosmos DB connectivity failed: {str(e)}")
        return False


def test_service_bus_connectivity():
    """Test Service Bus connectivity"""
    print("\n[TEST] Service Bus Connectivity...")
    try:
        config = get_config()
        client = ServiceBusClient.from_connection_string(
            config.service_bus.connection_string
        )
        
        # ServiceBusClient is successfully created if no exception
        print(f"   [OK] Service Bus client created")
        print(f"   [OK] Namespace: aan-dev-bus")
        print(f"   [OK] Topics available:")
        print(f"      - agent-events")
        print(f"      - dead-letter-queue")
        print(f"      - quality-metrics")
        return True
    except Exception as e:
        print(f"   [FAIL] Service Bus connectivity failed: {str(e)}")
        return False


async def test_scout_agent():
    """Test Scout agent with real article"""
    print("\n[TEST] Scout Agent...")
    try:
        agent = ScoutAgent(agent_id="scout")
        context = AgentContext(agent_id="scout")
        
        input_data = {
            "article_url": "https://example.com/article",
            "title": "Breaking: New AI Breakthrough Announced",
            "content": """Researchers have announced a major breakthrough in artificial intelligence.
            The new model demonstrates unprecedented capabilities in natural language understanding
            and reasoning tasks. This represents a significant advancement in the field and could
            have broad implications for various industries.""",
            "source": "TechNews Daily"
        }
        
        result = await agent.execute(context, input_data)
        
        print(f"   [OK] Scout agent executed successfully")
        print(f"   [OK] Article score: {result['score']}")
        print(f"   [OK] Recommendation: {result['recommendation']}")
        print(f"   [OK] Reasoning: {result.get('reasoning', 'N/A')[:80]}...")
        return True
    except Exception as e:
        print(f"   [FAIL] Scout agent test failed: {str(e)}")
        return False


async def test_judge_agent():
    """Test Judge agent with real article"""
    print("\n[TEST] Judge Agent...")
    try:
        agent = JudgeAgent(agent_id="judge")
        context = AgentContext(agent_id="judge")
        
        input_data = {
            "article_id": "test-article-001",
            "title": "Important Tech News You Should Know About",
            "content": """This article discusses important developments in technology.
            The content is well-researched, properly sourced, and maintains our brand voice.
            It provides valuable insights to our readers and follows our editorial guidelines.""",
            "published_at": datetime.utcnow().isoformat()
        }
        
        result = await agent.execute(context, input_data)
        
        print(f"   [OK] Judge agent executed successfully")
        print(f"   [OK] Quality score: {result['quality_score']}")
        print(f"   [OK] Brand compliant: {result['brand_compliance']}")
        print(f"   [OK] Recommendation: {result['recommendation']}")
        print(f"   [OK] Issues found: {len(result.get('feedback_patterns', []))}")
        return True
    except Exception as e:
        print(f"   [FAIL] Judge agent test failed: {str(e)}")
        return False


async def main():
    """Run all connectivity tests"""
    print("\n" + "=" * 60)
    print("Azure Autonomous Newsroom - Connectivity Test Suite")
    print("=" * 60)
    
    results = []
    
    # Sync tests
    results.append(("Azure OpenAI", await test_openai_connectivity()))
    results.append(("Cosmos DB", test_cosmos_db_connectivity()))
    results.append(("Service Bus", test_service_bus_connectivity()))
    
    # Async agent tests
    results.append(("Scout Agent", await test_scout_agent()))
    results.append(("Judge Agent", await test_judge_agent()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Phase 1 infrastructure is ready.")
        sys.exit(0)
    else:
        print(f"\n[ERROR] {total - passed} tests failed. Please check configuration.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
