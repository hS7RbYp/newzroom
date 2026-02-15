"""
FastAPI Approval Service

REST API for article approval workflow:
- GET /api/approval/queue - List pending articles
- GET /api/approval/queue/stats - Get approval statistics
- GET /api/approval/{article_id} - Get article details
- POST /api/approval/{article_id}/approve - Approve article
- POST /api/approval/{article_id}/reject - Reject article
- POST /api/articles/submit - Submit article to pipeline
"""

import asyncio
import os
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys

# Add agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from approval import get_approval_queue, ApprovalStatus
from orchestrator import ArticleOrchestrator
from config import get_config


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("approval_api")

# FastAPI app
app = FastAPI(
    title="Newsroom AI - Article Approval API",
    version="1.0.0",
    description="Human approval system for AI-generated articles"
)

# CORS middleware - commented out to debug
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,
#     allow_methods=["GET", "POST", "OPTIONS"],
#     allow_headers=["*"],
# )

# Global instances
orchestrator = ArticleOrchestrator()
approval_queue = get_approval_queue()


# ============================================================================
# Pydantic Models
# ============================================================================

class ArticleSubmission(BaseModel):
    """Article submission to pipeline"""
    title: str
    content: str
    source: str
    article_url: Optional[str] = None


class ApprovalDecision(BaseModel):
    """Human approval decision"""
    reviewer_id: str
    notes: Optional[str] = None


class RejectionReason(BaseModel):
    """Article rejection with reason"""
    reviewer_id: str
    reason: str


class ApprovalQueueItem(BaseModel):
    """Article in approval queue"""
    article_id: str
    title: str
    content_preview: str
    confidence_score: float
    quality_score: float
    brand_compliant: bool
    image_url: Optional[str]
    created_at: str
    queued_at: str


class ApprovalStats(BaseModel):
    """Approval queue statistics"""
    pending: int
    approved: int
    rejected: int
    total: int


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "approval",
        "version": "1.0.0"
    }


@app.post("/api/articles/submit")
async def submit_article(
    article: ArticleSubmission,
    background_tasks: BackgroundTasks
) -> dict:
    """
    Submit article to AI pipeline
    
    - Title, content, and source are required
    - Article is processed through all agents
    - Smart routing determines if it needs approval
    """
    try:
        logger.info(f"Submitting article: {article.title[:50]}...")
        
        article_data = {
            "title": article.title,
            "content": article.content,
            "source": article.source,
            "article_url": article.article_url or f"submitted://{article.source}"
        }
        
        # Process in background
        background_tasks.add_task(
            orchestrator.process_article,
            article_data
        )
        
        return {
            "status": "accepted",
            "message": "Article submitted for processing",
            "source": article.source
        }
    
    except Exception as e:
        logger.error(f"Failed to submit article: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/approval/queue", response_model=List[ApprovalQueueItem])
async def get_approval_queue_endpoint() -> List[dict]:
    """
    Get articles pending human approval
    
    Returns articles with:
    - Confidence scores
    - Quality metrics
    - Brand compliance status
    - Image preview
    """
    try:
        logger.info("Fetching approval queue")
        items = await approval_queue.get_queue(status=ApprovalStatus.PENDING_REVIEW)
        return items
    
    except Exception as e:
        logger.error(f"Failed to get queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/approval/queue/stats", response_model=ApprovalStats)
async def get_approval_stats() -> dict:
    """Get approval queue statistics"""
    try:
        stats = await approval_queue.get_approval_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/approval/{article_id}")
async def get_article_details(article_id: str) -> dict:
    """
    Get full article details for review
    
    Includes:
    - Full content
    - All agent outputs (facts, entities, sentiment, etc.)
    - Image URL
    - SEO keywords
    - Confidence scores
    """
    try:
        logger.info(f"Fetching article details: {article_id}")
        items = await approval_queue.get_queue()
        
        for item in items:
            if item.get("article_id") == article_id:
                return item
        
        raise HTTPException(status_code=404, detail="Article not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/approval/{article_id}/approve")
async def approve_article(
    article_id: str,
    decision: ApprovalDecision,
    background_tasks: BackgroundTasks
) -> dict:
    """
    Approve article for publication
    
    Once approved:
    - Ops agent publishes to Cosmos DB
    - Article goes live
    - Notifications sent to stakeholders
    """
    try:
        logger.info(f"Approving article {article_id} by {decision.reviewer_id}")
        
        result = await approval_queue.approve_article(
            article_id=article_id,
            reviewer_id=decision.reviewer_id,
            reviewer_notes=decision.notes or ""
        )
        
        if result.get("status") == "approved":
            # Schedule Ops agent to publish the article
            background_tasks.add_task(
                _publish_approved_article,
                article_id
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to approve article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/approval/{article_id}/reject")
async def reject_article(
    article_id: str,
    rejection: RejectionReason
) -> dict:
    """
    Reject article
    
    Article will:
    - Be marked as rejected
    - Not be published
    - Be available for revision or deletion
    """
    try:
        logger.info(f"Rejecting article {article_id} by {rejection.reviewer_id}")
        
        result = await approval_queue.reject_article(
            article_id=article_id,
            article_data={"article_id": article_id},
            reason=rejection.reason,
            reviewer_id=rejection.reviewer_id
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to reject article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Background Tasks
# ============================================================================

async def _publish_approved_article(article_id: str) -> None:
    """
    Publish approved article using Ops agent
    
    This is called after approval to actually publish to CMS
    """
    try:
        logger.info(f"Publishing approved article {article_id}")
        # TODO: Call Ops agent directly to publish
        # from ops import OpsAgent
        # ops = OpsAgent()
        # await ops.publish_article(article_id)
    except Exception as e:
        logger.error(f"Failed to publish article {article_id}: {str(e)}")


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Approval API starting up")
    logger.info("Approval queue initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Approval API shutting down")


# ============================================================================
# Root endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Newsroom AI Approval System",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /api/health",
            "submit": "POST /api/articles/submit",
            "queue": "GET /api/approval/queue",
            "stats": "GET /api/approval/queue/stats",
            "details": "GET /api/approval/{article_id}",
            "approve": "POST /api/approval/{article_id}/approve",
            "reject": "POST /api/approval/{article_id}/reject"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "approval_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
