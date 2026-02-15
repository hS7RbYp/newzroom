"""
Simple Flask Approval Service - No middleware conflicts

REST API for article approval workflow
"""

import asyncio
import os
import json
import logging
from datetime import datetime
import sys

# Add agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from approval import get_approval_queue, ApprovalStatus
from orchestrator import ArticleOrchestrator
from config import get_config


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("approval_api")

# Flask app
app = Flask(__name__)

# Enable CORS for dashboard access from port 3000
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Global instances
orchestrator = ArticleOrchestrator()
approval_queue = get_approval_queue()


# ============================================================================
# Endpoints
# ============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "approval",
        "version": "1.0.0"
    }), 200


@app.route("/api/approval/queue", methods=["GET"])
def get_queue():
    """Get pending articles in approval queue"""
    try:
        # Get optional status parameter
        status = request.args.get("status")
        if status:
            # Convert to enum value if provided
            status_map = {
                "pending": "PENDING_REVIEW",
                "pending_review": "PENDING_REVIEW",
                "approved": "APPROVED",
                "rejected": "REJECTED"
            }
            status = status_map.get(status.lower(), status.upper())
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        queue_items = loop.run_until_complete(approval_queue.get_queue(status))
        loop.close()
        
        # Return list as JSON array
        return Response(json.dumps(queue_items), mimetype='application/json'), 200
    except Exception as e:
        logger.error(f"Error getting queue: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/approval/queue/stats", methods=["GET"])
def get_stats():
    """Get approval queue statistics"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stats = loop.run_until_complete(approval_queue.get_approval_stats())
        loop.close()
        
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/articles/submit", methods=["POST"])
def submit_article():
    """Submit article to AI pipeline"""
    try:
        data = request.get_json()
        
        if not data or not data.get("title") or not data.get("content"):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        article_id = f"article-{os.urandom(8).hex()}"
        
        # Prepare article data
        article_data = {
            "id": article_id,
            "title": data.get("title"),
            "content": data.get("content"),
            "source": data.get("source", "api"),
            "article_url": data.get("article_url"),
            "submitted_at": datetime.now().isoformat()
        }
        
        logger.info(f"Article {article_id} submitted to pipeline")
        
        # For demo: process synchronously instead of background
        # In production, use Celery/RQ for background tasks
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(orchestrator.process_article(article_data, request_id=article_id))
        finally:
            loop.close()
        
        return jsonify({
            "status": "submitted",
            "article_id": article_id,
            "message": "Article processed through pipeline",
            "routing": result.get("status", "unknown")
        }), 200
    
    except Exception as e:
        logger.error(f"Error submitting article: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/approval/<article_id>", methods=["GET"])
def get_article(article_id):
    """Get article details"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        queue_items = loop.run_until_complete(approval_queue.get_queue())
        loop.close()
        
        for item in queue_items:
            if item.get("id") == article_id or item.get("article_id") == article_id:
                return Response(json.dumps(item), mimetype='application/json'), 200
        
        return jsonify({"status": "error", "message": "Article not found"}), 404
    except Exception as e:
        logger.error(f"Error getting article: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/approval/<article_id>/approve", methods=["POST"])
def approve_article(article_id):
    """Approve article for publishing"""
    try:
        data = request.get_json() or {}
        reviewer_id = data.get("reviewer_id", "unknown")
        notes = data.get("notes", "")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(approval_queue.approve_article(article_id, reviewer_id, notes))
        loop.close()
        
        if result:
            logger.info(f"Article {article_id} approved by {reviewer_id}")
            return jsonify({
                "status": "success",
                "message": "Article approved",
                "article_id": article_id
            }), 200
        else:
            return jsonify({"status": "error", "message": "Article not found"}), 404
    
    except Exception as e:
        logger.error(f"Error approving article: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/approval/<article_id>/reject", methods=["POST"])
def reject_article(article_id):
    """Reject article"""
    try:
        data = request.get_json() or {}
        reviewer_id = data.get("reviewer_id", "unknown")
        reason = data.get("reason", "No reason provided")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(approval_queue.reject_article(article_id, reason))
        loop.close()
        
        if result:
            logger.info(f"Article {article_id} rejected by {reviewer_id}: {reason}")
            return jsonify({
                "status": "success",
                "message": "Article rejected",
                "article_id": article_id
            }), 200
        else:
            return jsonify({"status": "error", "message": "Article not found"}), 404
    
    except Exception as e:
        logger.error(f"Error rejecting article: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# Error handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"status": "error", "message": "Internal server error"}), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting Approval API with Flask")
    logger.info(f"Orchestrator: {orchestrator}")
    logger.info(f"Approval Queue: {approval_queue}")
    logger.info("Server running on http://0.0.0.0:8000")
    
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        threaded=True
    )
