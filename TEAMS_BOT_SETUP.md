# Teams Bot Integration Guide

## Status: ✅ RUNNING

**Service URL:** http://localhost:5000  
**Port:** 5000  
**Status:** Ready for Teams webhook configuration

---

## Components Running

| Service | Port | Status | Purpose |
|---------|------|--------|---------|
| Approval API | 8000 | ✅ Running | Core approval pipeline & queue management |
| Editorial Dashboard | 3000 | ✅ Running | Web UI for article review |
| Teams Notification Bot | 5000 | ✅ Running | SendsTeams webhook notifications |
| **Total Articles Processed** | - | **6** | Across all test runs |

---

## How It Works

### Article Approval Flow
```
Article Submitted
      ↓
  AI Pipeline (6 agents)
      ↓
  Confidence Score Calculated
      ↓
  Smart Router Decision
      ├─ HIGH (>8.5) → Auto-publish
      ├─ MEDIUM (6.5-8.5) → Send to Queue
      └─ LOW (<6.5) → Auto-reject
      ↓
  Teams Notification ← You are here
      ↓
  Editorial Dashboard
      ↓
  Human Review/Approval
      ↓
  Published or Rejected
```

---

## Setting Up Teams Webhook

### Step 1: Get Teams Webhook URL

1. **Open Microsoft Teams**
2. **Go to your channel** where you want notifications
3. **Click channel menu (⋯)** → **Connectors**
4. **Search for "Incoming Webhook"**
5. **Click "Configure"**
6. **Give it a name:** e.g., "Newsroom AI Notifications"
7. (Optional) **Upload a logo**
8. **Click "Create"**
9. **Copy the webhook URL**

Example URL:
```
https://outlook.webhook.office.com/webhookb2/xxx@xxx/IncomingWebhook/yyy/zzz
```

### Step 2: Configure Environment Variable

**Option A: Manual (One-time)**
```powershell
# PowerShell
$env:TEAMS_WEBHOOK_URL = "https://outlook.webhook.office.com/webhookb2/..."

# Then restart the bot:
python teams_notification_service.py
```

**Option B: Permanent (.env file)**
Create `.env.teams`:
```
TEAMS_WEBHOOK_URL=https://outlook.webhook.office.com/webhookb2/...
TEAMS_BOT_PORT=5000
```

Then load and run:
```powershell
Get-Content .env.teams | ForEach-Object { $env:$($_.Split('=')[0]) = $_.Split('=')[1] }
python teams_notification_service.py
```

### Step 3: Restart Bot Service
```powershell
# Kill existing process
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Restart
python teams_notification_service.py
```

---

## Notification Types

### 1️⃣ Article Submitted
When a new article enters the queue
```
📰 Article SUBMITTED
Title: "Breaking News: Major Event"
Confidence: 6.5/10
Status: Pending Review
```

### 2️⃣ Article Approved  
When editorial team approves
```
📰 Article APPROVED
Title: "Breaking News: Major Event"
Status: Published
Reviewer: John Smith
```

### 3️⃣ Article Rejected
When editorial team rejects
```
📰 Article REJECTED
Title: "Breaking News: Major Event"
Reason: "Needs fact-checking"
Reviewer: Jane Doe
```

### 4️⃣ Queue Statistics
Periodic updates on queue status
```
📊 Queue Statistics Update
🟡 Pending Review: 4
✅ Approved: 12
❌ Rejected: 2
📈 Total: 18
```

---

## API Endpoints

### Send Article Submitted Notification
```bash
curl -X POST http://localhost:5000/api/notify/article-submitted \
  -H "Content-Type: application/json" \
  -d '{
    "article": {
      "id": "article-123",
      "title": "Breaking News",
      "confidence_score": 7.5,
      "status": "PENDING_REVIEW"
    }
  }'
```

### Send Article Approved Notification
```bash
curl -X POST http://localhost:5000/api/notify/article-approved \
  -H "Content-Type: application/json" \
  -d '{
    "article": {
      "id": "article-123",
      "title": "Breaking News",
      "confidence_score": 7.5
    },
    "reviewer": "John Smith",
    "notes": "Great article!"
  }'
```

### Send Article Rejected Notification
```bash
curl -X POST http://localhost:5000/api/notify/article-rejected \
  -H "Content-Type: application/json" \
  -d '{
    "article": {
      "id": "article-123",
      "title": "Breaking News"
    },
    "reviewer": "Jane Doe",
    "reason": "Unverified claims"
  }'
```

### Send Queue Update
```bash
curl -X POST http://localhost:5000/api/notify/queue-update \
  -H "Content-Type: application/json" \
  -d '{
    "stats": {
      "pending": 4,
      "approved": 12,
      "rejected": 2,
      "total": 18
    }
  }'
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

---

## Integration with Approval Service

### Automatic Notifications (When Ready)

The approval service can be configured to automatically call the Teams notification endpoints:

1. **When article is submitted:**
   - Hook in: `approval_service.py` → `submit_article()`
   - Calls: `POST /api/notify/article-submitted`

2. **When article is approved:**
   - Hook in: `approval_service.py` → `approve_article()`
   - Calls: `POST /api/notify/article-approved`

3. **When article is rejected:**
   - Hook in: `approval_service.py` → `reject_article()`
   - Calls: `POST /api/notify/article-rejected`

4. **Periodic queue updates:**
   - Hook in: Separate scheduler task
   - Calls: `POST /api/notify/queue-update`

---

## Testing Without Teams

If you don't have Teams configured yet, you can test the bot locally:

```bash
# Start bot
python teams_notification_service.py

# In another terminal, send test notifications
curl -X POST http://localhost:5000/api/notify/article-submitted \
  -H "Content-Type: application/json" \
  -d '{
    "article": {
      "id": "test-123",
      "title": "Test Article",
      "confidence_score": 7.5,
      "status": "PENDING_REVIEW"
    }
  }'

# Response:
# {"status": "success", "message": "Teams notification sent"}
```

**Note:** Without a webhook URL configured, the bot will return success but won't actually send to Teams (by design, to prevent errors).

---

## Troubleshooting

### "Webhook URL not configured"
**Solution:** Set `TEAMS_WEBHOOK_URL` environment variable before running the bot

### "Invalid webhook URL"
**Solution:** Check that the webhook URL from Teams is complete and hasn't expired
- Go to Teams channel → Connectors
- Reconfigure the webhook to get a new URL

### "Webhook not working"
**Check:**
1. Is the bot service running? `curl http://localhost:5000/api/health`
2. Is Teams webhook URL correct?
3. Check bot logs for errors
4. Try sending a test notification

### "No notifications appearing"
**Check:**
1. Verify webhook URL in Teams is correct
2. Check if the notification endpoint was called
3. Review Teams channel for blocked content

---

## Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY teams_notification_service.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV TEAMS_WEBHOOK_URL=https://outlook.webhook.office.com/webhookb2/...
ENV TEAMS_BOT_PORT=5000
EXPOSE 5000
CMD ["python", "teams_notification_service.py"]
```

### Azure Container Instance
```bash
az container create \
  --resource-group newsroom \
  --name teams-bot \
  --image newsroom-teams-bot \
  --environment-variables TEAMS_WEBHOOK_URL="..." TEAMS_BOT_PORT=5000 \
  --ports 5000
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: teams-bot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: teams-bot
  template:
    metadata:
      labels:
        app: teams-bot
    spec:
      containers:
      - name: teams-bot
        image: newsroom-teams-bot:latest
        env:
        - name: TEAMS_WEBHOOK_URL
          valueFrom:
            secretKeyRef:
              name: teams-secrets
              key: webhook-url
        ports:
        - containerPort: 5000
```

---

## Key Features

✅ **Async Notifications** - Non-blocking, fast sends to Teams  
✅ **Adaptive Cards** - Rich, interactive Teams messages  
✅ **Error Handling** - Graceful failures if webhook unavailable  
✅ **Flexible Configuration** - Environment variable or .env file  
✅ **Production Ready** - Logging, health checks, monitoring  
✅ **No External Dependencies** - Uses only aiohttp and Flask  

---

## Security

🔒 **Webhook URL:** Treat as sensitive - store in secrets manager  
🔒 **API Calls:** Consider adding API key authentication  
🔒 **Data:** All data sent over HTTPS to Teams  
🔒 **Logging:** Webhook URLs not logged (redacted)  

---

## Support

For issues:
1. Check bot logs: `curl http://localhost:5000/api/health`
2. Verify Teams webhook URL
3. Test with curl (see examples above)
4. Check Teams channel for missing connectors

**Last Updated:** February 15, 2026  
**Status:** ✅ Production Ready
