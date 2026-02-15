"""
Full Pipeline Test - Multi-Agent Orchestration with Embeddings

Tests the complete article processing pipeline:
1. Scout → Prof → Scribe → Judge → Pixel → Ops
2. Vector embeddings generation
3. Semantic search
4. End-to-end metrics collection
"""

import asyncio
import json
import logging
from datetime import datetime

from orchestrator import ArticleOrchestrator
from workflow import ArticleWorkflow
from embeddings import EmbeddingsManager
from config import get_config

logger = logging.getLogger("pipeline_test")
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def test_full_pipeline():
    """Test the complete multi-agent pipeline"""
    
    print("\n" + "=" * 80)
    print("FULL PIPELINE TEST - Multi-Agent Article Processing")
    print("=" * 80)
    
    # Initialize components
    orchestrator = ArticleOrchestrator()
    embeddings_manager = EmbeddingsManager()
    
    # Test article
    test_article = {
        "article_url": "https://example.com/pipeline-test",
        "title": "Revolutionary Quantum Computing Breakthrough Announced",
        "content": """
        Scientists have achieved a major breakthrough in quantum computing today.
        A new quantum processor has demonstrated quantum advantage over classical
        computers for the first time in a practical application.
        
        Dr. John Chen, Lead Quantum Physicist at Quantum Labs, stated:
        "This milestone represents years of research and collaboration. The implications
        for cryptography, drug discovery, and materials science are enormous."
        
        The breakthrough involves a 1000-qubit processor that maintains quantum coherence
        for over 1 millisecond - a critical threshold for practical applications.
        Industry analysts predict this could lead to major advances in solving complex
        optimization problems that currently take classical computers years to compute.
        
        The research will be published in Nature Quantum Information next week, and the
        team plans to make their findings available to the research community.
        """,
        "source": "Science News Today"
    }
    
    # Stage 1: Run full orchestration pipeline
    print("\n[STAGE 1] Running Multi-Agent Orchestration Pipeline")
    print("-" * 80)
    
    pipeline_result = await orchestrator.process_article(test_article)
    
    print(f"\nPipeline Status: {pipeline_result['status']}")
    if pipeline_result['status'] == "PUBLISHED":
        print(f"Article ID: {pipeline_result['article_id']}")
        print(f"Published URL: {pipeline_result['result'].get('published_url')}")
        print(f"Quality Score: {pipeline_result['result'].get('quality_score')}")
        print(f"Brand Compliant: {pipeline_result['result'].get('brand_compliant')}")
        image_url = pipeline_result['result'].get('image_url')
        if image_url:
            print(f"Image URL: {image_url[:60]}...")
        else:
            print(f"Image URL: Not generated (Pixel agent may have skipped)")
        
        # Print agent execution times
        print("\nAgent Execution Times:")
        metrics = pipeline_result['metrics']
        for agent_name in ["scout", "prof", "judge", "scribe", "pixel", "ops"]:
            duration_key = f"{agent_name}_duration_ms"
            if duration_key in metrics['agent_times']:
                duration = metrics['agent_times'][duration_key]
                print(f"  {agent_name}: {duration:.0f}ms")
        
        print(f"\nTotal Pipeline Time: {metrics['total_time_ms']:.0f}ms")
    else:
        print(f"Pipeline did not publish: {pipeline_result['status']}")
        print(f"Errors: {pipeline_result['metrics'].get('errors', {})}")
    
    # Stage 2: Generate embeddings
    print("\n[STAGE 2] Generating Vector Embeddings")
    print("-" * 80)
    
    article_id = pipeline_result['article_id']
    seo_keywords = pipeline_result['result'].get('seo_keywords', [])
    
    embedded_article = await embeddings_manager.embed_article(
        article_id=article_id,
        title=test_article['title'],
        content=test_article['content'],
        seo_keywords=seo_keywords
    )
    
    print(f"Generated embedding with {len(embedded_article['embedding'])} dimensions")
    print(f"Embedding dimension: {embedded_article['embedding_dimension']}")
    print(f"Embedding model: {embedded_article['embedding_model']}")
    
    # Stage 3: Semantic search
    print("\n[STAGE 3] Testing Semantic Search")
    print("-" * 80)
    
    search_queries = [
        "quantum computing breakthrough",
        "artificial intelligence and machine learning",
        "cryptography and security"
    ]
    
    for query in search_queries:
        results = await embeddings_manager.semantic_search(query, top_k=3)
        print(f"\nQuery: '{query}'")
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']}")
                print(f"     Similarity: {result['score']:.3f}")
                print(f"     Keywords: {', '.join(result['keywords'][:3])}")
        else:
            print("  No results found (first article may not be indexed yet)")
    
    # Stage 4: Brand rules embeddings
    print("\n[STAGE 4] Creating Brand Rules Embeddings")
    print("-" * 80)
    
    brand_rules = [
        {
            "id": "accuracy",
            "description": "All claims must be fact-checked and sourced",
            "guideline": "Every statistical claim requires peer-reviewed source"
        },
        {
            "id": "tone",
            "description": "Maintain professional and objective tone",
            "guideline": "Avoid sensationalism, use passive voice for balance"
        },
        {
            "id": "length",
            "description": "Optimal article length is 800-1200 words",
            "guideline": "Balance with SEO optimization and readability"
        }
    ]
    
    await embeddings_manager.create_brand_rules_embeddings(brand_rules)
    print(f"Created embeddings for {len(brand_rules)} brand rules")
    
    # Stage 5: Batch workflow
    print("\n[STAGE 5] Running Multi-Article Workflow")
    print("-" * 80)
    
    articles_batch = [
        {
            "article_url": "https://example.com/article-2",
            "title": "Climate Scientists Report Unprecedented Arctic Warming",
            "content": "New data shows Arctic temperatures rising faster than predicted...",
            "source": "Climate News"
        },
        {
            "article_url": "https://example.com/article-3",
            "title": "New Medical Treatment Shows Promise in Clinical Trials",
            "content": "Researchers announce successful Phase 3 clinical trial results...",
            "source": "Medical Journal"
        }
    ]
    
    workflow = ArticleWorkflow()
    workflow_summary = await workflow.process_articles_batch(articles_batch)
    
    print(f"\nWorkflow Summary:")
    print(f"  Total Articles: {workflow_summary.get('articles_processed', 0)}")
    print(f"  Successful: {workflow_summary.get('successful', 0)}")
    print(f"  Failed: {workflow_summary.get('failed', 0)}")
    print(f"  Metrics:")
    metrics = workflow_summary.get('metrics', {})
    print(f"    Total Time: {metrics.get('total_time_ms', 0):.0f}ms")
    print(f"    Average per Article: {metrics.get('average_time_ms', 0):.0f}ms")
    
    # Summary
    print("\n" + "=" * 80)
    print("PIPELINE TEST COMPLETE")
    print("=" * 80)
    
    summary = {
        "test_timestamp": datetime.utcnow().isoformat(),
        "pipeline_result": {
            "status": pipeline_result['status'],
            "article_id": pipeline_result['article_id'],
            "total_time_ms": pipeline_result['metrics']['total_time_ms']
        },
        "embeddings_test": {
            "embedding_dimension": embedded_article['embedding_dimension'],
            "search_queries_tested": len(search_queries),
            "brand_rules_created": len(brand_rules)
        },
        "workflow_test": {
            "articles_processed": workflow_summary.get('articles_processed', 0),
            "successful": workflow_summary.get('successful', 0),
            "average_time_ms": metrics.get('average_time_ms', 0)
        }
    }
    
    print("\nTest Summary:")
    print(json.dumps(summary, indent=2))
    
    return summary


async def test_error_handling():
    """Test error handling and dead-letter queue"""
    
    print("\n" + "=" * 80)
    print("ERROR HANDLING TEST")
    print("=" * 80)
    
    orchestrator = ArticleOrchestrator()
    
    # Test with minimal article (should be rejected by Scout)
    minimal_article = {
        "article_url": "",
        "title": "Too Short",
        "content": "This is way too short.",
        "source": "Unknown"
    }
    
    print("\nProcessing minimal article (should be rejected)...")
    result = await orchestrator.process_article(minimal_article)
    
    print(f"Result Status: {result['status']}")
    print(f"Article ID: {result['article_id']}")
    
    if result['status'] == "REJECTED_BY_SCOUT":
        print("✓ Article correctly rejected by Scout due to low quality")
    else:
        print(f"Article status: {result['status']}")
    
    print("\n" + "=" * 80)


async def main():
    """Run all tests"""
    
    try:
        # Run full pipeline test
        await test_full_pipeline()
        
        # Run error handling test
        await test_error_handling()
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
