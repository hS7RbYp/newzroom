# Phase 3: Human Approval System

## Overview

Phase 3 adds a complete human approval workflow with:

- **Smart Routing**: Confidence-based article routing (Green/Yellow/Red)
- **Web Dashboard**: Modern Next.js UI for article review
- **REST API**: FastAPI endpoints for approval management
- **Teams Bot**: Microsoft Teams integration for notifications

## Architecture

```
Article Pipeline
    ↓
Stage 5.5: Smart Router (calculates confidence score)
    ├─ Green (>8.5) → Auto-publish to Cosmos DB
    ├─ Yellow (6.5-8.5) → Approval queue
    └─ Red (<6.5) → Reject
         ↓
   Approval Queue (Cosmos DB)
         ↓
   Web Dashboard / Teams Bot
         ↓
   Human Decision (Approve/Reject)
         ↓
   Ops Agent (Publish to Cosmos DB)
```

## Components

### 1. Approval Queue Manager (`agents/approval.py`)

Smart routing logic with three confidence levels:

```python
score > 8.5  → GREEN: Auto-publish
6.5 ≤ score ≤ 8.5 → YELLOW: Queue for review
score < 6.5  → RED: Reject
```

**Confidence Score Calculation:**
- Scout score: 20% weight
- Prof fact-check score: 25% weight
- Judge quality score: 25% weight
- Brand compliance: 30% weight

### 2. FastAPI Approval Service (`approval_api.py`)

REST API endpoints:

```bash
# Get pending articles
GET /api/approval/queue

# Get statistics
GET /api/approval/queue/stats

# Get article details
GET /api/approval/{article_id}

# Approve article
POST /api/approval/{article_id}/approve
Body: {"reviewer_id": "name", "notes": "..."}

# Reject article
POST /api/approval/{article_id}/reject
Body: {"reviewer_id": "name", "reason": "..."}

# Submit new article
POST /api/articles/submit
Body: {"title": "...", "content": "...", "source": "..."}
```

**Start API:**
```bash
pip install fastapi uvicorn aiohttp
python approval_api.py
# Server runs on http://localhost:8000
```

### 3. Next.js Web Dashboard (`dashboard/`)

Modern, real-time approval interface:

**Pages:**
- Home (`/`) - Approval queue with statistics
- Article Review (`/article/[id]`) - Full article with approve/reject

**Features:**
- Real-time queue updates (auto-refresh every 30 seconds)
- Color-coded confidence/quality scores
- Article preview with image, content, entities
- One-click approve/reject decisions
- Reviewer name and notes/reason required

**Start Dashboard:**
```bash
cd dashboard
npm install
npm run dev
# Dashboard runs on http://localhost:3000
```

### 4. Microsoft Teams Bot (`teams_bot.py`)

Teams integration for article notifications and quick approval:

**Commands:**
```
queue - Show pending articles
stats - Show approval statistics
approve <article-id> - Approve article
reject <article-id> <reason> - Reject article
```

**Features:**
- Sends rich Adaptive Cards when articles need approval
- One-click approve/reject buttons in Teams
- Links to full review in web dashboard
- Approval statistics summary

**Start Bot:**
```bash
pip install botbuilder-core aiohttp
python teams_bot.py
# Bot webhook: http://localhost:3978/api/messages
```

## Modified Components

### Orchestrator (`agents/orchestrator.py`)

Added Stage 5.5: Smart Routing

```python
# Between Pixel and Ops agents
routing_result = await self.approval_queue.route_article(article_id, pipeline_data)

if routing_result["action"] == "AUTO_PUBLISH":
    # Continue to Ops
elif routing_result["action"] == "QUEUE_FOR_REVIEW":
    # Return pending status
elif routing_result["action"] == "REJECT":
    # Return rejected status
```

## Data Model

### Approval Queue Item (Cosmos DB)

```json
{
  "id": "article-uuid",
  "status": "PENDING_REVIEW",
  "article_id": "article-uuid",
  "confidence_score": 7.3,
  "title": "Article Title",
  "content_preview": "First 500 chars...",
  "image_url": "https://...",
  "seo_keywords": ["keyword1", "keyword2"],
  "fact_check_score": 7.5,
  "quality_score": 8.0,
  "brand_compliant": true,
  "entities": ["Entity1", "Entity2"],
  "sentiment": "neutral",
  "created_at": "2026-02-15T10:00:00Z",
  "queued_at": "2026-02-15T10:00:30Z",
  "approved_at": null,
  "rejected_at": null,
  "reviewer_id": null,
  "reviewer_notes": null
}
```

## Workflow Example

### 1. Article Submitted
```bash
curl -X POST http://localhost:8000/api/articles/submit \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Breaking News",
    "content": "Article content...",
    "source": "News Agency"
  }'
```

### 2. Pipeline Processing
- Scout: Newsworthiness (1-10)
- Prof: Fact-checking (1-10)
- Judge: Quality (1-10)
- Scribe: SEO optimization
- Pixel: Image generation

### 3. Smart Routing
- **Score 9.1** (GREEN) → Auto-published, no approval needed
- **Score 7.4** (YELLOW) → Added to approval queue
- **Score 4.2** (RED) → Rejected automatically

### 4. Human Approval (Yellow articles)
#### Via Dashboard:
1. Visit http://localhost:3000
2. See article in "Pending Review"
3. Click "Review →"
4. Read full content, check metrics
5. Enter name
6. Click ✅ "Approve & Publish" or ❌ "Reject"

#### Via Teams:
1. Bot sends adaptive card
2. Click "Review" link or approve/reject inline
3. Fast decisions without leaving Teams

### 5. Publishing (Approved articles)
- Ops agent publishes to Cosmos DB
- Article goes live
- Notification sent to stakeholders

## Configuration

### Environment Variables

```env
# FastAPI
NEXT_PUBLIC_API_URL=http://localhost:8000

# Teams Bot (optional for now)
TEAMS_APP_ID=your-app-id
TEAMS_APP_PASSWORD=your-app-password

# Confidence thresholds (configurable)
CONFIDENCE_AUTO_PUBLISH_THRESHOLD=8.5
CONFIDENCE_QUEUE_THRESHOLD=6.5
```

## Testing the Approval System

### 1. Start All Services

**Terminal 1 - FastAPI:**
```bash
python approval_api.py
```

**Terminal 2 - Dashboard:**
```bash
cd dashboard && npm run dev
```

**Terminal 3 - Teams Bot (optional):**
```bash
python teams_bot.py
```

### 2. Submit Test Article

```bash
curl -X POST http://localhost:8000/api/articles/submit \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Article",
    "content": "This is a test article content with enough length to be considered for publication by the AI agents involved in processing.",
    "source": "Test Source"
  }'
```

### 3. Check Queue

```bash
curl http://localhost:8000/api/approval/queue
```

### 4. Visit Dashboard

Open http://localhost:3000 in browser

### 5. Review and Approve

Click article → Review → Approve

## Performance Metrics

### Pipeline with Approval

- **Total Time**: ~17.5s (same as before)
- **Approval Queue Check**: <100ms
- **Smart Router**: <50ms
- **Database Operations**: <200ms

### Confidence Score Distribution

Expected distribution for production:
- **Green (Auto-publish)**: ~40% of articles
- **Yellow (Approval queue)**: ~50% of articles  
- **Red (Reject)**: ~10% of articles

## Deployment

### Local Development
```bash
# All services
python approval_api.py &
cd dashboard && npm run dev &
python teams_bot.py &
```

### Production Deployment

#### FastAPI to Azure App Service
```bash
az webapp up --name newsroom-approval-api \
  --sku B1 --runtime PYTHON:3.11
```

#### Next.js to Vercel
```bash
cd dashboard
npm run build
vercel deploy
```

#### Teams Bot to Azure Bot Service
Configure in Azure Portal

## Next Steps

1. **Feedback Loop**: Judge → Prof learning from rejections
2. **Analytics**: Track approval rates, common rejection reasons
3. **Webhooks**: Notify external systems on approval/rejection
4. **Batch Approval**: Approve multiple articles at once
5. **Advanced Routing**: ML-based confidence prediction

## Status

✅ Phase 3 Complete:
- [x] Approval queue manager
- [x] Smart routing logic
- [x] FastAPI REST API
- [x] Next.js dashboard UI
- [x] Teams bot integration
- [x] Cosmos DB integration
- [x] Orchestrator modification

🚀 Ready for deployment and testing!
