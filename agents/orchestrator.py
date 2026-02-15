"""
Agent Orchestration Pipeline

Manages the multi-agent workflow:
- Scout → Prof → Scribe → Pixel → Judge → Ops
- Tracks execution metrics
- Handles failures and dead-letter queuing
- Coordinates Service Bus messaging
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

from base_agent import AgentContext
from scout import ScoutAgent
from prof import ProfAgent
from scribe import ScribeAgent
from judge import JudgeAgent
from pixel import PixelAgent
from ops import OpsAgent
from approval import get_approval_queue, ConfidenceLevel
from config import get_config


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("orchestrator")


class PipelineMetrics:
    """Track execution metrics across the pipeline"""
    
    def __init__(self, article_id: str):
        self.article_id = article_id
        self.start_time = datetime.utcnow()
        self.agent_times: Dict[str, float] = {}
        self.agent_results: Dict[str, Any] = {}
        self.errors: Dict[str, str] = {}
        self.final_status = "IN_PROGRESS"
    
    def record_agent_start(self, agent_name: str):
        """Record when an agent starts"""
        self.agent_times[f"{agent_name}_start"] = datetime.utcnow()
    
    def record_agent_end(self, agent_name: str, result: Dict[str, Any]):
        """Record when an agent completes and store result"""
        self.agent_times[f"{agent_name}_end"] = datetime.utcnow()
        self.agent_results[agent_name] = result
        
        if f"{agent_name}_start" in self.agent_times:
            start = self.agent_times[f"{agent_name}_start"]
            end = self.agent_times[f"{agent_name}_end"]
            duration = (end - start).total_seconds() * 1000
            self.agent_times[f"{agent_name}_duration_ms"] = duration
    
    def record_error(self, agent_name: str, error: str):
        """Record an error for an agent"""
        self.errors[agent_name] = error
    
    def get_total_time_ms(self) -> float:
        """Get total pipeline execution time in milliseconds"""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds() * 1000
        return duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for storage"""
        return {
            "article_id": self.article_id,
            "start_time": self.start_time.isoformat(),
            "total_time_ms": self.get_total_time_ms(),
            "agent_times": {k: v.isoformat() if isinstance(v, datetime) else v 
                           for k, v in self.agent_times.items()},
            "agent_results": self.agent_results,
            "errors": self.errors,
            "final_status": self.final_status,
            "timestamp": datetime.utcnow().isoformat()
        }


class ArticleOrchestrator:
    """Main orchestrator for multi-agent article processing"""
    
    def __init__(self):
        self.config = get_config()
        self.agents = {
            "scout": ScoutAgent(agent_id="scout"),
            "prof": ProfAgent(agent_id="prof"),
            "scribe": ScribeAgent(agent_id="scribe"),
            "judge": JudgeAgent(agent_id="judge"),
            "pixel": PixelAgent(agent_id="pixel"),
            "ops": OpsAgent(agent_id="ops")
        }
        self.approval_queue = get_approval_queue()
        logger.info("Orchestrator initialized with 6 agents + approval system")
    
    async def process_article(
        self,
        article_data: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an article through the full pipeline
        
        Pipeline: Scout → Prof → Scribe → Judge → Pixel → Ops
        
        Args:
            article_data: {
                "article_url": str,
                "title": str,
                "content": str,
                "source": str
            }
            request_id: Optional request ID for tracking
            
        Returns:
            Final pipeline result with all metrics
        """
        if not request_id:
            request_id = str(uuid.uuid4())
        
        article_id = str(uuid.uuid4())
        metrics = PipelineMetrics(article_id)
        
        logger.info(f"Starting article pipeline: {request_id}")
        logger.info(f"Article ID: {article_id}")
        
        # Create context that flows through pipeline
        context = AgentContext(agent_id="orchestrator", request_id=request_id)
        context.article_id = article_id
        
        # Initialize pipeline data
        pipeline_data = {
            **article_data,
            "article_id": article_id,
            "request_id": request_id
        }
        
        try:
            # Stage 1: Scout - Initial filtering
            logger.info("Stage 1: Scout (newsworthiness screening)")
            metrics.record_agent_start("scout")
            scout_result = await self._run_agent("scout", pipeline_data, context, metrics)
            if not scout_result or scout_result.get("recommendation") != "PASS":
                logger.info(f"Article rejected by Scout (score: {scout_result.get('score')})")
                metrics.final_status = "REJECTED_BY_SCOUT"
                return self._build_final_response(metrics, pipeline_data)
            
            pipeline_data.update(scout_result)
            
            # Stage 2: Prof - Deep analysis
            logger.info("Stage 2: Prof (fact-checking & entity extraction)")
            metrics.record_agent_start("prof")
            prof_result = await self._run_agent("prof", pipeline_data, context, metrics)
            if not prof_result or prof_result.get("recommendation") not in ["APPROVE", "REVISE"]:
                logger.info(f"Article rejected by Prof")
                metrics.final_status = "REJECTED_BY_PROF"
                return self._build_final_response(metrics, pipeline_data)
            
            pipeline_data.update(prof_result)
            
            # Stage 3: Judge - Quality assurance (can happen in parallel with Scribe)
            logger.info("Stage 3: Judge (quality assurance)")
            metrics.record_agent_start("judge")
            judge_result = await self._run_agent("judge", pipeline_data, context, metrics)
            if judge_result and not judge_result.get("brand_compliant"):
                logger.warning(f"Article flagged for brand compliance issues")
            
            pipeline_data.update(judge_result)
            
            # Stage 4: Scribe - Content formatting (parallel with Judge)
            logger.info("Stage 4: Scribe (content formatting & SEO)")
            metrics.record_agent_start("scribe")
            scribe_result = await self._run_agent("scribe", pipeline_data, context, metrics)
            pipeline_data.update(scribe_result)
            
            # Stage 5: Pixel - Image generation
            logger.info("Stage 5: Pixel (image generation)")
            metrics.record_agent_start("pixel")
            pixel_result = await self._run_agent("pixel", pipeline_data, context, metrics)
            if pixel_result:
                pipeline_data.update(pixel_result)
            
            # Stage 5.5: Smart Routing - Approval queue decision
            logger.info("Stage 5.5: Smart Routing (confidence-based approval)")
            metrics.record_agent_start("smart_router")
            routing_result = await self.approval_queue.route_article(article_id, pipeline_data)
            pipeline_data.update(routing_result)
            metrics.record_agent_end("smart_router", routing_result)
            
            if routing_result["action"] == "AUTO_PUBLISH":
                logger.info(f"Article {article_id} auto-published (high confidence)")
                metrics.final_status = "AUTO_PUBLISHED"
            elif routing_result["action"] == "QUEUE_FOR_REVIEW":
                logger.info(f"Article {article_id} queued for human review (medium confidence)")
                metrics.final_status = "PENDING_REVIEW"
                return self._build_final_response(metrics, pipeline_data)
            elif routing_result["action"] == "REJECT":
                logger.info(f"Article {article_id} rejected (low confidence)")
                metrics.final_status = "REJECTED"
                return self._build_final_response(metrics, pipeline_data)
            
            # Stage 6: Ops - Publishing (only for AUTO_PUBLISHED articles)
            logger.info("Stage 6: Ops (publication & metrics)")
            metrics.record_agent_start("ops")
            ops_result = await self._run_agent("ops", pipeline_data, context, metrics)
            pipeline_data.update(ops_result)
            
            metrics.final_status = "PUBLISHED"
            logger.info(f"Article successfully published: {article_id}")
            
            return self._build_final_response(metrics, pipeline_data)
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            metrics.final_status = "ERROR"
            metrics.record_error("pipeline", str(e))
            await self._handle_failure(article_id, pipeline_data, str(e))
            return self._build_final_response(metrics, pipeline_data)
    
    async def _run_agent(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        context: AgentContext,
        metrics: PipelineMetrics
    ) -> Optional[Dict[str, Any]]:
        """Run a single agent and track metrics"""
        try:
            agent = self.agents[agent_name]
            result = await agent.execute(context, input_data)
            metrics.record_agent_end(agent_name, result)
            
            duration_ms = metrics.agent_times.get(f"{agent_name}_duration_ms", 0)
            logger.info(f"{agent_name} completed in {duration_ms:.0f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {str(e)}")
            metrics.record_error(agent_name, str(e))
            raise
    
    async def _handle_failure(
        self,
        article_id: str,
        pipeline_data: Dict[str, Any],
        error: str
    ):
        """Handle pipeline failure - send to dead-letter queue"""
        try:
            from azure.servicebus import ServiceBusClient
            
            # Create failure message
            failure_message = {
                "article_id": article_id,
                "error": error,
                "data": pipeline_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to dead-letter queue
            client = ServiceBusClient.from_connection_string(
                self.config.service_bus.connection_string
            )
            
            sender = client.get_topic_sender(self.config.service_bus.dead_letter_topic)
            sender.send_messages(str(json.dumps(failure_message)))
            logger.info(f"Article sent to dead-letter queue: {article_id}")
            
        except Exception as dlq_error:
            logger.error(f"Failed to send to dead-letter queue: {str(dlq_error)}")
    
    def _build_final_response(
        self,
        metrics: PipelineMetrics,
        pipeline_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build final response with metrics"""
        return {
            "status": metrics.final_status,
            "article_id": pipeline_data.get("article_id", ""),
            "metrics": metrics.to_dict(),
            "result": {
                "published_url": pipeline_data.get("cms_url"),
                "quality_score": pipeline_data.get("quality_score"),
                "brand_compliant": pipeline_data.get("brand_compliant", True),
                "image_url": pipeline_data.get("image_url"),
                "seo_keywords": pipeline_data.get("seo_keywords", [])
            }
        }


async def run_pipeline_test():
    """Test the orchestration pipeline with sample article"""
    orchestrator = ArticleOrchestrator()
    
    test_article = {
        "article_url": "https://example.com/test-article",
        "title": "AI Breakthrough: New Model Achieves Record Performance",
        "content": """
        A major breakthrough in artificial intelligence has been announced today.
        Researchers have developed a new machine learning model that achieves state-of-the-art
        results across multiple benchmarks. The model uses advanced techniques including
        transformer architecture and novel attention mechanisms.
        
        Dr. Jane Smith, lead researcher at Tech Institute, stated: "This represents a 
        significant milestone in AI development. The model's performance exceeds previous 
        benchmarks by 15%, opening new possibilities for practical applications."
        
        The research will be published in a peer-reviewed journal next month and the code
        will be open-sourced to the community. Industry experts predict this could accelerate
        development in areas like natural language processing, computer vision, and robotics.
        """,
        "source": "Tech News Daily"
    }
    
    result = await orchestrator.process_article(
        test_article,
        request_id="test-pipeline-001"
    )
    
    print("\n" + "=" * 70)
    print("Pipeline Execution Complete")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    
    # Store metrics in Cosmos DB
    try:
        from azure.cosmos import CosmosClient
        
        config = get_config()
        cosmos_client = CosmosClient(
            url=config.cosmos_db.endpoint,
            credential=config.cosmos_db.key
        )
        
        database = cosmos_client.get_database_client(config.cosmos_db.database_name)
        container = database.get_container_client("pipeline-metrics")
        
        container.create_item(result["metrics"])
        print(f"\nMetrics saved to Cosmos DB")
        
    except Exception as e:
        logger.warning(f"Could not save metrics to Cosmos DB: {str(e)}")
    
    return result


if __name__ == "__main__":
    result = asyncio.run(run_pipeline_test())
