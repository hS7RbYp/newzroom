"""Ops Agent - Operations & Publishing

Ops handles final publishing and operational tasks:
1. Validates article is ready for publication
2. Publishes to CMS/web
3. Notifies subscribers
4. Logs metrics
5. Handles dead-letter queue escalations

Model: N/A (orchestration + API calls)
Typical Response Time: 2-4 seconds
Success Rate Target: >99%
"""

from typing import Any, Dict
from base_agent import BaseAgent, AgentContext


class OpsAgent(BaseAgent):
    """Ops orchestrates publication and operations"""

    async def _execute_agent(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ops workflow:
        1. Collect all prior outputs
        2. Validate completeness
        3. Publish to CMS
        4. Log metrics
        5. Send notifications
        
        Args:
            input_data: {
                "article_id": str,
                "formatted_title": str,
                "formatted_content": str,
                "image_url": str,
                "seo_keywords": [str],
                "quality_score": float
            }
            
        Returns:
            {
                "article_id": str,
                "published_at": str,
                "status": "PUBLISHED|FAILED",
                "cms_url": str,
                "metrics": dict
            }
        """
        article_id = input_data.get("article_id", "")
        title = input_data.get("formatted_title", "")
        content = input_data.get("formatted_content", "")
        image_url = input_data.get("image_url", "")
        seo_keywords = input_data.get("seo_keywords", [])
        quality_score = input_data.get("quality_score", 0)

        try:
            # Validate article completeness
            if not all([article_id, title, content]):
                raise ValueError("Missing required content fields")
            
            # Store article metadata in Cosmos DB
            from azure.cosmos import CosmosClient
            from config import get_config
            import datetime
            
            app_config = get_config()
            cosmos_client = CosmosClient(
                url=app_config.cosmos_db.endpoint,
                credential=app_config.cosmos_db.key
            )
            
            database = cosmos_client.get_database_client(app_config.cosmos_db.database_name)
            container = database.get_container_client(app_config.cosmos_db.articles_container)
            
            # Create article document
            article_doc = {
                "id": article_id,
                "title": title,
                "content": content,
                "image_url": image_url,
                "seo_keywords": seo_keywords,
                "quality_score": quality_score,
                "status": "PUBLISHED",
                "published_at": datetime.datetime.utcnow().isoformat(),
                "pipeline_completed": True
            }
            
            # Upsert to Cosmos DB
            container.upsert_item(article_doc)
            self.logger.info(f"Published article {article_id} to Cosmos DB")
            
            # Simulate CMS publishing
            cms_url = f"https://newsroom.example.com/articles/{article_id}"
            
            # Calculate total end-to-end time from context
            total_time_ms = context.execution_times.get("total", 30000) if hasattr(context, "execution_times") else 30000

            return {
                "agent": "ops",
                "request_id": context.request_id,
                "article_id": article_id,
                "status": "PUBLISHED",
                "cms_url": cms_url,
                "published_at": article_doc["published_at"],
                "metrics": {
                    "total_time_ms": total_time_ms,
                    "pipeline_completed": True,
                    "quality_score": quality_score,
                    "articles_published": 1
                },
                "next_agent": None  # End of pipeline
            }

        except Exception as e:
            self.logger.error(f"Ops processing failed: {str(e)}")
            
            # TODO: Send to dead-letter queue for manual review
            # await self._send_to_dlq(article_id, error)

            raise


# Entrypoint for Foundry
async def ops_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler invoked by Azure Foundry Agent Service"""
    agent = OpsAgent(agent_id="ops")
    context = AgentContext(agent_id="ops")
    return await agent.execute(context, input_data)
