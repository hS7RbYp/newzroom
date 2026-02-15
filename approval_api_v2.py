"""
FastAPI Approval Service - Simple working version

REST API for article approval workflow
"""

import asyncio
import os
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
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

# FastAPI app (no middleware to avoid version conflicts)
app = FastAPI(
    title="Newsroom AI - Article Approval API",
    version="1.0.0",
    description="Human approval system for AI-generated articles"
)

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
    """
    try:
        article_id = f"article-{os.urandom(8).hex()}"
        
        # Prepare article data
        article_data = {
            "id": article_id,
            "title": article.title,
            "content": article.content,
            "source": article.source,
            "article_url": article.article_url,
            "submitted_at": asyncio.get_event_loop().time()
        }
        
        # Submit to orchestrator (non-blocking)
        background_tasks.add_task(
            orchestrator.process_article,
            article_id,
            article_data
        )
        
        logger.info(f"Article {article_id} submitted to pipeline")
        
        return {
            "status": "submitted",
            "article_id": article_id,
            "message": "Article submitted to pipeline"
        }
    
    except Exception as e:
        logger.error(f"Error submitting article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/approval/queue")
async def get_queue():
    """Get pending articles in approval queue"""
    try:
        queue_items = await approval_queue.get_queue()
        return {
            "status": "success",
            "count": len(queue_items),
            "items": queue_items
        }
    except Exception as e:
        logger.error(f"Error getting queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/approval/queue/stats")
async def get_stats():
    """Get approval queue statistics"""
    try:
        stats = await approval_queue.get_approval_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/approval/{article_id}")
async def get_article(article_id: str):
    """Get article details"""
    try:
        queue_items = await approval_queue.get_queue()
        for item in queue_items:
            if item.get("id") == article_id:
                return {
                    "status": "success",
                    "article": item
                }
        raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        logger.error(f"Error getting article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/approval/{article_id}/approve")
async def approve_article(article_id: str, decision: ApprovalDecision):
    """Approve article for publishing"""
    try:
        result = await approval_queue.approve_article(
            article_id,
            decision.reviewer_id,
            decision.notes or ""
        )
        
        if result:
            logger.info(f"Article {article_id} approved by {decision.reviewer_id}")
            return {
                "status": "success",
                "message": "Article approved",
                "article_id": article_id
            }
        else:
            raise HTTPException(status_code=404, detail="Article not found in queue")
    
    except Exception as e:
        logger.error(f"Error approving article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/approval/{article_id}/reject")
async def reject_article(article_id: str, rejection: RejectionReason):
    """Reject article"""
    try:
        result = await approval_queue.reject_article(
            article_id,
            rejection.reason
        )
        
        if result:
            logger.info(f"Article {article_id} rejected by {rejection.reviewer_id}")
            return {
                "status": "success",
                "message": "Article rejected",
                "article_id": article_id
            }
        else:
            raise HTTPException(status_code=404, detail="Article not found in queue")
    
    except Exception as e:
        logger.error(f"Error rejecting article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Approval API starting up")
    logger.info(f"Orchestrator: {orchestrator}")
    logger.info(f"Approval Queue: {approval_queue}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Approval API shutting down")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )
