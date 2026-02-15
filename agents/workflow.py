"""
Multi-Agent Workflow - Article Publishing Pipeline

Demonstrates end-to-end article processing through the agent mesh.
Includes workflow coordination, error handling, and metrics collection.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from orchestrator import ArticleOrchestrator, PipelineMetrics
from config import get_config
from azure.cosmos import CosmosClient
from azure.servicebus import ServiceBusClient

logger = logging.getLogger("workflow")
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


@dataclass
class WorkflowMetrics:
    """Track metrics across multiple article workflows"""
    total_articles_processed: int = 0
    successful_articles: int = 0
    rejected_articles: int = 0
    failed_articles: int = 0
    total_time_ms: float = 0.0
    average_time_per_article_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "total": self.total_articles_processed,
            "successful": self.successful_articles,
            "rejected": self.rejected_articles,
            "failed": self.failed_articles,
            "total_time_ms": self.total_time_ms,
            "average_time_ms": self.average_time_per_article_ms,
            "timestamp": datetime.utcnow().isoformat()
        }


class ArticleWorkflow:
    """Manages multi-article workflow with batching and retry logic"""
    
    def __init__(self):
        self.config = get_config()
        self.orchestrator = ArticleOrchestrator()
        self.metrics = WorkflowMetrics()
    
    async def process_articles_batch(
        self,
        articles: List[Dict[str, Any]],
        max_concurrent: int = 3,
        retry_failed: bool = True
    ) -> Dict[str, Any]:
        """
        Process a batch of articles concurrently
        
        Args:
            articles: List of article data {url, title, content, source}
            max_concurrent: Maximum concurrent articles processing
            retry_failed: Whether to retry failed articles
            
        Returns:
            Workflow summary with metrics
        """
        logger.info(f"Starting batch workflow: {len(articles)} articles")
        
        start_time = datetime.utcnow()
        results = []
        
        # Process articles with concurrency control
        for i in range(0, len(articles), max_concurrent):
            batch = articles[i : i + max_concurrent]
            batch_tasks = [
                self.orchestrator.process_article(article)
                for article in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
            
            logger.info(f"Batch {i // max_concurrent + 1} complete: {len(batch)} articles")
        
        # Process results and update metrics
        for result in results:
            self.metrics.total_articles_processed += 1
            
            if isinstance(result, Exception):
                self.metrics.failed_articles += 1
                logger.error(f"Article failed: {str(result)}")
            elif result.get("status") == "PUBLISHED":
                self.metrics.successful_articles += 1
                logger.info(f"Article published: {result.get('article_id')}")
            else:
                self.metrics.rejected_articles += 1
                logger.info(f"Article rejected: {result.get('status')}")
        
        # Calculate final metrics
        total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.metrics.total_time_ms = total_time
        if self.metrics.total_articles_processed > 0:
            self.metrics.average_time_per_article_ms = (
                total_time / self.metrics.total_articles_processed
            )
        
        return self._build_workflow_summary(results)
    
    async def process_article_stream(
        self,
        articles_generator,
        batch_size: int = 5,
        max_concurrent: int = 3
    ):
        """
        Process a continuous stream of articles
        
        Args:
            articles_generator: Async generator yielding articles
            batch_size: Articles per batch
            max_concurrent: Concurrent articles
            
        Yields:
            Workflow events and metrics
        """
        batch = []
        
        async for article in articles_generator:
            batch.append(article)
            
            if len(batch) >= batch_size:
                logger.info(f"Processing stream batch: {len(batch)} articles")
                result = await self.process_articles_batch(
                    batch,
                    max_concurrent=max_concurrent
                )
                yield result
                batch = []
        
        # Process remaining articles
        if batch:
            logger.info(f"Processing final batch: {len(batch)} articles")
            result = await self.process_articles_batch(
                batch,
                max_concurrent=max_concurrent
            )
            yield result
    
    async def save_workflow_metrics(self, summary: Dict[str, Any]):
        """Save workflow metrics to Cosmos DB"""
        try:
            cosmos_client = CosmosClient(
                url=self.config.cosmos_db.endpoint,
                credential=self.config.cosmos_db.key
            )
            
            database = cosmos_client.get_database_client(
                self.config.cosmos_db.database_name
            )
            
            # Try to get or create workflow-metrics container
            try:
                container = database.get_container_client("workflow-metrics")
            except:
                # Create container if it doesn't exist
                logger.info("Creating workflow-metrics container")
                container = database.create_container(
                    id="workflow-metrics",
                    partition_key="/workflow_id"
                )
            
            container.create_item(summary)
            logger.info("Workflow metrics saved to Cosmos DB")
            
        except Exception as e:
            logger.warning(f"Could not save metrics to Cosmos DB: {str(e)}")
    
    async def publish_workflow_event(
        self,
        event_type: str,
        summary: Dict[str, Any]
    ):
        """Publish workflow event to Service Bus"""
        try:
            client = ServiceBusClient.from_connection_string(
                self.config.service_bus.connection_string
            )
            
            sender = client.get_topic_sender(
                self.config.service_bus.agent_events_topic
            )
            
            event = {
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": summary
            }
            
            sender.send_messages(json.dumps(event))
            logger.info(f"Published workflow event: {event_type}")
            
        except Exception as e:
            logger.warning(f"Could not publish workflow event: {str(e)}")
    
    def _build_workflow_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build workflow summary from results"""
        successful_results = [
            r for r in results 
            if isinstance(r, dict) and r.get("status") == "PUBLISHED"
        ]
        
        return {
            "workflow_id": self._generate_workflow_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self.metrics.to_dict(),
            "articles_processed": len(results),
            "successful": len(successful_results),
            "failed": len(results) - len(successful_results),
            "published_articles": [
                {
                    "article_id": r.get("article_id"),
                    "url": r.get("result", {}).get("published_url"),
                    "quality_score": r.get("result", {}).get("quality_score"),
                    "processing_time_ms": r.get("metrics", {}).get("total_time_ms")
                }
                for r in successful_results
            ]
        }
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        import uuid
        return f"workflow-{uuid.uuid4().hex[:8]}"


# ============================================================================
# Sample Workflows
# ============================================================================

async def workflow_sample_articles():
    """Sample workflow with predefined articles"""
    logger.info("Running sample articles workflow")
    
    articles = [
        {
            "article_url": "https://news.example.com/ai-breakthrough",
            "title": "AI Researchers Achieve Major Breakthrough in Large Language Models",
            "content": """
            Scientists announced a major breakthrough in artificial intelligence today.
            A new large language model has achieved state-of-the-art performance on multiple
            benchmarks. The model demonstrates improved reasoning and understanding capabilities.
            """,
            "source": "Tech News Daily"
        },
        {
            "article_url": "https://news.example.com/climate-summit",
            "title": "Global Climate Summit Reaches Historic Agreement",
            "content": """
            World leaders have reached a historic agreement on climate action.
            The new accord commits nations to ambitious emissions reduction targets and
            establishes a $100 billion fund for climate initiatives in developing countries.
            """,
            "source": "Global News Network"
        },
        {
            "article_url": "https://news.example.com/space-mission",
            "title": "NASA Launches New Deep Space Exploration Mission",
            "content": """
            NASA has successfully launched an ambitious new mission to explore
            previously unknown regions of deep space. The mission will use advanced
            telescopes and sensors to search for signs of habitable exoplanets.
            """,
            "source": "Space Research Weekly"
        }
    ]
    
    workflow = ArticleWorkflow()
    summary = await workflow.process_articles_batch(articles)
    
    await workflow.save_workflow_metrics(summary)
    await workflow.publish_workflow_event("batch_complete", summary)
    
    print("\n" + "=" * 70)
    print("Sample Workflow Complete")
    print("=" * 70)
    print(json.dumps(summary, indent=2))
    
    return summary


async def workflow_stream_articles():
    """Sample workflow with article stream"""
    logger.info("Running stream workflow")
    
    async def article_stream():
        """Simulate continuous article stream"""
        articles = [
            {
                "article_url": f"https://news.example.com/article-{i}",
                "title": f"Breaking News Article #{i}",
                "content": f"Content for article {i}. This is a news article about current events.",
                "source": "News Stream"
            }
            for i in range(10)
        ]
        
        for article in articles:
            yield article
            await asyncio.sleep(0.5)  # Simulate arrival delay
    
    workflow = ArticleWorkflow()
    
    async for event in workflow.process_article_stream(
        article_stream(),
        batch_size=3,
        max_concurrent=2
    ):
        logger.info(f"Stream workflow event: {event['metrics']}")
    
    return event


async def main():
    """Run example workflows"""
    print("\n" + "=" * 70)
    print("Multi-Agent Article Publishing Workflow")
    print("=" * 70)
    
    # Run sample articles workflow
    await workflow_sample_articles()
    
    print("\n" + "=" * 70)
    print("Workflow execution complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
