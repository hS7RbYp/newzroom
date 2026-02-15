"""
Human Approval System for Article Pipeline

Manages the approval queue with smart routing:
- Green (score > 8.5): Auto-publish
- Yellow (6.5-8.5): Approval queue
- Red (< 6.5): Rejected
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid

from azure.cosmos import CosmosClient, PartitionKey
from config import get_config


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("approval")


class ApprovalStatus(str, Enum):
    """Article approval status states"""
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    AUTO_PUBLISHED = "AUTO_PUBLISHED"
    REVISION_REQUESTED = "REVISION_REQUESTED"


class ConfidenceLevel(str, Enum):
    """Confidence scoring levels"""
    GREEN = "GREEN"      # High confidence, auto-publish
    YELLOW = "YELLOW"    # Medium confidence, needs review
    RED = "RED"          # Low confidence, reject


class ApprovalQueue:
    """Manages article approval workflow"""
    
    def __init__(self):
        config = get_config()
        self.cosmos_endpoint = config.cosmos_db.endpoint
        self.cosmos_key = config.cosmos_db.key
        self.client = CosmosClient(self.cosmos_endpoint, self.cosmos_key)
        self.database = self.client.get_database_client("articles")
        
        # Initialize approval container
        try:
            self.approval_container = self.database.get_container_client("approval-queue")
            logger.info("Approval queue container found")
        except:
            # Create if doesn't exist
            self.approval_container = self.database.create_container(
                id="approval-queue",
                partition_key=PartitionKey(path="/status"),
                offer_throughput=400
            )
            logger.info("Approval queue container created")
    
    async def calculate_confidence_score(
        self,
        article_data: Dict[str, Any]
    ) -> float:
        """
        Calculate overall confidence score (0-10) based on agent outputs
        
        Factors:
        - Scout score (20%)
        - Prof fact-check score (25%)
        - Judge quality score (25%)
        - Brand compliance (30%)
        """
        scout_score = article_data.get("score", 5.0) * 0.2
        prof_score = article_data.get("fact_check_score", 5.0) * 0.25
        judge_score = article_data.get("quality_score", 5.0) * 0.25
        brand_bonus = (10.0 * 0.3) if article_data.get("brand_compliant", False) else (5.0 * 0.3)
        
        confidence = scout_score + prof_score + judge_score + brand_bonus
        return min(10.0, confidence)  # Cap at 10.0
    
    def get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine confidence level from score"""
        if score > 8.5:
            return ConfidenceLevel.GREEN
        elif score >= 6.5:
            return ConfidenceLevel.YELLOW
        else:
            return ConfidenceLevel.RED
    
    async def route_article(
        self,
        article_id: str,
        article_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route article based on confidence score
        
        Returns:
        - GREEN: Ready to auto-publish
        - YELLOW: Add to approval queue
        - RED: Reject article
        """
        confidence_score = await self.calculate_confidence_score(article_data)
        confidence_level = self.get_confidence_level(confidence_score)
        
        routing_result = {
            "article_id": article_id,
            "confidence_score": round(confidence_score, 2),
            "confidence_level": confidence_level,
            "action": None,
            "reason": None
        }
        
        if confidence_level == ConfidenceLevel.GREEN:
            routing_result["action"] = "AUTO_PUBLISH"
            routing_result["reason"] = f"High confidence score: {confidence_score:.1f}/10"
        
        elif confidence_level == ConfidenceLevel.YELLOW:
            routing_result["action"] = "QUEUE_FOR_REVIEW"
            routing_result["reason"] = f"Medium confidence score: {confidence_score:.1f}/10"
            await self.add_to_queue(article_id, article_data, confidence_score)
        
        else:  # RED
            routing_result["action"] = "REJECT"
            routing_result["reason"] = f"Low confidence score: {confidence_score:.1f}/10"
            await self.reject_article(article_id, article_data, "Low confidence score")
        
        logger.info(f"Article {article_id} routed to: {routing_result['action']}")
        return routing_result
    
    async def add_to_queue(
        self,
        article_id: str,
        article_data: Dict[str, Any],
        confidence_score: float
    ) -> None:
        """Add article to approval queue"""
        approval_doc = {
            "id": article_id,
            "status": ApprovalStatus.PENDING_REVIEW,
            "article_id": article_id,
            "confidence_score": confidence_score,
            "title": article_data.get("title", "Untitled"),
            "content_preview": article_data.get("content", "")[:500],
            "image_url": article_data.get("image_url"),
            "seo_keywords": article_data.get("seo_keywords", []),
            "fact_check_score": article_data.get("fact_check_score"),
            "quality_score": article_data.get("quality_score"),
            "brand_compliant": article_data.get("brand_compliant"),
            "entities": article_data.get("entities", []),
            "sentiment": article_data.get("sentiment"),
            "created_at": datetime.utcnow().isoformat(),
            "queued_at": datetime.utcnow().isoformat(),
            "approved_at": None,
            "rejected_at": None,
            "reviewer_id": None,
            "reviewer_notes": None
        }
        
        try:
            self.approval_container.upsert_item(approval_doc)
            logger.info(f"Article {article_id} added to approval queue")
        except Exception as e:
            logger.error(f"Failed to add article to queue: {str(e)}")
            raise
    
    async def get_queue(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get articles in approval queue"""
        try:
            if status:
                query = f"SELECT * FROM c WHERE c.status = @status ORDER BY c.queued_at ASC"
                items = list(self.approval_container.query_items(
                    query=query,
                    parameters=[{"name": "@status", "value": status}]
                ))
            else:
                query = "SELECT * FROM c WHERE c.status = @status ORDER BY c.queued_at ASC"
                items = list(self.approval_container.query_items(
                    query=query,
                    parameters=[{"name": "@status", "value": ApprovalStatus.PENDING_REVIEW}]
                ))
            
            logger.info(f"Retrieved {len(items)} articles from queue (status={status})")
            return items
        except Exception as e:
            logger.error(f"Failed to get queue: {str(e)}")
            return []
    
    async def approve_article(
        self,
        article_id: str,
        reviewer_id: str,
        reviewer_notes: str = ""
    ) -> Dict[str, Any]:
        """Approve article for publication"""
        try:
            # Update approval document
            query = "SELECT * FROM c WHERE c.article_id = @article_id"
            items = list(self.approval_container.query_items(
                query=query,
                parameters=[{"name": "@article_id", "value": article_id}]
            ))
            
            if not items:
                logger.error(f"Article {article_id} not found in approval queue")
                return {"status": "error", "message": "Not found"}
            
            doc = items[0]
            doc["status"] = ApprovalStatus.APPROVED
            doc["approved_at"] = datetime.utcnow().isoformat()
            doc["reviewer_id"] = reviewer_id
            doc["reviewer_notes"] = reviewer_notes
            
            self.approval_container.upsert_item(doc)
            logger.info(f"Article {article_id} approved by {reviewer_id}")
            
            return {
                "status": "approved",
                "article_id": article_id,
                "approved_at": doc["approved_at"],
                "reviewer_id": reviewer_id
            }
        except Exception as e:
            logger.error(f"Failed to approve article: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def reject_article(
        self,
        article_id: str,
        article_data: Dict[str, Any],
        reason: str,
        reviewer_id: str = "system"
    ) -> Dict[str, Any]:
        """Reject article"""
        try:
            rejection_doc = {
                "id": str(uuid.uuid4()),
                "status": ApprovalStatus.REJECTED,
                "article_id": article_id,
                "title": article_data.get("title", "Untitled"),
                "rejection_reason": reason,
                "rejected_at": datetime.utcnow().isoformat(),
                "reviewer_id": reviewer_id,
                "confidence_score": article_data.get("confidence_score", 0)
            }
            
            self.approval_container.upsert_item(rejection_doc)
            logger.info(f"Article {article_id} rejected: {reason}")
            
            return {
                "status": "rejected",
                "article_id": article_id,
                "reason": reason,
                "rejected_at": rejection_doc["rejected_at"]
            }
        except Exception as e:
            logger.error(f"Failed to reject article: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_approval_stats(self) -> Dict[str, Any]:
        """Get approval queue statistics"""
        try:
            query = "SELECT * FROM c"
            items = list(self.approval_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            # Count items by status
            stats = {
                ApprovalStatus.PENDING_REVIEW: 0,
                ApprovalStatus.APPROVED: 0,
                ApprovalStatus.REJECTED: 0
            }
            
            for item in items:
                status = item.get("status")
                if status in stats:
                    stats[status] += 1
            
            return {
                "pending": stats[ApprovalStatus.PENDING_REVIEW],
                "approved": stats[ApprovalStatus.APPROVED],
                "rejected": stats[ApprovalStatus.REJECTED],
                "total": len(items)
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {"error": str(e)}


# Singleton instance
_approval_queue = None


def get_approval_queue() -> ApprovalQueue:
    """Get or create approval queue instance"""
    global _approval_queue
    if _approval_queue is None:
        _approval_queue = ApprovalQueue()
    return _approval_queue
