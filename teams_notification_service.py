"""
Teams Notification Service for Article Approval

Sends notifications and adaptive cards to Teams webhook when:
- New article arrives for review
- Article is approved/rejected
- Queue reaches capacity
"""

import os
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import aiohttp
from flask import Flask, request, jsonify

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("teams_notifications")

app = Flask(__name__)

# Teams webhook URL (set via environment variable)
# To get this URL: Teams → Channel → Connectors → Incoming Webhook
TEAMS_WEBHOOK_URL = os.getenv(
    "TEAMS_WEBHOOK_URL",
    "https://outlook.webhook.office.com/webhookb2/..."
)

APPROVAL_API_URL = os.getenv("APPROVAL_API_URL", "http://localhost:8000")


class TeamsNotificationService:
    """Service to send notifications to Teams"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def send_notification(self, message: Dict[str, Any]) -> bool:
        """Send notification to Teams webhook"""
        if not self.webhook_url or self.webhook_url.startswith("https://outlook.webhook.office.com/webhookb2/..."):
            logger.warning("Teams webhook not configured. Set TEAMS_WEBHOOK_URL environment variable")
            return False
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(self.webhook_url, json=message) as resp:
                if resp.status == 200:
                    logger.info("✓ Notification sent to Teams")
                    return True
                else:
                    logger.error(f"Failed to send Teams notification: {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Teams notification: {str(e)}")
            return False
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()


async def send_article_notification(article: Dict[str, Any], action: str):
    """Send article notification to Teams"""
    service = TeamsNotificationService(TEAMS_WEBHOOK_URL)
    
    article_id = article.get("id", article.get("article_id"))
    title = article.get("title", "Untitled")
    confidence = article.get("confidence_score", 0)
    
    # Build adaptive card
    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": f"Article {action}: {title}",
        "themeColor": "0078D4" if action == "submitted" else ("28a745" if action == "approved" else "dc3545"),
        "sections": [
            {
                "activityTitle": f"📰 Article {action.upper()}",
                "activitySubtitle": title,
                "facts": [
                    {
                        "name": "Article ID",
                        "value": article_id
                    },
                    {
                        "name": "Confidence Score",
                        "value": f"{confidence:.1f}/10"
                    },
                    {
                        "name": "Status",
                        "value": article.get("status", "Unknown")
                    },
                    {
                        "name": "Time",
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                ],
                "markdown": True
            }
        ],
        "potentialAction": [
            {
                "@type": "ViewAction",
                "name": "Review in Dashboard",
                "target": [
                    f"http://localhost:3000/article/{article_id}"
                ]
            }
        ]
    }
    
    await service.send_notification(card)
    await service.close()


@app.route("/api/notify/article-submitted", methods=["POST"])
def notify_article_submitted():
    """Notify Teams about new article"""
    try:
        data = request.get_json()
        article = data.get("article", {})
        
        asyncio.run(send_article_notification(article, "submitted"))
        
        return jsonify({
            "status": "success",
            "message": "Teams notification sent"
        }), 200
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/notify/article-approved", methods=["POST"])
def notify_article_approved():
    """Notify Teams about article approval"""
    try:
        data = request.get_json()
        article = data.get("article", {})
        reviewer = data.get("reviewer", "Unknown")
        notes = data.get("notes", "")
        
        article["status"] = "Approved"
        article["reviewer"] = reviewer
        
        asyncio.run(send_article_notification(article, "approved"))
        
        return jsonify({
            "status": "success",
            "message": f"Approval notification sent (reviewed by {reviewer})"
        }), 200
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/notify/article-rejected", methods=["POST"])
def notify_article_rejected():
    """Notify Teams about article rejection"""
    try:
        data = request.get_json()
        article = data.get("article", {})
        reviewer = data.get("reviewer", "Unknown")
        reason = data.get("reason", "")
        
        article["status"] = "Rejected"
        article["reason"] = reason
        article["reviewer"] = reviewer
        
        asyncio.run(send_article_notification(article, "rejected"))
        
        return jsonify({
            "status": "success",
            "message": f"Rejection notification sent (reviewed by {reviewer})"
        }), 200
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/notify/queue-update", methods=["POST"])
def notify_queue_update():
    """Notify Teams about queue statistics"""
    try:
        data = request.get_json()
        stats = data.get("stats", {})
        
        pending = stats.get("pending", 0)
        approved = stats.get("approved", 0)
        rejected = stats.get("rejected", 0)
        total = stats.get("total", 0)
        
        # Send summary card
        service = TeamsNotificationService(TEAMS_WEBHOOK_URL)
        
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": "Approval Queue Update",
            "themeColor": "0078D4",
            "sections": [
                {
                    "activityTitle": "📊 Queue Statistics Update",
                    "facts": [
                        {
                            "name": "🟡 Pending Review",
                            "value": str(pending)
                        },
                        {
                            "name": "✅ Approved",
                            "value": str(approved)
                        },
                        {
                            "name": "❌ Rejected",
                            "value": str(rejected)
                        },
                        {
                            "name": "📈 Total",
                            "value": str(total)
                        }
                    ],
                    "markdown": True
                }
            ],
            "potentialAction": [
                {
                    "@type": "ViewAction",
                    "name": "View Dashboard",
                    "target": ["http://localhost:3000"]
                }
            ]
        }
        
        asyncio.run(service.send_notification(card))
        asyncio.run(service.close())
        
        return jsonify({
            "status": "success",
            "message": "Queue update notification sent"
        }), 200
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    webhook_configured = not TEAMS_WEBHOOK_URL.startswith("https://outlook.webhook.office.com/webhookb2/...")
    
    return jsonify({
        "status": "healthy" if webhook_configured else "warning",
        "message": "Teams notification service running",
        "webhook_configured": webhook_configured,
        "port": 5000
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("TEAMS_BOT_PORT", 5000))
    
    logger.info("=" * 60)
    logger.info("Teams Notification Service Starting")
    logger.info("=" * 60)
    logger.info(f"Port: {port}")
    logger.info(f"Approval API: {APPROVAL_API_URL}")
    
    if TEAMS_WEBHOOK_URL.startswith("https://outlook.webhook.office.com/webhookb2/..."):
        logger.warning("")
        logger.warning("⚠️  TEAMS_WEBHOOK_URL not configured!")
        logger.warning("")
        logger.warning("To enable Teams notifications:")
        logger.warning("1. Go to your Teams channel → Connectors")
        logger.warning("2. Search for 'Incoming Webhook' → Configure")
        logger.warning("3. Copy the webhook URL")
        logger.warning("4. Set environment variable:")
        logger.warning("")
        logger.warning('   export TEAMS_WEBHOOK_URL="https://outlook.webhook.office.com/..."')
        logger.warning("")
        logger.warning("5. Restart this service")
        logger.warning("")
    else:
        logger.info("✓ Teams webhook URL configured")
        logger.info(f"  Webhook: {TEAMS_WEBHOOK_URL[:50]}...")
    
    logger.info("")
    logger.info("Endpoints:")
    logger.info("  POST /api/notify/article-submitted")
    logger.info("  POST /api/notify/article-approved")
    logger.info("  POST /api/notify/article-rejected")
    logger.info("  POST /api/notify/queue-update")
    logger.info("  GET  /api/health")
    logger.info("")
    
    app.run(host="0.0.0.0", port=port, debug=False)
