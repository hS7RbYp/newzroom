"""
Microsoft Teams Bot for Article Approval

Integrates with Teams to:
- Send approval notifications
- Allow one-click approve/reject in Teams
- Display article summaries with approve/reject buttons
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any
from aiohttp import web
from aiohttp import ClientSession
import sys

# Add agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from botbuilder.core import (
    BotFrameworkAdapter,
    ConversationState,
    MemoryStorage,
    MessageFactory,
    CardFactory
)
from botbuilder.schema import Activity, ActivityTypes, Attachment
from botbuilder.dialogs import Dialog, DialogSet, DialogState
from approval import get_approval_queue
from config import get_config


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("teams_bot")


class ArticleApprovalBot:
    """Teams bot for article approval workflow"""
    
    def __init__(self):
        config = get_config()
        self.approval_queue = get_approval_queue()
        
        # Bot settings (from environment or defaults)
        import os
        self.app_id = os.getenv("TEAMS_APP_ID", "")
        self.app_password = os.getenv("TEAMS_APP_PASSWORD", "")
        
        # Adapter
        self.adapter = BotFrameworkAdapter(self.app_id, self.app_password)
        
        # Conversation state
        memory = MemoryStorage()
        self.conversation_state = ConversationState(memory)
        self.user_state = ConversationState(memory)
        
        logger.info("Teams bot initialized")
    
    async def on_message_activity(self, activity: Activity) -> None:
        """Handle incoming messages"""
        text = activity.text.strip() if activity.text else ""
        
        if text.lower() == "queue":
            await self._send_queue_summary(activity)
        elif text.lower() == "stats":
            await self._send_stats(activity)
        elif text.lower().startswith("approve"):
            await self._handle_approval(activity)
        elif text.lower().startswith("reject"):
            await self._handle_rejection(activity)
        else:
            await self._send_help(activity)
    
    async def _send_queue_summary(self, activity: Activity) -> None:
        """Send approval queue summary as Teams card"""
        try:
            queue = await self.approval_queue.get_queue()
            
            if not queue:
                reply = MessageFactory.text("✅ All caught up! No pending articles.")
                await self.adapter.send_activities(activity, [reply])
                return
            
            # Create card for each pending article
            for article in queue[:5]:  # Show first 5
                card = self._create_article_card(article)
                reply = MessageFactory.attachment(card)
                await self.adapter.send_activities(activity, [reply])
        
        except Exception as e:
            logger.error(f"Failed to send queue: {str(e)}")
    
    async def _send_stats(self, activity: Activity) -> None:
        """Send approval statistics"""
        try:
            stats = await self.approval_queue.get_approval_stats()
            
            summary = f"""
            📊 **Approval Queue Statistics**
            
            • **Pending Review**: {stats.get('pending', 0)} articles
            • **Approved**: {stats.get('approved', 0)} articles
            • **Rejected**: {stats.get('rejected', 0)} articles
            • **Total**: {stats.get('total', 0)} articles
            """
            
            reply = MessageFactory.text(summary)
            await self.adapter.send_activities(activity, [reply])
        
        except Exception as e:
            logger.error(f"Failed to send stats: {str(e)}")
    
    async def _handle_approval(self, activity: Activity) -> None:
        """Handle approval via Teams command"""
        # Extract article ID from message (format: "approve article-id")
        parts = activity.text.split()
        if len(parts) < 2:
            reply = MessageFactory.text("Usage: `approve <article-id>`")
            await self.adapter.send_activities(activity, [reply])
            return
        
        article_id = parts[1]
        reviewer_id = activity.from_property.name or "Teams User"
        
        try:
            result = await self.approval_queue.approve_article(
                article_id=article_id,
                reviewer_id=reviewer_id,
                reviewer_notes=f"Approved via Teams by {reviewer_id}"
            )
            
            reply = MessageFactory.text(f"✅ Article approved: {article_id}")
            await self.adapter.send_activities(activity, [reply])
        
        except Exception as e:
            logger.error(f"Failed to approve: {str(e)}")
            reply = MessageFactory.text(f"❌ Error: {str(e)}")
            await self.adapter.send_activities(activity, [reply])
    
    async def _handle_rejection(self, activity: Activity) -> None:
        """Handle rejection via Teams command"""
        # Format: "reject article-id reason..."
        parts = activity.text.split(maxsplit=2)
        if len(parts) < 3:
            reply = MessageFactory.text("Usage: `reject <article-id> <reason>`")
            await self.adapter.send_activities(activity, [reply])
            return
        
        article_id = parts[1]
        reason = parts[2]
        reviewer_id = activity.from_property.name or "Teams User"
        
        try:
            result = await self.approval_queue.reject_article(
                article_id=article_id,
                article_data={"article_id": article_id},
                reason=reason,
                reviewer_id=reviewer_id
            )
            
            reply = MessageFactory.text(f"❌ Article rejected: {article_id}\nReason: {reason}")
            await self.adapter.send_activities(activity, [reply])
        
        except Exception as e:
            logger.error(f"Failed to reject: {str(e)}")
            reply = MessageFactory.text(f"❌ Error: {str(e)}")
            await self.adapter.send_activities(activity, [reply])
    
    async def _send_help(self, activity: Activity) -> None:
        """Send help message"""
        help_text = """
        🤖 **Newsroom AI Approval Bot**
        
        Available commands:
        • `queue` - Show pending articles for review
        • `stats` - Show approval statistics
        • `approve <article-id>` - Approve an article
        • `reject <article-id> <reason>` - Reject an article
        
        Or visit the **[Web Dashboard](http://localhost:3000)** for detailed review interface.
        """
        
        reply = MessageFactory.text(help_text)
        await self.adapter.send_activities(activity, [reply])
    
    def _create_article_card(self, article: Dict[str, Any]) -> Attachment:
        """Create adaptive card for article"""
        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": article.get("title", "Untitled"),
                    "weight": "bolder",
                    "size": "large"
                },
                {
                    "type": "TextBlock",
                    "text": article.get("content_preview", "")[:200],
                    "wrap": True,
                    "spacing": "medium"
                },
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "width": "auto",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"📊 Confidence: {article.get('confidence_score', 0):.1f}/10"
                                }
                            ]
                        },
                        {
                            "width": "auto",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"✓ Quality: {article.get('quality_score', 0):.1f}/10"
                                }
                            ]
                        }
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "👁️ Review",
                    "url": f"http://localhost:3000/article/{article.get('article_id')}"
                },
                {
                    "type": "Action.Submit",
                    "title": "✅ Approve",
                    "data": {
                        "action": "approve",
                        "article_id": article.get("article_id")
                    }
                },
                {
                    "type": "Action.Submit",
                    "title": "❌ Reject",
                    "data": {
                        "action": "reject",
                        "article_id": article.get("article_id")
                    }
                }
            ]
        }
        
        return CardFactory.adaptive_card(card)


# Create bot instance
bot = ArticleApprovalBot()


# ============================================================================
# Web Routes
# ============================================================================

async def messages(req: web.Request) -> web.Response:
    """Handle incoming messages"""
    try:
        body = await req.json()
        activity = Activity().deserialize(body)
        
        # Process activity
        if activity.type == ActivityTypes.message:
            await bot.on_message_activity(activity)
        
        return web.Response(status=200)
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return web.Response(status=500, text=str(e))


async def health(req: web.Request) -> web.Response:
    """Health check"""
    return web.json_response({
        "status": "healthy",
        "service": "teams-bot",
        "version": "1.0.0"
    })


async def start_server():
    """Start Teams bot web server"""
    app = web.Application()
    app.router.add_post('/api/messages', messages)
    app.router.add_get('/api/health', health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 3978)
    await site.start()
    
    logger.info("Teams bot server started on http://localhost:3978")
    logger.info("Webhook URL: http://localhost:3978/api/messages")
    
    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(start_server())
