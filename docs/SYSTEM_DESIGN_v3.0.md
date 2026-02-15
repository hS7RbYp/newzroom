# System Design Document: Azure Autonomous Newsroom (AAN)
**Date:** February 14, 2026  
**Version:** 3.0 (Revised with Production Architecture)  
**Architecture Model:** Gen 2 Agentic Workflow (Autonomous) with Connected Agents  
**Cloud Provider:** Microsoft Azure  
**Orchestration Framework:** Foundry Agent Service (Connected Agents)

---

## 1. Executive Summary

The Azure Autonomous Newsroom (AAN) is a production-grade multi-agent AI ecosystem designed to function as a virtual content team. This **v3.0 revision** incorporates architectural best practices for enterprise agentic systems, including:

- **Connected Agent Mesh** with feedback loops and conditional routing
- **Hierarchical Memory Architecture** (immediate/working/long-term)
- **Tiered Model Strategy** for cost optimization (~40% savings)
- **Resilience Patterns** (circuit breakers, dead-letter queues, graceful degradation)
- **Vector-Embedded Knowledge Base** for semantic brand enforcement
- **Production-Grade Observability** with Foundry native tracing

The system moves beyond linear pipelines to a **self-correcting agent ecosystem** where agents collaborate, learn from feedback, and escalate intelligently when needed.

---

## 2. High-Level Architecture

### 2.1 Core Workflow: Agent Mesh

The system follows a **newsroom metaphor** where specialized agents collaborate in a **mesh topology** (not linear) under a central **Foundry Orchestrator**.

```
┌─────────────────────────────────────────────────────────┐
│           FOUNDRY AGENT SERVICE (Orchestrator)          │
│  ✓ Multi-agent coordination                             │
│  ✓ Message routing & retry logic                        │
│  ✓ Conversation threading                               │
│  ✓ Built-in tracing & observability                     │
└─────────────────────────────────────────────────────────┘

    ↓                                    ↓
┌────────────────┐              ┌──────────────────┐
│   SCOUT AGENT  │              │  MEMORY LAYER    │
│ (Continuous    │              │  ┌─ Immediate   │
│  Listening)    │◄────────────►│  ├─ Working     │
│                │              │  └─ Long-term   │
└────────────────┘              │  (Vector DB)    │
    │                           └──────────────────┘
    │ Pitch Card
    ▼
┌─────────────────────────────────────────────┐
│  EDITOR APPROVAL (Microsoft Teams)          │
│  [✅ Approve] [🔄 Needs Research] [❌ Reject]│
└─────────────────────────────────────────────┘
    │ Approved
    ▼
┌────────────────┐    ┌────────────┐    ┌──────────────┐
│  PROF AGENT    │◄──►│ SCRIBE     │◄──►│  JUDGE       │
│  (Research)    │    │ AGENT      │    │  AGENT       │
│                │    │ (Writing)  │    │ (Compliance) │
│                │    │            │    │              │
└────────────────┘    └────────────┘    └──────────────┘
                      ▲       │
                      │       │ Rejected?
                      │       ▼ (max 3 retries)
                      └ Iteration Loop
                      
          Pass ▼
┌────────────────┐    ┌──────────────┐
│  PIXEL AGENT   │    │  OPS AGENT   │
│  (Media)       │───►│  (Publishing)│
│                │    │              │
└────────────────┘    └──────────────┘
```

### 2.2 Key Flows

**Flow A: Continuous Monitoring (24/7)**
```
Scout (15-min timer) 
  → Ingest 500+ headlines/social posts
  → Filter against User Interest Profile
  → Calculate Relevance Score (0-10)
  → Send Story Pitch Card to Teams
  → Await Human Decision (✅/❌/🔄)
```

**Flow B: Execution (Upon Approval)**
```
Editor Clicks ✅
  → Prof runs deep research
    → Insufficient data → Scout rescans (feedback loop)
    → Contradicts guidelines → Flag to Editor (escalation)
  → Scribe drafts content
  → Judge performs compliance check
    → Fail → Scribe iterates (max 3)
      → Still fail → Alert Editor + escalate to DLQ
    → Pass → Ops commits to GitHub
      → GitHub Actions triggers build
      → Azure Static Web Apps publishes to preview URL
      → Editor approves in Teams
        → Merge to main
        → Live site updates

Flow C: Feedback & Learning
```
Judge Rejection Reason → Stored in Cosmos DB
  → Used to update Judge's system prompt
  → Shared with Scribe for awareness
  → Reduces future rejections (iterative improvement)
```

---

## 3. Agent Roster (The "Crew") — REVISED

Each agent is a **Foundry Connected Agent** with defined responsibilities, tiered models, and tool access.

| Agent | Role | Model | Responsibility | Tools/MCPs | Max Retries |
|-------|------|-------|-----------------|-----------|------------|
| **Scout** | Watchdog | GPT-4o-mini | 15-min timer. Ingest raw feeds, calculate Relevance Score (0-10), post to Teams | Bing News API, Social Listening API, Azure Cosmos DB (read) | 3 (fallback: cached headlines) |
| **Prof** | Researcher | GPT-4o | Deep dives on approved pitches. Retrieves internal stance (RAG) and external facts. Can request Scout rescan. | Bing Search v7, Azure AI Search (vector RAG), Cosmos DB | 2 (escalate if fails) |
| **Scribe** | Writer | GPT-4o | Drafts Markdown with Frontmatter. Adapts tone per brand rules. Receives feedback from Judge. | GPT-4o, FileSystem, Cosmos DB (read/write drafts) | 3 (then escalate) |
| **Judge** | Critic / Compliance | GPT-4o-mini | Validates drafts for forbidden words, hallucinations, brand alignment. Enforces vector-embedded rulebook. | Azure Content Safety, Azure AI Search (brand rules), Custom Rulebook | N/A (decision = final) |
| **Pixel** | Media Lead | DALL-E 3 + Vision | Generates visuals, applies brand overlays (logo, fonts). Uses Claude Vision for image QA. | DALL-E 3, Python PIL, Azure Blob, Claude Vision API | 2 |
| **Ops** | Publisher | (No LLM) | GitOps workflow. Commits files to GitHub, triggers builds. Posts to social via Logic Apps. | GitHub API, Azure Logic Apps, Static Web Apps API | 3 (DLQ on final failure) |

---

## 4. Memory Architecture (3-Tier) — NEW

### 4.1 Tier 1: Immediate (Agent Thread Memory)
- **Storage:** Foundry Agent Service conversation thread
- **TTL:** Current session (until pitch resolved or rejected)
- **Purpose:** Real-time agent state, current task context
- **Example:** "Scout finding: Tech layoffs trend detected in 47 sources"

### 4.2 Tier 2: Working (Session State)
- **Storage:** Azure Cosmos DB (partitioned by agent)
- **TTL:** 30 days rolling window
- **Purpose:** Past pitches, approval decisions, iteration history
- **Indexes:** Agent ID, timestamp, story ID
- **Example:** Previous story pitches, editor's feedback reasons, brand violation incidents

### 4.3 Tier 3: Long-Term (Semantic Knowledge Base)
- **Storage:** Azure AI Search (Vector Store)
- **TTL:** Permanent (with archival policy)
- **Embedding Model:** text-embedding-3-small (cost) or text-embedding-3-large (quality)
- **Contents:**
  - Brand voice guidelines (semantic chunks)
  - Past editorial decisions (why stories were rejected/approved)
  - Competitor analysis (never disparage XYZ)
  - Topic sensitivity rules (geopolitical, financial disclaimers)
  - Hallucination patterns from Judge (e.g., "avoid absolute claims")

#### 4.3.1 Vector Embedding Pipeline

```
Brand Rulebook Document (Markdown)
  ↓
Split into semantic chunks (overlap=20%)
  ↓
Embed with text-embedding-3-small
  ↓
Index in Azure AI Search
  ↓
Judge runs semantic search during compliance check:
  Query: "Is this tone appropriate for our audience?"
  → Retrieves top-3 relevant brand rules (cosine similarity)
  → Adds to Judge's system prompt for context
```

---

## 5. Detailed Subsystems

### 5.1 Scout Agent: Continuous Listening & Filtering

**Trigger:** Azure Function Timer (every 15 minutes)

**Logic:**
```
1. Ingest 500+ headlines/social posts
   - Bing News API
   - Twitter API (social listening)
   - Reddit (trending in relevant subreddits)

2. Filter against Editor's Interest Profile
   - Keywords (tech, finance, local news)
   - Competitor watch list
   - Excluded topics (internal politics)

3. Calculate Relevance Score (0-10)
   - Source credibility (0-3 points)
   - Keyword match strength (0-3 points)
   - Recency (0-2 points)
   - Uniqueness vs. past month (0-2 points)

4. Filter to top-5 stories per 15-min cycle
   - Send as Teams Adaptive Card with:
     * Headline
     * Summary (2 sentences)
     * Relevance Score
     * Source + URL
     * [✅ Write This] [🔄 Research More] [❌ Skip]

5. Store in Cosmos DB for audit trail
```

**Resilience:**
- Circuit breaker: If Bing API fails 3x in 5 min → use cached headlines from past 24h
- Fallback: If all APIs down → send "No stories to report" card (transparency)

### 5.2 Editor Approval Layer (Microsoft Teams)

**Enhanced Workflow:**

- **✅ Approve & Publish:** Editor confident → direct to Prof
- **🔄 Needs Research:** "Scout, find more on this topic" → Scout rescans with specific keywords
- **📝 Needs Discussion:** "Assign to Prof first, let Prof recommend angle" → Prof reads Editor's note
- **❌ Reject:** With optional feedback → stored in Cosmos DB → Judge learns

**Feedback Loop:** Editor's reject reasons aggregated weekly → used to refine Judge's system prompt

### 5.3 Prof Agent: Research & Validation

**Trigger:** Editor approves pitch

**Logic:**
```
1. Download story URL + Scout's pitch summary
2. Semantic search in Azure AI Search for:
   - Past coverage on this topic
   - Competitor mentions (brand sensitivity)
   - Internal stance/position on this issue
3. Cross-reference with Bing Search v7 for:
   - Conflicting sources
   - Update on the story since Scout's detection
   - Expert citations available
4. If insufficient corroboration:
   - Signal to Scout: "Rescan for [specific keyword] in past 6 hours"
   - Wait for Scout's second pass
5. Compile research brief (Markdown):
   - Key facts + sources
   - Counterarguments
   - Brand alignment assessment
6. Hand off to Scribe with research context
```

**Resilience:**
- If search returns contradictory info → flag to Editor before Scribe starts
- If Bing API throttled → use only AI Search (slower but safer)

### 5.4 Scribe Agent: Content Generation with Iteration

**Trigger:** Prof completes research

**Logic:**
```
1. Receive research brief + interest profile
2. Choose writing tone from library:
   - Formal (tech press release)
   - Conversational (blog post)
   - Urgent (breaking news)
   - Educational (explainer)
3. Generate Markdown draft with:
   - Frontmatter (title, date, author: "AAN", tags)
   - SEO-optimized headline
   - Lede (inverted pyramid)
   - Body (3-5 sections)
   - Callout/fact box
   - Sources appendix
4. Pass to Judge for compliance check
5. If Judge rejects:
   - Receive specific feedback (e.g., "remove absolute claims in para 3")
   - Retry (max 3 iterations)
   - If still failing after 3 retries → escalate to Editor + store in DLQ
```

### 5.5 Judge Agent: Compliance & Brand Enforcement

**Trigger:** Scribe submits draft

**Process:**
```
1. Semantic search in Azure AI Search for brand rules
   - Query: "Brand voice and tone guidelines"
   - Query: "Forbidden competitor mentions"
   - Query: "Content that caused past rejections"
   
2. Check for:
   a) Forbidden keywords (from rulebook vector search)
   b) Absolute claims ("bug-free", "guaranteed", "always")
   c) Competitor disparagement (AI Search warns if XYZ mentioned negatively)
   d) Factual hallucinations (cross-ref with Prof's research brief)
   e) Brand tone consistency (semantic similarity to past approved posts)

3. Action:
   - If PASS: → Forward to Ops (publish)
   - If FAIL: → Return specific feedback to Scribe
     Example: "Your claim in para 2 —'this will eliminate X'— violates our 'no absolutes' rule. Soften to 'may reduce'."

4. Log rejection reason → stored in Cosmos DB vector search
   → Used to auto-update Judge's prompt weekly
```

**Key Innovation:** Vector embeddings enable semantic rule enforcement (not just regex matching).

### 5.6 Pixel Agent: Branded Media Generation

**Trigger:** Judge approves draft (parallel execution with Ops)

**Pipeline:**
```
1. Extract headline + key keyword from Scribe's draft
2. Generate image via DALL-E 3:
   - Prompt: "Modern, professional, minimalist design showing [topic]"
   - Size: 1200x630 (social/OG image standard)
3. Post-process with Python PIL:
   a) Add dark gradient overlay (rgba 0,0,0,0.3) for text readability
   b) Render headline in corporate font (e.g., Segoe UI, white, center, 42pt)
   c) Stamp company logo (bottom-right, 100x100px, branded colors)
4. Quality check via Claude Vision API:
   - "Does this image match brand standards?"
   - "Is the text readable?"
   - "Any copyright/NSFW issues?"
5. Upload to Azure Blob Storage
6. Pass image URL to Ops for inclusion in published post
```

**Resilience:**
- DALL-E 3 rate limited? → Queue image generation, use placeholder
- Vision API rejects image? → Retry generation (max 2)
- If Image fails after retries → publish without image + alert Editor

### 5.7 Ops Agent: GitOps Publishing

**Trigger:** Judge approves + Pixel completes (or times out)

**Flow:**
```
1. Receive: Markdown draft + image URL (optional)
2. Commit to GitHub (drafts branch):
   - Path: content/posts/YYYY-MM-DD-slug.md
   - Commit message: "[AAN] {headline} — Scout pitch {pitch_id}"
3. Azure Static Web Apps auto-builds preview:
   - GitHub Actions runs build
   - Hugo/Astro generates preview site
   - Static Web Apps provisions preview URL (e.g., peaceful-sand-xyz.azurestaticapps.net)
4. Post preview link in Teams card:
   - Editor sees live preview before final approval
   - [✅ Publish to Main] [📝 Request Edits] [❌ Reject]
5. If ✅ Publish:
   - Merge drafts branch → main
   - Automatic redeploy to production
   - Post to social media via Azure Logic Apps (Twitter, LinkedIn, etc.)
6. If fails (Git API error, build fails):
   - Retry (max 3)
   - If still fails → store in Azure Service Bus DLQ
   - Daily digest: Editor reviews failed publishes

7. Log to Cosmos DB:
   - Published post ID, publish time, editor approval time
   - Time-to-publish metric (for analytics)
```

---

## 6. Resilience & Error Handling

### 6.1 Circuit Breaker Pattern

**Scenario:** Bing News API fails repeatedly

**Implementation:**
```yaml
Service: Bing News API
Failure Threshold: 3 failures in 5 minutes
Circuit State:
  CLOSED (normal) → request to API
  OPEN (failing) → fallback to cached headlines
  HALF_OPEN (recovering) → test single request

Fallback Strategy:
  - Scout retrieves last 24h of stories from Cosmos DB
  - Filters to "high relevance" scores only
  - Sends familiar headlines (with note: "Fresh data unavailable")
  - Alerts Editor: "Bing API unavailable; using cached headlines"

Recreation:
  - After 5 minutes of success → transition to HALF_OPEN
  - If test request passes → transition to CLOSED
```

### 6.2 Rate Limiting & Throttling

| Service | Limits | mitigation |
|---------|--------|-----------|
| **Bing News API** | 20 req/sec | Batch headlines in single call, Scout cycles every 15 min (not on demand) |
| **Azure OpenAI (GPT-4o)** | Region-specific quotas | Queue requests in Azure Service Bus; monitor usage via Application Insights |
| **DALL-E 3** | 5 images/min (Standard tier) | Pre-queue 5 images per 15-min cycle; store pending in Cosmos DB |
| **GitHub API** | 5,000 req/hour (authenticated) | Batch commits when possible; avoid frequent checks |

### 6.3 Dead Letter Handling

**Scenario:** Scribe draft fails Judge after 3 retries

**Flow:**
```
Scribe fails Judge (iteration 3) 
  → Message sent to Azure Service Bus DLQ
  → Separate "Manual Review" queue in Teams
  → Editor notified: "Story needs manual edit: {story_id}"
  → Editor can:
    a) Edit draft manually + resubmit
    b) Discard story
    c) Mark as "Editor requires different angle"

Daily Digest:
  - 9 AM: Ops sends summary of all DLQ items from past 24h
  - Helps identify patterns (e.g., "Judge rejects all political topics")
  - Used to update Judge's rulebook
```

### 6.4 Cascading Failures

**Safeguard:** No single service failure blocks the pipeline.

| Point of Failure | Fallback |
|------------------|----------|
| Scout | Use cached headlines + alert |
| Prof | Proceed with Scout's summary only (lower confidence) |
| Scribe | Skip content generation; ask Editor to write manually |
| Judge | Bypass compliance check; mark as "Requires Editor Review" |
| Pixel | Publish without image; use default brand image |
| Ops | Retry up to 3x; escalate to Editor |

---

## 7. Cost Optimization Strategy

### 7.1 Tiered Model Selection

**Expected Cost Reduction: ~40%**

```
Old Model Strategy:
  All agents use GPT-4o → ~$0.05 per 1K input tokens

New Strategy (Tiered):
  Scout: GPT-4o-mini → $0.00015 per 1K input tokens (333x cheaper)
  Prof: GPT-4o → $0.03 per 1K input tokens (40% savings over 4o-200k)
  Scribe: GPT-4o → $0.03 per 1K input tokens
  Judge: GPT-4o-mini → $0.00015 per 1K input tokens
  Pixel: DALL-E 3 → flat rate (unavoidable)

Result:
  Baseline (all 4o): ~$500/month (10K API calls/day)
  Tiered: ~$300/month (same volume)
```

### 7.2 Caching & Deduplication

- **Scout:** Cache headlines for 24h; avoid re-ingesting same story
- **Prof:** Cache research results per URL; 7-day TTL
- **Scribe:** Cache style templates; reuse for similar topics
- **Image Cache:** Azure CDN for DALL-E outputs; 30-day retention

---

## 8. Observability & Monitoring

### 8.1 Foundry Native Tracing

**Capture:**
- Agent execution trace (start → end time per agent)
- Tool calls (which API, latency, result)
- Token usage per agent per day
- Conversation threading (full audit trail)

**Storage:** Foundry built-in + Application Insights

### 8.2 Custom Dashboards (Power BI / Azure Monitor)

```
Dashboard: "AAN Daily Operations"
Metrics:
  - Pitches generated per day (target: 15-20)
  - Editor approval rate (target: >40%)
  - Judge rejection rate (target: <10%)
  - Time-to-publish (avg: 2-4 hours from approval)
  - Cost per published article
  - Top-5 topics pitched (trend detection)
  - API health (circuit breaker status)
  
Alerts:
  - Judge rejection rate > 15% → escalate
  - Time-to-publish > 6 hours → investigate
  - Cost per article > $10 → investigate model selection
  - DLQ queue growing → Editor intervention needed
```

### 8.3 Logging Structure

**Structured logs in Application Insights:**

```json
{
  "timestamp": "2026-02-14T10:30:00Z",
  "agent": "Scribe",
  "pitch_id": "story_123",
  "action": "draft_generated",
  "tokens_used": {"input": 2150, "output": 890},
  "duration_ms": 3500,
  "next_agent": "Judge",
  "confidence_score": 0.92
}
```

---

## 9. Technical Stack (Updated)

| Component | Service | Tier | Notes |
|-----------|---------|------|-------|
| **Orchestrator** | Foundry Agent Service | Standard | Connected Agents, native tracing |
| **LLM Inference** | Azure OpenAI Service | GPT-4o (Scribe, Prof), GPT-4o-mini (Scout, Judge) | Tiered for cost |
| **Image Generation** | Azure OpenAI (DALL-E 3) | Standard | Used by Pixel agent |
| **Vision Model** | Claude 3.5 Sonnet (via Anthropic API) | Standard | Image quality validation only |
| **Memory - Working** | Azure Cosmos DB | Serverless, 1-hour autoscale | 30-day rolling state |
| **Memory - Long-term** | Azure AI Search | Standard | Vector embeddings for brand rules |
| **Vector Embeddings** | Embedding Models | text-embedding-3-small | Via Azure OpenAI batch API |
| **Hosting (Agents)** | Foundry Hosted Agents | Auto-scaling | Or Azure Container Apps (Consumption) |
| **Webhooks/Triggers** | Azure Functions | Premium | Timer-based + event-driven |
| **Web Host** | Azure Static Web Apps | Standard | Hugo/Astro framework |
| **Repository** | GitHub (Private) | Separate "drafts" branch for preview |
| **File Storage** | Azure Blob Storage | Standard (Hot tier) | Images + media assets |
| **Message Queue** | Azure Service Bus | Standard | DLQ, rate limiting, async workflows |
| **Notifications** | Microsoft Teams Bot | Azure Bot Service | Adaptive Cards for approvals |
| **Automation** | Azure Logic Apps | Standard | Social media posting, email alerts |
| **Observability** | Application Insights | Standard | Metrics, logs, traces |
| **Dashboard** | Power BI / Azure Monitor | Standard | Custom KPI views |
| **Secrets** | Azure Key Vault | Standard | API keys, GitHub tokens |

---

## 10. Implementation Roadmap (Revised 3-Phase)

### Phase 0: Infrastructure Bootstrap (Week 0)

**Goal:** Foundation ready for agents

**Tasks:**
- [ ] Set up Foundry project in Microsoft Foundry Portal
- [ ] Provision Cosmos DB account (multi-region backup enabled)
- [ ] Create Azure AI Search index structure (for vector embeddings)
- [ ] Deploy Azure OpenAI models: GPT-4o, GPT-4o-mini, DALL-E 3
- [ ] Set up Service Bus namespace for DLQ
- [ ] Configure GitHub repo (private) with drafts branch protection
- [ ] Deploy Static Web Apps resource (linked to GitHub)
- [ ] Set up Application Insights + Power BI dashboard template
- [ ] Create Key Vault for secrets

**Success Criteria:** All agents can execute a test workflow end-to-end (no external APIs needed)

---

### Phase 1: Scout + Judge (Weeks 1-2) — "Ear + Quality Gate"

**Goal:** 15-20 story pitches per day, with upstream filtering

**Tasks:**
- [ ] Deploy Scout agent (Foundry Connected Agent)
  - [ ] Integrate Bing News API
  - [ ] Implement circuit breaker
  - [ ] Create Teams Adaptive Card for pitches
- [ ] Deploy Judge agent
  - [ ] Vector-embed brand rulebook into AI Search
  - [ ] Implement semantic rule checking
  - [ ] Create rejection feedback loop to Cosmos DB
- [ ] Set up Editor approval interface (Microsoft Teams)
- [ ] Configure timer trigger (15-min intervals)
- [ ] Create monitoring dashboard for Scout metrics

**Success Criteria:**
- Scout generates 15-20 pitches per day
- Judge processes sample drafts (manual input)
- Editor receives Teams cards with <5 min latency
- Circuit breaker tested (API simu­lation)

---

### Phase 2: Prof + Scribe + Feedback Loops (Weeks 3-4) — "Brain + Iteration"

**Goal:** Approved pitches → published drafts in 1-2 hours

**Tasks:**
- [ ] Deploy Prof agent (Foundry)
  - [ ] Integrate Bing Search v7 + Azure AI Search
  - [ ] Implement feedback loop to Scout (rescan logic)
  - [ ] Create research brief output format
- [ ] Deploy Scribe agent (Foundry)
  - [ ] Implement tone library (4 styles)
  - [ ] Build iteration loop with Judge (max 3 retries)
  - [ ] Create escalation to DLQ after max retries
- [ ] Build Agent Mesh messaging between Prof ↔ Scribe ↔ Judge
  - [ ] Conditional routing (fail → iterate vs. escalate)
  - [ ] Retry policies with exponential backoff
- [ ] Create end-to-end test scenario (5 sample pitches → published drafts)

**Success Criteria:**
- Full workflow executes end-to-end
- Time-to-publish < 2 hours from approval
- Judge 95%+ acceptance on first try
- DLQ remains empty (zero escalations)

---

### Phase 3: Pixel + Ops + Full Observability (Weeks 5-6) — "Brand + Analytics"

**Goal:** Production-ready system with branded images + detailed metrics

**Tasks:**
- [ ] Deploy Pixel agent
  - [ ] Integrate DALL-E 3 for image generation
  - [ ] Build PIL post-processing pipeline (gradients, fonts, logos)
  - [ ] Integrate Claude Vision for image QA
  - [ ] Handle DALL-E rate limiting gracefully
- [ ] Deploy Ops agent
  - [ ] Implement GitHub API for commit/branch logic
  - [ ] Integrate Static Web Apps preview URLs
  - [ ] Set up social media posting via Logic Apps
  - [ ] Implement DLQ monitoring + daily digest
- [ ] Build comprehensive observability:
  - [ ] Power BI dashboard with KPIs
  - [ ] Daily cost report (avg $/article)
  - [ ] Pitch acceptance trends (topics, times)
  - [ ] Judge rejection patterns (for rulebook updates)
- [ ] Load testing (10K API calls/day simulation)
- [ ] Run chaos engineering tests (API failures, timeouts)

**Success Criteria:**
- System stable under load
- All published articles include branded images
- Editor receives daily summary of operations
- Cost tracking accurate + <$10/article

---

## 11. Comparative Analysis (Gen 1.5 vs Gen 2 vs Gen 3)

| Feature | Gen 1.5 (Co-pilot) | Gen 2 (Original AAN) | Gen 3 (v3.0 — This Doc) |
|---------|-------------------|----------------------|------------------------|
| **Trigger** | Manual | Event-Driven | Event-Driven + Feedback |
| **Context** | Session | Stateful (Cosmos DB) | 3-Tier Memory (Immediate/Working/Long-term) |
| **Quality** | Unverified | Self-Correcting (Judge) | Self-Correcting + Learning (vector rules) |
| **Action** | Text-Only | Tool-Use (Git, APIs) | Tool-Use + Resilience Patterns |
| **Topology** | N/A | Linear (Scout→Prof→Scribe→Judge→Ops) | Mesh (agents can re-route, feedback loops) |
| **Cost** | N/A | ~$500/mo (all GPT-4o) | ~$300/mo (tiered models) |
| **Resilience** | N/A | Basic | Production-Grade (circuit breakers, DLQ, fallbacks) |
| **Observability** | N/A | Basic logging | Foundry tracing + Power BI dashboards |
| **Learning** | N/A | Manual rulebook edits | Automatic rulebook updates (vector embeddings) |
| **Scalability** | Single user | 1 newsroom | Multi-tenant ready (Foundry multi-agent) |

Conclusion: Gen 3 (v3.0) transforms AAN from a prototype into a **production-grade, self-improving, resilient multi-agent system** ready for enterprise newsrooms.

---

## 12. Success Metrics & KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Pitches/day** | 15-20 | Scout counter |
| **Editor approval rate** | >40% | (Approvals / Total pitches) × 100 |
| **Judge acceptance rate** | 95%+ on first try | (Passed / Total submissions) × 100 |
| **Time-to-publish** | < 2 hours | (Publish time - Approval time) |
| **Cost per article** | < $10 | Total spend / articles published |
| **Uptime** | 99.9% | (Operational mins / Total mins) × 100 |
| **Judge rejection rate** | < 10% | (Rejections / Total) × 100 |
| **DLQ queue growth** | Zero backlog | Manual review queue drain rate |

---

## 13. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **API Quota Exhaustion** | System grinds to halt | Implement rate limiting + alerting; tiered model strategy reduces token spend |
| **LLM Drift** | Quality degradation over time | Vector-embedded rulebook auto-updates; weekly brand rule reviews |
| **Hallucination** | False facts published | Judge cross-checks with Prof research + Content Safety API |
| **Regional Outage** | Full downtime | Cosmos DB multi-region + Static Web Apps auto-failover |
| **Privacy/Compliance** | Regulatory risk | RBAC via Entra ID; audit logs in Application Insights; data residency control |
| **Social Media Toxicity** | Brand damage | Judge + Content Safety filter; Editor manual review before social posting |

---

## 14. Next Steps

1. **Week 0:** Approve this v3.0 design; green-light infrastructure bootstrap
2. **Week 1-2:** Spin up Phase 0 (Foundry setup) + Phase 1 (Scout + Judge)
3. **Week 3-4:** Phase 2 (Prof + Scribe + agent mesh integration)
4. **Week 5-6:** Phase 3 (Pixel + Ops + full observability)
5. **Week 7:** Load testing + chaos engineering
6. **Week 8:** GA readiness review + go-live

---

**Document Version:** 3.0  
**Last Updated:** February 14, 2026  
**Architect:** Agentic AI Architecture Team (Azure)  
**Status:** Ready for Implementation ✅
