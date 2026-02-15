# Detailed Implementation Roadmap

**Document Version:** 1.0  
**Date:** February 14, 2026  
**Duration:** 8 weeks to production GA  
**Status:** Ready for execution

---

## Executive Summary

This roadmap details the step-by-step implementation of Azure Autonomous Newsroom v3.0, broken into 4 phases:

| Phase | Duration | Focus | Go/No-Go Gate |
|-------|----------|-------|---------------|
| **Phase 0** | Week 0 | Infrastructure bootstrap | Pass: All services deployed & tested |
| **Phase 1** | Weeks 1-2 | Scout + Judge (Ear + Quality Gate) | Pass: 15+ pitches/day, zero rejections from test |
| **Phase 2** | Weeks 3-4 | Prof + Scribe + Agent Mesh | Pass: End-to-end workflow functional |
| **Phase 3** | Weeks 5-6 | Pixel + Ops + Full Observability | Pass: Load testing + chaos engineering |
| **Phase 4** | Week 7 | Production hardening & GA readiness | Pass: Security audit + compliance |

---

## Phase 0: Infrastructure Bootstrap

**Duration:** Week 0 (5 business days)  
**Team:** Cloud Architect (lead), 1 DevOps, 1 Backend Engineer  
**Deliverable:** All Azure services deployed, agents can execute test workflow

### 0.1 Azure Resources Creation

**Priority 1 (Days 1-2):**

- [ ] **Foundry Project**
  - Task: Create Microsoft Foundry project in ai.azure.com
  - Owner: Cloud Architect
  - Success: Project dashboard accessible
  - Costs: $0 (included in Foundry)

- [ ] **Azure OpenAI Service**
  - Task: Deploy GPT-4o (1 instance), GPT-4o-mini (1 instance), DALL-E 3 (1 instance)
  - Owner: Cloud Architect
  - Success: Model is available + token limit increased to 10K TPM
  - Costs: ~$50/month (base deployment)
  - Note: Request quota increase for peek load (500K tokens/day = ~$0.30)

- [ ] **Azure Cosmos DB**
  - Task: Deploy serverless account (auto-scale)
  - Owner: DevOps
  - Config:
    - Regions: East US (primary), West US (secondary for failover)
    - Database: `newsroom`; Containers: `pitches`, `judge_feedback`, `editor_decisions`
    - Partition keys: `pk` (agent_id/date)
    - TTL: 30 days on `pitches`
  - Success: Database created, test document inserted/retrieved
  - Costs: ~$250/month (serverless autoscale)

- [ ] **Azure AI Search (Vector Store)**
  - Task: Deploy Standard tier
  - Owner: DevOps
  - Config:
    - Index: `brand_knowledge`
    - Field: `embedding` (1536 dimensions)
    - Indexer: Manual (seed with brand rulebook)
  - Success: Sample rules indexed + semantic search returns results
  - Costs: ~$150/month

- [ ] **Azure Storage (Blobs)**
  - Task: Create container `newsroom-images` (Hot tier)
  - Owner: DevOps
  - Config: Public access disabled; CORS enabled for Static Web Apps
  - Success: File upload/download works
  - Costs: ~$20/month

**Priority 2 (Days 2-3):**

- [ ] **Azure Static Web Apps**
  - Task: Create Standard tier instance
  - Owner: DevOps
  - Config: Link to GitHub repo (drafts branch for preview builds)
  - Success: Preview build triggers on GitHub push
  - Costs: ~$100/month

- [ ] **Azure Service Bus**
  - Task: Create Standard namespace
  - Owner: DevOps
  - Config: Queue `agent-dlq` (dead letter queue for failures)
  - Success: Test message queued + retrieved
  - Costs: ~$75/month

- [ ] **Azure Key Vault**
  - Task: Create Standard vault
  - Owner: DevOps
  - Secrets:
    - `github-token` (PAT)
    - `bing-api-key`
    - `twitter-api-key`
    - `openai-api-key`
  - Access: Managed Identity for services + RBAC for humans
  - Success: Secret retrieved via SDK
  - Costs: ~$10/month

- [ ] **Azure Application Insights**
  - Task: Create workspace (linked to Cosmos DB for context)
  - Owner: DevOps
  - Config: 
    - Log analytics workspace
    - Data retention: 90 days
    - Sampling: Turn OFF (we'll sample at agent level)
  - Success: Test log ingested
  - Costs: ~$50/month

**Priority 3 (Days 4-5):**

- [ ] **GitHub Repository**
  - Task: Create private repo `azure-newsroom`
  - Owner: Backend Engineer
  - Config:
    - Branch protection on `main`
    - `drafts` branch for preview builds
    - Webhooks: POST to Logic Apps on push
    - Actions: Build + deploy to Static Web Apps
  - Success: Test commit triggers build
  - Costs: $0 (GitHub repo, LFS storage if needed)

- [ ] **Azure Logic Apps**
  - Task: Create automation for social media posting
  - Owner: Backend Engineer
  - Workflows:
    - Trigger: Ops publishes article
    - Action 1: POST to Twitter/X
    - Action 2: POST to LinkedIn
    - Action 3: Webhook to Slack (optional notifications)
  - Success: Test workflow executes end-to-end
  - Costs: ~$30/month (per action)

- [ ] **Microsoft Teams Bot Setup**
  - Task: Register bot in Azure Bot Service
  - Owner: Backend Engineer
  - Config: Bot Framework, Adaptive Cards support
  - Success: Bot can send test message to channel
  - Costs: ~$0 (Teams Bot is free tier)

### 0.2 Foundry Agent Infrastructure

**Days 3-5:**

- [ ] **Deploy Foundry Agent Framework**
  - Task: Set up Foundry Agent Service (Connected Agents capability)
  - Owner: Cloud Architect
  - Config:
    - Agent runtime: Foundry Hosted (or Azure Container Apps if preferred)
    - Model deployments: Link to Azure OpenAI instances
    - Tracing: Enable built-in tracing to App Insights
  - Success: Can list agents via CLI; agent SDK functional
  - Costs: Included in Foundry

- [ ] **Test Foundry Agent Mesh**
  - Task: Create 2 test agents; verify bidirectional messaging
  - Owner: Backend Engineer
  - Test:
    - Agent A sends message → Agent B receives it
    - Agent B replies → Agent A receives it
    - Messagethrough thread history
  - Success: Full roundtrip communication works
  - Costs: $0

- [ ] **Configure Agent Observability**
  - Task: Enable Foundry tracing; connect to Application Insights
  - Owner: DevOps
  - Config:
    - Trace sampler: Log all traces (we'll downsample later)
    - Instrumentation key: Linked to App Insights
  - Success: Test agent execution shows up in App Insights
  - Costs: $0 (included in App Insights)

### 0.3 Security & Compliance Hardening

**Days 4-5:**

- [ ] **Virtual Network Setup**
  - Task: Create VNet with private endpoints for Cosmos, AI Search, Storage
  - Owner: Cloud Architect
  - Config: All services behind private link (no public IP)
  - Success: Services accessible only via VNet or Managed Identity
  - Costs: +~$50/month (private link service)

- [ ] **Identity & RBAC**
  - Task: Set up Managed Identities for all agents; RBAC roles for team
  - Owner: Cloud Architect
  - Config:
    - Managed ID for each agent (Scout, Prof, Scribe, Judge, Pixel, Ops)
    - Roles: Reader (for Cosmos reads), Contributor (for writes), Limited to specific containers
    - Team access: Editors get "Viewer" role (read-only dashboards)
  - Success: Agent can read/write without connection strings
  - Costs: $0 (Managed Identity is free)

- [ ] **Content Safety API**
  - Task: Enable Azure Content Safety for Judge agent
  - Owner: Backend Engineer
  - Config: Check for harmful, sexual, violent content; custom categories (competitor names)
  - Success: Test API call returns safety scores
  - Costs: ~$0.01 per call; budget ~$30/month

### 0.4 Phase 0 Validation Checklist

- [ ] All Azure services deployed & accessible
- [ ] Managed Identities configured for all services
- [ ] Key Vault secrets populated
- [ ] Foundry project created & agents can execute
- [ ] GitHub repo created with branch protection
- [ ] Application Insights receiving traces
- [ ] Static Web Apps linked to GitHub
- [ ] Teams Bot can send/receive messages
- [ ] Cost baseline calculated (Phase 0 = $700-800/month)

**Phase 0 Success Criteria:** ✅ All services healthy, agents can execute test workflow

**Go/No-Go Gate:** Approve Phase 1 kickoff

---

## Phase 1: Scout + Judge (Weeks 1-2)

**Duration:** 2 weeks  
**Team:** Backend Engineer (Scout), Backend Engineer (Judge), Data Engineer (RAG setup)  
**Goal:** 15-20 story pitches per day; Judge validates test drafts

### 1.1 Scout Agent Deployment

**Week 1, Days 1-3:**

- [ ] **Scout Agent Code**
  - Task: Implement Scout agent in Foundry SDK (Python)
  - Owner: Backend Engineer #1
  - Code:
    ```python
    from foundry import Agent
    
    agent = Agent(
        name="scout",
        model="gpt-4o-mini",
        system_prompt="""You are Scout, the Watchdog. Your job is to:
        1. Ingest 500+ headlines from news/social feeds
        2. Filter for relevance to our topics: AI, Tech, Finance, Local
        3. Calculate Relevance Score (0-10) based on criteria...
        4. Generate Markdown story pitch cards
        """,
        tools=["bing_news_api", "cosmos_db_read"],
        max_retries=3,
        timeout_sec=45
    )
    ```
  - Success: Agent code compiles; can be deployed to Foundry
  - Time estimate: 2-3 days

- [ ] **Bing News API Integration**
  - Task: Create wrapper for Bing News API; handle pagination + caching
  - Owner: Backend Engineer #1
  - Code:
    - `bing_news_client.py`: Call Bing API, cache results to Cosmos DB
    - Returns: List of headlines with scores
  - Success: ~500 headlines ingested in 30 seconds
  - Time estimate: 1 day

- [ ] **Relevance Scoring Logic**
  - Task: Implement scoring algorithm (keyword matching, source credibility, recency)
  - Owner: Backend Engineer #1
  - Code:
    ```python
    def calculate_relevance_score(headline, source, interest_profile):
        # Keyword match (0-3 pts)
        keyword_score = sum(1 for kw in interest_profile.keywords if kw in headline.lower()) / 3
        
        # Source credibility (0-3 pts)
        source_score = SOURCE_CREDIBILITY_MAP.get(source.domain, 1.0)
        
        # Age penalty (0-2 pts)
        age_score = 2.0 * (1 - (now() - headline.published_time).days / 7)
        
        # Uniqueness (0-2 pts)
        uniqueness_score = 2.0 if not similar_story_in_past_24h(headline) else 0
        
        return keyword_score + source_score + age_score + uniqueness_score
    ```
  - Success: Scoring produces 0-10 distribution; reasonable results
  - Time estimate: 1.5 days

- [ ] **Scout Testing**
  - Task: Unit + integration tests
  - Owner: Backend Engineer #1
  - Tests:
    - Bing API mock returns 500 headlines → Scout filters to top-5
    - Relevance score correctly calculated
    - Teams Adaptive Card rendered
  - Success: >90% test pass rate
  - Time estimate: 0.5 days

**Week 1, Days 4-5:**

- [ ] **Scout Deployment**
  - Task: Deploy to Foundry; run live on 15-min timer
  - Owner: Backend Engineer #1
  - Config: Timer trigger every 15 min UTC
  - Success: First pitches appear in Teams
  - Time estimate: 0.5 days

- [ ] **Scout Monitoring**
  - Task: Set up dashboards + alerts for Scout
  - Owner: Data Engineer
  - Metrics:
    - Pitches generated per 15-min cycle
    - Relevance score distribution
    - API latency
  - Success: Dashboard visible in Power BI
  - Time estimate: 1 day

### 1.2 Judge Agent Deployment

**Week 1, Days 3-5 (parallel with Scout scaling):**

- [ ] **Brand Rulebook Creation**
  - Task: Finalize brand rules (Markdown format)
  - Owner: Product Manager / Editor
  - Content:
    - "No absolute claims" rule with examples
    - "Competitor respect" rule
    - "Financial claims need 2 sources"
    - 10-15 total rules
  - Success: Rulebook document finalized
  - Time estimate: 1 day

- [ ] **Vector Embedding of Rulebook**
  - Task: Embed brand rules into Azure AI Search
  - Owner: Data Engineer
  - Process:
    1. Parse Markdown rulebook into semantic chunks
    2. Call Azure OpenAI embedding API (text-embedding-3-small)
    3. Upload vectors to AI Search index
  - Success: Semantic search on brand rules works (test queries)
  - Time estimate: 1.5 days
  - Code:
    ```python
    from azure.search.documents.indexes import SearchIndexClient
    
    # Chunk rulebook
    chunks = [
        "Avoid absolute claims like 'bug-free', 'guarantee'",
        "Anthropic is our friend; frame as 'everyone advancing AI'",
        ...
    ]
    
    # Embed
    embeddings = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )
    
    # Upload to AI Search
    for chunk, emb in zip(chunks, embeddings):
        index.upload_document({
            "rule_text": chunk,
            "embedding": emb.embedding
        })
    ```

- [ ] **Judge Agent Code**
  - Task: Implement Judge agent
  - Owner: Backend Engineer #2
  - Code:
    ```python
    agent = Agent(
        name="judge",
        model="gpt-4o-mini",
        system_prompt="""You are Judge. Your job is to validate drafts against brand rules.
        1. Search brand rulebook (vector search)
        2. Check for violations
        3. Provide specific feedback if fail
        """,
        tools=["azure_ai_search_vector", "azure_content_safety"],
        timeout_sec=30
    )
    ```
  - Success: Judge can process test draft; returns pass/fail
  - Time estimate: 2 days

- [ ] **Judge Testing**
  - Task: Test Judge against manually written drafts
  - Owner: Backend Engineer #2
  - Test cases:
    - Draft with absolute claim → FAIL (with specific feedback)
    - Draft with competitor disparagement → FAIL
    - Clean draft → PASS
  - Success: 100% accuracy on test set
  - Time estimate: 1 day

**Week 2, Days 1-2:**

- [ ] **Scout + Judge Integration**
  - Task: Scout generates pitches → Editor approves → Judge validates sample drafts
  - Owner: Backend Engineer #1 + #2
  - Test: 
    - Scout sends pitch
    - Editor manually writes draft for that pitch
    - Judge validates draft
  - Success: Full loop works without errors
  - Time estimate: 1 day

- [ ] **Editor Approval UI (Teams)**
  - Task: Enhance Teams Adaptive Card for better UX
  - Owner: Backend Engineer #1
  - Card elements:
    - Headline + summary
    - [✅ Approve & Write] [🔄 Research More] [❌ Skip]
    - Confidence score + source count
  - Success: UI renders correctly; buttons work
  - Time estimate: 1.5 days

### 1.3 Phase 1 Validation & Monitoring

**Week 2, Days 3-5:**

- [ ] **Metrics Dashboard (Scout + Judge)**
  - Task: Create Power BI dashboard
  - Owner: Data Engineer
  - Metrics:
    - Pitches/day (target: 15-20)
    - Approval rate (target: >40%)
    - Judge rejection rate on manual drafts (target: <15%)
    - API latencies
  - Success: Dashboard deployed; metrics visible
  - Time estimate: 1 day

- [ ] **Alert Rules**
  - Task: Set up alerts
  - Owner: Data Engineer
  - Alerts:
    - Scout down (no pitches for 30 min)
    - Judge rejection rate spike (>30%)
  - Success: Test alert fires
  - Time estimate: 0.5 days

- [ ] **Phase 1 Load Testing**
  - Task: Simulate 7-day continuous operation
  - Owner: Backend Engineer #1
  - Test:
    - 15-min scouts * 7 days = 672 pitch generations
    - 100 manual drafts validated by Judge
  - Success: Zero errors; system stable
  - Time estimate: 1 day (automated test)

### 1.4 Phase 1 Success Criteria

✅ **Pitch Generation:**
- Scout generates 15-20 pitches per day
- Relevance scores reasonable (8-10 for top stories)
- Teams Adaptive Cards render perfectly

✅ **Judge Validation:**
- Judge processes drafts with >95% accuracy
- Rejection reasons specific + actionable
- Vector search for brand rules works

✅ **Monitoring:**
- Power BI dashboard live
- Alerts configured
- Cost tracking: ~$950/month (Phase 0 + Phase 1 services)

✅ **Load Testing:**
- System handles 7-day continuous load
- Zero critical errors
- No performance degradation

**Phase 1 Go/No-Go Gate:** Approve Phase 2 if all criteria met; else fix issues + retest

---

## Phase 2: Prof + Scribe + Agent Mesh (Weeks 3-4)

**Duration:** 2 weeks  
**Team:** Backend Engineer (Prof), Backend Engineer (Scribe), Backend Engineer (Mesh Orchestration)  
**Goal:** End-to-end workflow: Pitch → Approval → Draft published

### 2.1 Prof Agent Deployment

**Week 3, Days 1-3:**

- [ ] **Prof Research Module**
  - Task: Implement research deep-dive (semantic search + web search)
  - Owner: Backend Engineer #3
  - Tools:
    - Azure AI Search (vector) for internal knowledge
    - Bing Search v7 for external sources
  - Code:
    ```python
    def research_story(headline, summary):
        # Search internal knowledge
        internal = ai_search.search(query=headline, k=5)
        
        # Search external sources
        external = bing_search.search(q=headline, count=10)
        
        # Corroborate facts
        corroboration_score = calculate_corroboration(internal + external)
        
        return {
            "facts": [extract_facts_from(d) for d in results],
            "sources": external,
            "corroboration_level": corroboration_score
        }
    ```
  - Success: Prof searches return 10+ sources; facts extracted
  - Time estimate: 2 days

- [ ] **Prof Feedback Loop (Back to Scout)**
  - Task: Implement logic for Prof to request Scout rescan
  - Owner: Backend Engineer #3
  - Logic:
    ```python
    if corroboration_level < 0.70:
        send_message_to_scout({
            "message_type": "rescan_request",
            "keywords": extract_keywords_from_facts(),
            "date_range": "last_6_hours"
        })
        wait_for_response(timeout_sec=600)  # 10 min
    ```
  - Success: Prof can trigger Scout rescan; waits for result
  - Time estimate: 1 day

- [ ] **Prof Testing**
  - Task: Unit + integration tests
  - Owner: Backend Engineer #3
  - Tests:
    - Headline → Prof searches → Returns 10+ results
    - Corroboration score calculated correctly
    - Scout rescan request triggers new Scout sweep
  - Success: >90% test pass
  - Time estimate: 1 day

### 2.2 Scribe Agent Deployment

**Week 3, Days 2-4:**

- [ ] **Scribe Generation Module**
  - Task: Implement content generation with tone selection
  - Owner: Backend Engineer #4
  - Code:
    ```python
    def generate_draft(research_brief, tone="technical_blog"):
        tone_templates = {
            "technical_blog": "Formal, sto rich in detail, data-driven",
            "conversational": "Friendly, accessible, ELI5 style",
            "urgent": "Breaking news tone, immediate relevance",
            "educational": "Teaching mode, explain concepts"
        }
        
        prompt = f"""
        Write a {tone_templates[tone]} article based on this research:
        {format_research_brief(research_brief)}
        
        Output Markdown with Frontmatter.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    ```
  - Success: Drafter generates Markdown articles with frontmatter
  - Time estimate: 1.5 days

- [ ] **Scribe Iteration Loop**
  - Task: Implement retry logic (max 3 iterations with Judge feedback)
  - Owner: Backend Engineer #4
  - Logic:
    ```python
    for iteration in range(1, 4):
        draft = generate_draft(research_brief)
        judge_result = judge_agent.validate(draft)
        
        if judge_result.status == "PASSED":
            return draft
        
        # Iterate with feedback
        feedback = judge_result.feedback
        draft = generate_draft(research_brief, feedback=feedback)
    
    # If all 3 fail, escalate
    escalate_to_dlq(draft, judge_result.reasons)
    ```
  - Success: Draft iterates with Judge; stops after 3 tries
  - Time estimate: 1 day

- [ ] **Scribe Testing**
  - Task: Multi-iteration test scenarios
  - Owner: Backend Engineer #4
  - Tests:
    - Research brief → Draft generated
    - Judge feedback → Scribe revises → Judge re-checks
    - After 3 failures → Escalates
  - Success: >90% pass rate on integration tests
  - Time estimate: 1 day

### 2.3 Agent Mesh Orchestration

**Week 3, Days 3-5:**

- [ ] **Foundry Connected Agents Configuration**
  - Task: Set up all 6 agents with proper routing + messaging
  - Owner: Backend Engineer (Mesh Lead)
  - Config (YAML):
    ```yaml
    agents:
      scout:
        routes_to: [prof, editor]  # After Scout detects
      prof:
        routes_to: [scribe, scout]  # Prof → Scribe OR back to Scout
      scribe:
        routes_to: [judge]  # Scribe → Judge
      judge:
        routes_to: [scribe, pixel, ops]  # Judge → Iterate or Proceed
      pixel:
        routes_to: [ops]  # Pixel → Ops
      ops:
        routes_to: [dui_teams]  # Ops → Editor (final approval)
    ```
  - Success: Agents communicate via Foundry message bus
  - Time estimate: 2 days

- [ ] **Conditional Routing Logic**
  - Task: Implement decision trees
  - Owner: Backend Engineer (Mesh Lead)
  - Example routing:
    ```
    if judge_passes:
      route_to: [pixel, ops]  # Parallel execution
      wait_for: both_complete
    
    elif judge_fails AND iteration < 3:
      route_to: scribe
      with_feedback: judge_rejection_details
    
    else:  # iteration >= 3
      route_to: dlq
      with_context: full_conversation_thread
    ```
  - Success: Routing decisions execute correctly
  - Time estimate: 1.5 days

- [ ] **Error Handling & Retry Policies**
  - Task: Implement circuit breakers, timeouts, retries
  - Owner: Backend Engineer (Mesh Lead)
  - Config:
    - Scout: 3 retries, exponential backoff
    - Prof: 2 retries, fallback to low-confidence
    - Scribe: 1 per iteration (explicit), max 3 iterations
    - Judge: 0 retries (decision final), but fast timeout (30s)
    - Pixel: 2 retries, fallback to text-only
    - Ops: 3 retries, then DLQ
  - Success: Timeouts trigger; retries backoff; DLQ handles final failures
  - Time estimate: 1.5 days

### 2.4 End-to-End Integration

**Week 4, Days 1-3:**

- [ ] **Full Pipeline Test (Manual)**
  - Task: Execute complete workflow: Scout → Editor → Prof → Scribe → Judge → Ops
  - Owner: All Backend Engineers
  - Test scenario:
    1. Scout generates real pitch (top story of day)
    2. Editor approves in Teams
    3. Prof researches (AI Search + Bing)
    4. Scribe drafts (GPT-4o, technical tone)
    5. Judge validates (passes on first try)
    6. Pixel generates image (DALL-E 3, skipped if not ready)
    7. Ops commits to drafts branch → builds preview
    8. Editor approves preview (in Teams UI)
    9. Merges to main → live!
  - Success: Story appears live on preview site
  - Time estimate: 2 days (execution + debugging)

- [ ] **Chaos Engineering (Week 4, Days 3-4)**
  - Task: Simulate failures; verify graceful degradation
  - Owner: Backend Engineer (Mesh Lead)
  - Chaos tests:
    - Scout API timeout → Fallback to cache
    - Prof research insufficient → Flag but proceed
    - Scribe times out → Alert Editor
    - Judge fails 3x → Escalate to DLQ
    - Pixel image gen fails → Publish without image
    - Ops GitHub API error → Retry correctly
  - Success: System handles all failures; no data loss
  - Time estimate: 1 day

### 2.5 Phase 2 Validation

**Week 4, Days 4-5:**

- [ ] **Performance Benchmarking**
  - Task: Measure end-to-end latencies
  - Owner: Backend Engineer (Mesh Lead)
  - Metrics:
    - Scout execution: <2 min
    - Prof research: <2 min
    - Scribe generation: <2 min (GPT-4o typical)
    - Judge check: <30s
    - Time-to-publish: <3 hours (incl. human approval waits)
  - Success: All latencies within target
  - Time estimate: 0.5 days

- [ ] **Update Dashboards**
  - Task: Extend Power BI with Phase 2 metrics
  - Owner: Data Engineer
  - New charts:
    - Prof research confidence score (distribution)
    - Scribe iteration count (how many revisions)
    - Judge rejection rate (by agent/topic)
    - Time-to-publish (histogram)
  - Success: Phase 2 metrics visible in dashboards
  - Time estimate: 1 day

### 2.6 Phase 2 Success Criteria

✅ **End-to-End Workflow:**
- Scout → Editor approval → Prof → Scribe → Judge → Ops → Editor preview → Live

✅ **Agent Mesh:**
- All 6 agents connected via Foundry
- Conditional routing works correctly
- Feedback loops (Prof→Scout, Judge→Scribe) functional

✅ **Performance:**
- End-to-end time: <3 hours (excl. human waits)
- No missed stories due to timeouts

✅ **Reliability:**
- Chaos engineering: All failures handled gracefully
- No data loss under any fault condition
- DLQ catches escalations correctly

✅ **Monitoring:**
- Phase 2 metrics in Power BI
- Alerts for critical failures
- Cost tracking: ~$1,200/month

**Phase 2 Go/No-Go Gate:** Approve Phase 3 if system stable + meets performance SLAs

---

## Phase 3: Pixel + Ops + Full Observability (Weeks 5-6)

**Duration:** 2 weeks  
**Team:** Backend Engineer (Pixel), Backend Engineer (Ops), Data Engineer (Observability), DevOps (Infrastructure)  
**Goal:** Production-ready system with branded images + comprehensive monitoring

### 3.1 Pixel Agent Deployment

**Week 5, Days 1-3:**

- [ ] **Image Generation Module**
  - Task: Implement DALL-E 3 integration with PIL post-processing
  - Owner: Backend Engineer #5
  - Code:
    ```python
    from PIL import Image, ImageDraw, ImageFont
    import openai
    
    def generate_branded_image(headline, keywords):
        # Step 1: DALL-E 3 generation
        prompt = f"Modern, professional, minimalist image about {keywords}"
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size="1024x768",
            quality="standard"
        )
        image_url = response.data[0].url
        
        # Step 2: PIL post-processing
        img = Image.open(requests.get(image_url, stream=True).raw)
        
        # Add gradient overlay
        gradient = create_gradient(1200, 630, color=(0, 0, 0), alpha=0.3)
        img = Image.alpha_composite(img.convert("RGBA"), gradient)
        
        # Add text
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("segoe-ui-bold.ttf", 42)
        draw.text((600, 315), headline, font=font, fill="white", anchor="mm")
        
        # Add logo
        logo = Image.open("logo.png").resize((100, 100))
        img.paste(logo, (1100, 530), logo)
        
        return img
    ```
  - Success: Images generated with branding applied
  - Time estimate: 1.5 days

- [ ] **Image Quality Assurance (Claude Vision)**
  - Task: Use Claude vision model to QA generated images
  - Owner: Backend Engineer #5
  - Logic:
    ```python
    def validate_image_quality(image_url):
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [{
                    "type": "image",
                    "source": {"type": "url", "url": image_url}
                }, {
                    "type": "text",
                    "text": """Rate this image:
                    1. Is text readable? (yes/no)
                    2. Does it match brand standards? (yes/no)
                    3. Any copyright/NSFW issues? (yes/no)
                    Return JSON: {readable, brand_aligned, safe, score}"""
                }]
            }]
        )
        return json.loads(response.content[0].text)
    ```
  - Success: Image QA returns pass/fail + quality score
  - Time estimate: 1 day

- [ ] **Pixel Testing + Deployment**
  - Task: Test Pixel agent end-to-end; deploy to Foundry
  - Owner: Backend Engineer #5
  - Tests:
    - Headline + keywords → Image generated (verify uniqueness)
    - Vision QA passes >90% of images
    - Images upload to Azure Blob Storage
  - Success: Pixel agent can be called live
  - Time estimate: 1.5 days

### 3.2 Ops Agent Deployment

**Week 5, Days 2-4:**

- [ ] **GitHub API Integration**
  - Task: Implement GitOps workflow (commit, branch, merge)
  - Owner: Backend Engineer #6
  - Code:
    ```python
    import pygithub
    
    def publish_story(markdown_content, image_url, headline):
        repo = github.get_repo("org/azure-newsroom")
        
        # Create draft file
        path = f"content/posts/{date.today()}-{slug(headline)}.md"
        content_with_image = add_image_to_markdown(markdown_content, image_url)
        
        # Commit to drafts branch
        repo.create_file(
            path=path,
            message=f"[AAN] {headline}",
            content=content_with_image,
            branch="drafts"
        )
        
        # Return preview URL
        # (Static Web Apps auto-builds, provides URL)
        preview_url = f"https://{preview_build_id}.azurestaticapps.net"
        return preview_url
    ```
  - Success: Files committed to GitHub; preview URL generated
  - Time estimate: 1.5 days

- [ ] **Static Web Apps Integration**
  - Task: Configure builds + track preview URLs
  - Owner: DevOps
  - Config:
    - Build trigger: GitHub Actions (on drafts branch push)
    - Build framework: Hugo or Astro
    - Output: Preview staging URL
  - Success: commit → 2 min build → preview URL
  - Time estimate: 1 day

- [ ] **Social Media Automation (Logic Apps)**
  - Task: Integrate with Twitter, LinkedIn, Slack (post-publication)
  - Owner: Backend Engineer #6
  - Workflow:
    1. Article published (main branch)
    2. Logic Apps triggered (webhook from GitHub)
    3. POST to Twitter API (link + excerpt)
    4. POST to LinkedIn (same)
    5. POST to Slack (team notification)
  - Success: Published story automatically posted to social
  - Time estimate: 1 day

- [ ] **Ops Testing + Deployment**
  - Task: End-to-end publish test with all integrations
  - Owner: Backend Engineer #6
  - Test:
    1. Judge approves draft
    2. Ops commits to GitHub
    3. Preview builds
    4. Editor approves preview
    5. Ops merges to main
    6. Social media posts fire
    7. Slack notifies team
  - Success: Full publish pipeline works
  - Time estimate: 1 day

### 3.3 Full Observability Setup

**Week 5, Days 4-5 + Week 6, Days 1-2:**

- [ ] **Foundry Tracing Deep Dive**
  - Task: Capture end-to-end traces for every pitch
  - Owner: Data Engineer (Observability)
  - Implementation:
    - Enable Foundry native tracing (all agents)
    - Set trace sample rate: 100% (full detail)
    - Connect to Application Insights
  - Success: Every pitch has full trace in App Insights
  - Time estimate: 0.5 days

- [ ] **Custom Metrics Implementation**
  - Task: Define + instrument KPIs
  - Owner: Data Engineer (Observability)
  - Metrics:
    - aan_pitches_generated (counter)
    - aan_approval_rate (gauge)
    - aan_judge_rejection_rate (gauge)
    - aan_publish_duration_sec (histogram)
    - aan_cost_per_article_usd (gauge)
  - Code:
    ```python
    from opentelemetry import metrics
    meter = metrics.get_meter(__name__)
    
    pitch_counter = meter.create_counter("aan_pitches_generated")
    rejection_gauge = meter.create_gauge("aan_judge_rejection_rate")
    
    # In each agent:
    pitch_counter.add(1)
    rejection_gauge.set(rejection_count / total_submissions)
    ```
  - Success: Metrics appear in Application Insights
  - Time estimate: 1 day

- [ ] **Power BI Dashboard (Final)**
  - Task: Comprehensive operations dashboard
  - Owner: Data Engineer (Observability)
  - Panels:
    1. **Health Status** (Scout, Prof, Scribe, Judge, Pixel, Ops)
    2. **Daily KPIs** (Pitches, approval rate, rejection rate)
    3. **Performance** (Latencies p50/p95/p99)
    4. **Cost Breakdown** (by model, API, infrastructure)
    5. **Error Patterns** (rejection reasons, API failures, timeouts)
    6. **Trends** (7-day rolling)
  - Success: Dashboard deployed; real-time data
  - Time estimate: 2 days

- [ ] **Alert Rules + Runbooks**
  - Task: Configure production alerts
  - Owner: Data Engineer (Observability)
  - Alerts:
    - Scout offline (no pitches for 45 min)
    - Judge rejection rate > 20%
    - Time-to-publish > 4 hours
    - Cost spike (>$8 per article)
    - DLQ backlog > 5 items
    - Any API circuit breaker open
  - Runbooks:
    - Scout offline → Restart + use cache
    - High rejections → Review rulebook
    - Cost spike → Check model usage
  - Success: Alerts tested; runbooks validated
  - Time estimate: 1.5 days

- [ ] **Incident Response Setup**
  - Task: On-call rotation, escalation policies, PIR templates
  - Owner: DevOps
  - Setup:
    - PagerDuty integration
    - Slack alerts
    - Severity levels + SLAs
    - PIR template adopted
  - Success: On-call rotation live
  - Time estimate: 1 day

### 3.4 Load & Chaos Testing

**Week 6, Days 2-3:**

- [ ] **Load Testing (10K calls/day simulation)**
  - Task: Simulate full production load
  - Owner: Backend Engineer #6
  - Test:
    - 15-min Scout runs → 672 cycles per week
    - Average 100 prof/scribe calls per day
    - Peak hour: 5x normal load (lunch time spike)
    - Measure: latencies, error rates, cost
  - Tool: Apache JMeter or custom Python script
  - Success: System stable under 10x nominal load; <2% error rate
  - Time estimate: 1.5 days (test + analysis)

- [ ] **Chaos Engineering (Production Resilience)**
  - Task: Intentional failure injection
  - Owner: Backend Engineer #6
  - Scenarios:
    1. Scout API timeout → Verify fallback to cache
    2. Cosmos DB latency spike → System self-heals
    3. Judge model quota exhausted → Queue requests
    4. GitHub API 503 → Retry + DLQ
    5. Network partition → Services recover automatically
    6. Foundry agent crash → Auto-restart + resume from checkpoint
  - Tool: Gremlin or custom fault injection
  - Success: System recovers from all failures; no data loss
  - Time estimate: 1.5 days

### 3.5 Production Hardening

**Week 6, Days 4-5:**

- [ ] **Security Audit**
  - Task: Review authentication, encryption, data handling
  - Owner: Cloud Architect (Security Lead)
  - Checklist:
    - [ ] All APIs authenticated (Managed Identity or keys from Key Vault)
    - [ ] All data encrypted in transit (TLS 1.3) and at rest
    - [ ] RBAC roles follow least privilege
    - [ ] No secrets in logs or code
    - [ ] Foundry agents run with limited permissions
    - [ ] Network isolated (VNet + private endpoints)
    - [ ] Audit logging enabled
  - Success: Security audit passed
  - Time estimate: 1.5 days

- [ ] **Compliance Review**
  - Task: Data privacy, retention, compliance
  - Owner: Legal + Data Engineer
  - Checks:
    - [ ] GDPR compliance (data retention, right to delete)
    - [ ] Content safety policies enforced
    - [ ] Audit trail complete (who/what/when)
    - [ ] Data classification (public vs. internal)
  - Success: Compliance requirements met
  - Time estimate: 1 day

- [ ] **Documentation & Knowledge Transfer**
  - Task: Finalize runbooks, architecture diagrams, troubleshooting guides
  - Owner: All engineers (rotating)
  - Deliverables:
    - Runbook handbook (PDF + wiki)
    - Architecture diagram (Lucid)
    - Troubleshooting guide (step-by-step)
    - Agent code comments + doc strings
  - Success: Team can operate system without external help
  - Time estimate: 2 days

### 3.6 Phase 3 Success Criteria

✅ **Branded Media:**
- Pixel generates high-quality images for every story
- Logo, fonts, brand colors consistent
- Image QA passes >95%

✅ **Publishing:**
- Ops commits to GitHub → Static Web Apps builds → Preview URL
- Editor approval → Main merge → Live site updates
- Social media posts automatically

✅ **Full Observability:**
- Power BI dashboard with all KPIs (real-time)
- Foundry traces capture every decision point
- Alerts trigger correctly; runbooks effective

✅ **Load & Resilience:**
- System stable under 10x load
- All chaos tests: graceful degradation
- Zero data loss under any failure

✅ **Production Ready:**
- Security audit passed
- Compliance requirements met
- Team trained + runbooks documented

**Phase 3 Go/No-Go Gate:** Approve Phase 4 (hardening) + GA readiness

---

## Phase 4: Production GA Readiness (Week 7)

**Duration:** 1 week  
**Team:** All (final cross-check)  
**Goal:** Live system, fully monitored, ready for 24/7 operation

### 4.1 Final Validation Checklist

- [ ] All 6 agents deployed + operational
- [ ] End-to-end workflow tested (5+ real stories)
- [ ] Dashboards + alerts live + validated
- [ ] Cost tracking accurate (Phase 0-3: ~$1,200-1,400/month total)
- [ ] Security + compliance audit passed  

- [ ] On-call rotation established + tested
- [ ] Runbooks documented + team trained
- [ ] Disaster recovery tested (BCDR)
- [ ] Backup/restore procedure validated

### 4.2 Soft Launch (Days 1-4)

- [ ] Deploy to full production
- [ ] Limit to 1 editor initially (controlled)
- [ ] Monitor closely for 48 hours
- [ ] Fix critical issues (if any)
- [ ] Expand to full editorial team (Days 3-4)

### 4.3 Official GA Launch (Day 5)

- [ ] Announce to stakeholders
- [ ] Training for editors
- [ ] Publish "AAN v3.0 Go-Live" blog post
- [ ] Celebrate! 🎉

---

## Budget Summary

| Phase | AWS/Azure Services | Labor (Engineer-Days) | Total Cost |
|-------|-------------------|---------------------|-----------|
| Phase 0 | $700 | 8 | $12,000 |
| Phase 1 | $950 | 12 | $18,000 |
| Phase 2 | $1,200 | 16 | $24,000 |
| Phase 3 | $1,400 | 14 | $21,000 |
| Phase 4 | $1,400 | 4 | $6,000 |
| **TOTAL** | — | **54 engineer-days** | **$81,000** |

**Ongoing (per month):** $1,400 infrastructure + $12,000 labor (0.5 FTE)

---

## Success Criteria by Phase

| Criteria | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|----------|---------|---------|---------|---------|---------|
| **Infrastructure** | ✅ Deployed | ✅ | ✅ | ✅ | ✅ |
| **Scout** | — | ✅ 15-20 pitches/day | ✅ | ✅ | ✅ |
| **Judge** | — | ✅ >95% accuracy | ✅ | ✅ | ✅ |
| **Prof** | — | — | ✅ Research API | ✅ | ✅ |
| **Scribe** | — | — | ✅ Draft generation | ✅ | ✅ |
| **Pixel** | — | — | — | ✅ Branded images | ✅ |
| **Ops** | — | — | — | ✅ GitOps pipeline | ✅ |
| **End-to-End** | — | — | ✅ <3h publish | ✅ | ✅ |
| **Monitoring** | — | — | ✅ Basic | ✅ Full dashboards | ✅ |
| **Resilience** | — | — | ✅ Basic | ✅ Chaos tested | ✅ |
| **Go-Live** | — | — | — | ✅ Ready | ✅ **LIVE** |

---

**Document Version:** 1.0  
**Last Updated:** February 14, 2026  
**Status:** Ready for immediate execution ✅  
**Next Step:** Kickoff Phase 0 (Infrastructure Bootstrap)
