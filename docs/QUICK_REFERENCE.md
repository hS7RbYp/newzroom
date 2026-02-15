# Azure Autonomous Newsroom (AAN) — Quick Reference Guide

**Document Version:** 1.0  
**Date:** February 14, 2026  
**Purpose:** Executive summary + quick reference for all documentation

---

## 📋 Document Map

| Document | Purpose | Audience | Length |
|----------|---------|----------|--------|
| [SYSTEM_DESIGN_v3.0.md](./SYSTEM_DESIGN_v3.0.md) | Complete architectural specification | Architects, Tech Leads | 35 pages |
| [AGENT_MESH_COMMUNICATION.md](./AGENT_MESH_COMMUNICATION.md) | Agent interactions + message flows | Backend Engineers | 25 pages |
| [MEMORY_ARCHITECTURE.md](./MEMORY_ARCHITECTURE.md) | 3-tier memory system (Immediate/Working/Long-term) | Data Engineers, Architects | 20 pages |
| [OBSERVABILITY_MONITORING.md](./OBSERVABILITY_MONITORING.md) | Dashboards, alerts, metrics, runbooks | DevOps, Data Engineers | 30 pages |
| [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) | Phase-by-phase execution plan (8 weeks) | Project Manager, All Engineers | 40 pages |
| **QUICK_REFERENCE.md** (this file) | Summary + cheat sheets | Everyone | 5 pages |

---

## 🚀 System at a Glance

### Architecture

```
┌─ Azure Foundry Agent Service (Orchestrator) ─┐
│  Manages 6 Connected Agents + Message Routing │
└┬─────────────────────────────────────────────┘
 │
 ├─ Scout (GPT-4o-mini)      → Watches RSS/social for trends
 ├─ Prof (GPT-4o)            → Researches + cross-validates
 ├─ Scribe (GPT-4o)          → Drafts content (with iterations)
 ├─ Judge (GPT-4o-mini)      → Brand compliance checks
 ├─ Pixel (DALL-E 3 + PIL)   → Generates branded images
 └─ Ops (API-driven)         → GitOps publishing
```

### Value Proposition

| Aspect | Traditional Writer | Gen 1.5 Co-pilot | Gen 2 (AAN) | Gen 3 (This System) |
|--------|-------------------|------------------|-------------|-------------------|
| **Speed** | 2-4 hours | 30 min | 1-2 hours | **30-45 min** |
| **Quality** | Manual | Varies | Enforced by Judge | **Self-Improving** |
| **Throughput** | 3 stories/day | 1-2/day | 2-3/day | **5-7/day** ✨ |
| **Cost** | $500 salary | $100 API | $300/mo | **$300/mo** |
| **Learning** | Manual | No | Manual rules | **Auto-Updates** ✨ |

---

## 🏗️ 3-Tier Memory

### Immediate (Agent Thread)
- **Duration:** 1-2 hours (during pitch lifecycle)
- **Storage:** Foundry Agent Service (managed)
- **Query:** Full audit trail of one pitch
- **Example:** "Show me all messages for story_001"

### Working (Cosmos DB)
- **Duration:** 30 days (then auto-delete)
- **Storage:** ~500 GB (15 GB/month)
- **Query:** "Show all pitches approved this week by Editor X"
- **Example:** "What topics did Judge reject most this month?"

### Long-Term (AI Search — Vector)
- **Duration:** Permanent
- **Storage:** ~500 MB (brand rules + patterns)
- **Query:** "Find similar content that violated this rule"
- **Example:** "Judge finds all absolute claims ever flagged"

---

## 📊 Key Metrics & Targets

### Daily Operations
| Metric | Target | Current | Frequency |
|--------|--------|---------|-----------|
| Pitches/day | 15-20 | — | Real-time |
| Approval rate | >40% | — | Hourly |
| Judge rejection | <10% | — | Hourly |
| Time-to-publish | <2 hours | — | Per story |
| Cost/article | <$10 | — | Daily |

### Quality
| Metric | Target |
|--------|--------|
| Factual accuracy (audited) | >98% |
| Brand tone consistency | >90% |
| Image quality score | >8.5/10 |
| Zero data loss | 100% |

### System Health
| Metric | Target |
|--------|--------|
| Uptime | 99.9% |
| Error rate | <1% |
| P95 latency (end-to-end) | <3 hours |
| API availability | >99% |

---

## 💰 Cost Breakdown

**Monthly Infrastructure:**
```
Azure OpenAI (GPT-4o, GPT-4o-mini)    $300
DALL-E 3 (images)                     $150
Cosmos DB (serverless)                $250
Azure AI Search (vector)              $150
Static Web Apps + Storage             $120
Service Bus + Logic Apps              $100
Application Insights                  $50
Network (VNet + private endpoints)    $50
Miscellaneous                         $30
─────────────────────────────────────
TOTAL                                 $1,200/month
```

**Per Article:**
- GPT tokens: ~$0.25
- DALL-E image: ~$0.10
- Infra (amortized): ~$0.05
- **Total: ~$0.40 per article**
  
With ~500 articles/month: $200 + $60 infra = $260/month

---

## 🔄 Core Workflows

### Workflow A: Story Detection (Scout)

```
EVERY 15 MINUTES:
1. Ingest 500+ headlines (Bing News + Social)
2. Filter by keywords (AI, Tech, Finance, Local)
3. Score 0-10 (keyword + source + recency + uniqueness)
4. Top-5 → Send to Teams card
5. Editor: [✅ Approve] [🔄 Research More] [❌ Skip]

RESULT: 15-20 pitches per day
```

### Workflow B: Content Production (Editor Approves)

```
UPON ✅ APPROVAL:
1. Prof researches (AI Search + Bing)
   - If insufficient → rescan request to Scout
2. Scribe drafts (GPT-4o)
3. Judge validates (vector rules + Content Safety)
   - If fail → feedback to Scribe (max 3 iterations)
   - If final fail → DLQ (manual review)
4. Pixel images (DALL-E 3 + branding)
5. Ops publishes (GitHub drafts branch)
   - Preview URL sent to Teams
   - Editor: [✅ Publish] [📝 Edit] [❌ Reject]
6. Merge to main → Live site + auto-post social

RESULT: Story live in <2 hours
```

---

## 🔧 Agent Specifications

### Scout (Watchdog)
```
Model: GPT-4o-mini
Trigger: Every 15 minutes (timer)
Latency: ~2 min
Cost: ~$0.02
Success: >90% relevance accuracy
Timeout: 45s (fallback to cache if timeout)
```

### Prof (Researcher)
```
Model: GPT-4o
Trigger: Editor approves pitch
Latency: ~2 min
Cost: ~$0.10
Success: >90% corroboration
Timeout: 120s (proceed with lower confidence)
Feedback: Can request Scout rescan
```

### Scribe (Writer)
```
Model: GPT-4o
Trigger: Prof completes research
Latency: ~1.5-2 min per draft
Cost: ~$0.15 per draft
Success: Draft generated (Judge validates)
Iterations: Max 3 attempts; then escalate
Timeout: 60s per draft
```

### Judge (Critic)
```
Model: GPT-4o-mini
Trigger: Scribe submits draft
Latency: ~20-30s
Cost: ~$0.02
Rules: Vector search in AI Search
Feedback: Specific rejection reasons
Timeout: 30s (passes if timeout)
Decision: Final (no retries)
```

### Pixel (Media)
```
Model: DALL-E 3 + Claude Vision QA
Trigger: Judge approves (parallel to Ops)
Latency: ~60s
Cost: ~$0.10 per image
Output: Branded 1200x630 JPEG
Retry: 2x if fails
Timeout: 120s (publish without image)
```

### Ops (Publisher)
```
Trigger: Judge approves
Latency: ~30s (commit) + 120s (build)
Cost: ~$0.01
Steps: Commit → Build preview → Merge → Deploy
Retry: 3x exponential backoff
DLQ: Failed publishes manually reviewed
```

---

## ⚠️ Failure Handling

### Circuit Breaker Pattern

```
API Call Fails:
  Attempt 1 → CLOSED (normal)
  Attempt 2 → CLOSED
  Attempt 3 → OPEN (stop calling)
  
  Fallback: Use cached data or proceed with warning
  
  Retry: Every 5 minutes test connection
  Recovery: After 3 consecutive successes → HALF_OPEN → CLOSED
```

### Retry Policies

| Agent | Max Retries | Strategy |
|-------|------------|----------|
| Scout | 3 | Exponential backoff; fallback to cache |
| Prof | 2 | Linear backoff; proceed if timeout |
| Scribe | 0 | Explicit iteration (max 3); then escalate |
| Judge | 0 | Timeout = pass (don't block) |
| Pixel | 2 | Linear backoff; publish without image |
| Ops | 3 | Exponential backoff; then DLQ |

### Escalation to DLQ

**When:**
- Scribe fails Judge 3x (need human edit)
- Ops publish fails 3x (GitHub unavailable)
- Prof confidence too low (editor decides)

**Processing:**
- Daily digest email (9 AM UTC)
- Editor manually reviews
- Can re-queue or discard

---

## 📈 Scaling Principles

### Horizontal Scaling
- **Foundry Hosted Agents:** Auto-scale by default
- **Cosmos DB:** Serverless autoscale (up to 40K RU/s)
- **Static Web Apps:** CDN handles spike traffic

### Cost Optimization
- GPT-4o-mini for "cheaper" tasks (Scout, Judge)
- GPT-4o for high-stakes (Scribe, Prof)
- Image caching (30-day retention)
- Smart batching (Prof searches in bulk)

### Performance Optimization
- Scout caches 24h headline history
- Prof caches research results (7 days)
- Judge uses vector search (fast semantic matching)
- Pixel parallelize with Ops (don't wait for image before publish)

---

## 🚨 Common Issues & Solutions

### Scout Generating Few Pitches
```
🔍 Diagnosis:
  1. Check Bing API quota (might throttled)
  2. Check interest profile (keywords too narrow?)
  3. Check relevance threshold (too high?)

✅ Solution:
  - Increase throttle window (wider filter)
  - OR lower relevance threshold temporarily
  - OR add more keywords to interest profile
```

### Judge Rejection Rate Spiking
```
🔍 Diagnosis:
  1. Did brand rulebook change?
  2. Did Scribe quality degrade?
  3. New content type Scribe unfamiliar with?

✅ Solution:
  - Review recent Judge rejections in Power BI
  - Check if rulebook needs refinement
  - Retrain Scribe with examples
```

### High Cost Per Article
```
🔍 Diagnosis:
  1. Is Scribe using GPT-4o for iterations? (expensive)
  2. Are DALL-E retry loops?
  3. Prof doing expensive searches?

✅ Solution:
  - Switch Scribe iterations to GPT-4o-mini
  - Check Bing API call volume
  - Enable image caching
```

### DLQ Backlog Growing
```
🔍 Diagnosis:
  1. Is Judge too strict? (rejecting everything)
  2. Is Ops GitHub API failing?
  3. Network issues?

✅ Solution:
  - Review Judge rulebook (may be too strict)
  - Check GitHub status
  - Contact Azure support if network issues
```

---

## 📞 Incident Response

### Critical Incident (Scout Down)
```
Impact: No new pitches; Editor can't approve stories
SLA: 15 minutes
Response:
  1. Check Bing News API status
  2. If API down → Use cached headlines manually
  3. Restart Scout agent (auto-retry every 2 min)
  4. Monitor for recovery
  5. Post-incident review within 24h
Cost of outage: ~$50/hour (missed stories)
```

### Warning Incident (Judge Rejection Spike)
```
Impact: Stories taking longer to publish; risk of escalation
SLA: 1 hour
Response:
  1. Check last 10 rejections in Power BI
  2. Identify pattern (e.g., "absolute claims")
  3. If human error → Scribe retraining
  4. If rulebook issue → Update rules
  5. Monitor approval rate
Cost of issue: ~$10/delayed article
```

### Escalation Path
```
Editor → On-Call DevOps → Cloud Architect → VP Engineering
┬        ┬                ┬                 ┬
15 min   30 min          1 hour            4 hours
(if not resolved)
```

---

## 🎓 Team Roles & Responsibilities

| Role | Responsibility | Daily Tasks |
|------|-----------------|-----------|
| **Editor** | Approve/reject pitches; provide feedback | Check Teams every 2h; approve 3-5 stories |
| **On-Call DevOps** | System health; incident response | Daily dashboard review; alert monitoring |
| **Data Engineer** | Metrics, dashboards, analysis | Update Power BI; investigate anomalies |
| **Cloud Architect** | Infrastructure, security, scaling | Weekly capacity review; cost optimization |

---

## 📋 Checklists

### Daily Operations Checklist
- [ ] Morning: Check Power BI (no critical alerts?)
- [ ] 10 AM: Scout running? (15+ pitches generated)
- [ ] Noon: Any stuck stories in DLQ?
- [ ] 3 PM: Review cost-per-article (still <$10?)
- [ ] 5 PM: Check judge rejection rate trend
- [ ] Evening: Any on-call escalations?

### Weekly Review
- [ ] Monday: Analyze Judge rejection patterns
- [ ] Wednesday: Review author performance (Prof, Scribe)
- [ ] Friday: Cost analysis + optimization opportunities
- [ ] Friday: Team standup (any blockers?)

### Monthly Deep Dive
- [ ] Generate PIR for any incidents
- [ ] Review & update brand rulebook
- [ ] Analyze top-performing topics
- [ ] Capacity planning (within limits?)
- [ ] Team retro (what to improve?)

---

## 🔐 Security Checklist

- [ ] All API keys in Key Vault (not in code)
- [ ] Managed Identities used (not connection strings)
- [ ] RBAC roles follow least privilege
- [ ] VNet + Private endpoints enabled
- [ ] Audit logging on all services
- [ ] Data encryption in transit (TLS 1.3)
- [ ] Data encryption at rest (managed keys)

---

## 💡 Tips & Tricks

### Performance
- Reduce Judge timeout during high load (pass unvalidated stories faster)
- Batch Prof searches (combine keywords into single query)
- Cache scout headlines longer during API issues
- Pre-generate images during off-peak hours

### Cost
- Use GPT-4o-mini for all iteration/refinement tasks
- Enable image caching (avoid DALL-E re-generation)
- Batch vector embeddings (weekly, not per-query)
- Use Azure Reservations for 1-year commitment (-30%)

### Quality
- Review Judge rejection reasons weekly (update rules)
- Monitor Scribe output (quality degradation signals)
- Verify Prof research (spot-check facts)
- A/B test different tones with editors

---

## 🎯 Success Metrics (Monthly)

| KPI | Formula | Target |
|-----|---------|--------|
| Productivity | Articles published / day | >5 |
| Quality | Factual accuracy % | >98% |
| Efficiency | Average time to publish | <2 hours |
| Cost Efficiency | Cost per article | <$10 |
| System Health | Uptime % | >99.9% |
| Learning | Judge auto-rule updates | >2/week |

---

## 📚 Additional Resources

- **Foundry Docs:** https://aka.ms/foundry-docs
- **Azure OpenAI:** https://aka.ms/aoai
- **Semantic Kernel:** https://github.com/microsoft/semantic-kernel
- **Vector Search:** https://aka.ms/azai-search-vector
- **AAN Discord:** #azure-newsroom

---

## 🚀 Quick Start Commands

```bash
# Check Scout status
curl https://foundry-api/agents/scout/status

# View latest pitches (past 24h)
az cosmosdb query --query "SELECT * FROM pitches WHERE created_at > NOW() - 86400"

# Trigger manual rescan
curl -X POST https://foundry-api/agents/scout/rescan \
  -d '{"keywords": "AI"}'

# View Judge rejections (today)
az monitor log-analytics query --query "judge_feedback | where timestamp > ago(24h)"

# Check system cost (YTD)
az billing invoice --start-date "2026-01-01" --aggregation monthly
```

---

**Last Updated:** February 14, 2026  
**Version:** 1.0  
**Maintained By:** Cloud Architecture Team (Azure)

---

### Document Navigation
- [← Back to Main Docs](#document-map)
- [System Design (v3.0)](./SYSTEM_DESIGN_v3.0.md)
- [Agent Mesh](./AGENT_MESH_COMMUNICATION.md)
- [Memory Architecture](./MEMORY_ARCHITECTURE.md)
- [Observability](./OBSERVABILITY_MONITORING.md)
- [Implementation](./IMPLEMENTATION_ROADMAP.md)
