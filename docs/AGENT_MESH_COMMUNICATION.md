# Agent Mesh & Communication Patterns

**Document Version:** 1.0  
**Date:** February 14, 2026  
**Purpose:** Deep dive into agent-to-agent communication, routing logic, and feedback loops

---

## 1. Agent Mesh Topology

### 1.1 Mesh vs. Linear Architecture

**Linear (Original Gen 2):**
```
Scout → Prof → Scribe → Judge → Pixel → Ops
```
Problems:
- One agent failure → entire pipeline halts
- No feedback loops or conditional routing
- Inefficient (all agents run even if earlier stages filtered)

**Mesh (Gen 3 — This System):**
```
Scout ←→ Prof ←→ Scribe ←→ Judge → Pixel
  ↑       ↑        ↑        ↓       ↓
  └─ Foundry Orchestrator (routes messages, handles retries)
  └─ Fallback paths & escalation to Editor (DLQ)
```

Advantages:
- Agents can communicate bidirectionally
- Conditional routing based on outcomes
- Fallback chains where needed
- Feedback loops for iteration

---

## 2. Message Flow Definitions

### 2.1 Scout → Prof: "Research Request"

```json
{
  "message_type": "research_request",
  "pitch_id": "story_2026_02_14_001",
  "headline": "OpenAI releases multi-modal model",
  "summary": "New vision + text model rivals competitors",
  "source_urls": [
    "https://openai.com/blog/...",
    "https://techcrunch.com/...",
    "https://reddit.com/r/MachineLearning/..."
  ],
  "relevance_score": 8.7,
  "detected_keywords": ["AI", "OpenAI", "Vision", "Model"],
  "confidence": 0.92,
  "brand_sensitivities": [
    "Avoid disparaging Anthropic/Claude",
    "Acknowledge our past predictions on this topic"
  ]
}
```

**Route Logic (Foundry):**
```
if relevance_score > 8.0 and confidence > 0.85:
  SEND to Prof
elif relevance_score > 6.0:
  SEND to Prof with note: "Low confidence — double-check research"
else:
  DISCARD (store in analytics for trend tracking)
```

---

### 2.2 Prof → Scout: "Rescan Request" (Feedback Loop)

```json
{
  "message_type": "rescan_request",
  "original_pitch_id": "story_2026_02_14_001",
  "reason": "insufficient_corroboration",
  "search_params": {
    "keywords": ["OpenAI Vision model benchmark comparison"],
    "date_range": "last_6_hours",
    "sources": ["arxiv.org", "github.com", "academic"]
  },
  "urgency": "high"
}
```

**Scout's Response Logic:**
```
1. Rescan with specified keywords (priority over regular sweep)
2. Return TOP-2 matching stories (within 15 min)
3. Send message: "Rescan complete — found {N} matching stories"
4. If still insufficient:
   - Prof proceeds with lower confidence
   - Stores confidence level in metadata
   - Judge may flag for Editor review
```

---

### 2.3 Prof → Scribe: "Research Brief"

```json
{
  "message_type": "research_brief",
  "pitch_id": "story_2026_02_14_001",
  "key_facts": [
    {
      "fact": "Model shows 15% improvement in visual understanding",
      "sources": ["OpenAI blog", "OpenAI technical paper"],
      "confidence": 0.99
    },
    {
      "fact": "Released February 13, 2026",
      "sources": ["OpenAI announcement"],
      "confidence": 1.0
    }
  ],
  "counterarguments": [
    "Model not yet widely tested in production"
  ],
  "competitor_mentions": [
    {
      "company": "Anthropic",
      "sentiment": "neutral",
      "caution": "Avoid disparaging their Claude vision model"
    }
  ],
  "brand_alignment_score": 0.94,
  "suggested_angle": "Technical advancement; position our expertise in this space",
  "research_confidence": 0.91
}
```

---

### 2.4 Scribe → Judge: "Draft Submission"

```json
{
  "message_type": "draft_submission",
  "pitch_id": "story_2026_02_14_001",
  "iteration_number": 1,
  "draft_content": "# OpenAI Releases Multimodal Model\n\nOpenAI announced...",
  "tone": "technical_blog",
  "metadata": {
    "word_count": 850,
    "readability_score": 8.2,
    "keywords": ["AI", "Vision", "OpenAI"]
  }
}
```

---

### 2.5 Judge → Scribe: "Rejection with Feedback" (Feedback Loop)

```json
{
  "message_type": "rejection_feedback",
  "pitch_id": "story_2026_02_14_001",
  "iteration_number": 1,
  "rejection_reasons": [
    {
      "type": "absolute_claim",
      "severity": "high",
      "location": "paragraph 2, sentence 3",
      "original_text": "This model will eliminate the need for human review",
      "feedback": "Remove absolute claim. Replace with: 'may reduce reliance on human review'",
      "matched_rule": "No absolute claims (bug-free, guaranteed, always)",
      "rule_confidence": 0.99
    }
  ],
  "passed_checks": [
    "Brand tone consistency",
    "Competitor sensitivity",
    "Factual corroboration (per Prof research)"
  ],
  "overall_pass": false,
  "retry_count": 1,
  "max_retries": 3,
  "next_action": "RETURN_TO_SCRIBE_FOR_REVISION"
}
```

---

### 2.6 Scribe → Judge: "Revised Draft" (2nd Iteration)

(Same as 2.4, but `iteration_number: 2`)

**Judge's Logic:**
```
if iteration 1 failed on: absolute_claim
  and iteration 2 revised that specific clause:
    RECHECK semantic similarity to brand rules
    if confidence > 0.95:
      PASS
    else:
      RETURN rejection with updated feedback
else if iteration >= 3:
  FAIL (escalate to Editor)
  STORE in DLQ with context
```

---

### 2.7 Judge → Ops: "Publication Ready" (Success Path)

```json
{
  "message_type": "publication_ready",
  "pitch_id": "story_2026_02_14_001",
  "markdown_content": "# OpenAI Releases Multimodal Model\n\n...",
  "metadata": {
    "headline": "OpenAI Releases Multimodal Model",
    "slug": "openai-releases-multimodal-model",
    "date": "2026-02-14",
    "author": "Azure Autonomous Newsroom",
    "tags": ["AI", "OpenAI", "Vision"]
  },
  "qa_checks_passed": [
    "brand_alignment",
    "factual_accuracy",
    "tone_consistency",
    "competitor_sensitivity"
  ]
}
```

---

### 2.8 Ops ← Pixel: "Image Asset Ready" (Parallel Execution)

```json
{
  "message_type": "image_asset_ready",
  "pitch_id": "story_2026_02_14_001",
  "image_url": "https://blob.azure.com/newsroom/images/2026-02-14-001.jpg",
  "image_metadata": {
    "width": 1200,
    "height": 630,
    "format": "JPEG",
    "size_kb": 150,
    "quality_check_passed": true,
    "quality_score": 0.97
  }
}
```

---

## 3. Conditional Routing Rules (Foundry Orchestrator)

### 3.1 Decision Tree: Scout → Prof

```yaml
decision_point: Scout_sends_pitch
conditions:
  - if: relevance_score >= 8.0 AND confidence >= 0.85
    then: ROUTE_TO_Prof
    label: "High confidence pitch"
  
  - if: relevance_score >= 6.0 AND confidence < 0.85
    then: ROUTE_TO_Prof
    metadata:
      note: "Lower confidence — double-check research"
      flag_for_editor: false
  
  - if: relevance_score < 6.0
    then: STORE_IN_ANALYTICS
    label: "Below threshold — trend tracking only"
    do_not_pitch: true
```

### 3.2 Decision Tree: Prof → Scribe or Scout (Rescan)

```yaml
decision_point: Prof_research_complete
conditions:
  - if: corroboration_level >= 0.90 AND fact_check_passed
    then: ROUTE_TO_Scribe
    attach: research_brief
  
  - if: corroboration_level < 0.70
    then: ROUTE_BACK_TO_Scout
    message_type: "rescan_request"
    wait_time_sec: 600  # 10 minutes for rescan
    on_timeout: "ROUTE_TO_Scribe_with_low_confidence_flag"
  
  - if: brand_sensitivity_high AND competitor_mentioned_negatively
    then: FLAG_FOR_EDITOR
    action: "send_teams_alert"
    route_to: "Editor approval queue"
```

### 3.3 Decision Tree: Scribe → Judge → Iterate or Escalate

```yaml
decision_point: Scribe_submits_draft
conditions:
  - label: "First submission"
    submission_number: 1
    then: ROUTE_TO_Judge
    
  - label: "Judge rejected; attempt revision"
    submission_number: 2
    prior_status: "REJECTED_BY_JUDGE"
    then: ROUTE_TO_Judge
    
  - label: "Judge rejected twice; final attempt"
    submission_number: 3
    prior_status: "REJECTED_BY_JUDGE"
    then: ROUTE_TO_Judge
    metadata:
      critical_message: "Last attempt before escalation"
    
  - label: "All retries exhausted"
    submission_number: 4
    prior_status: "REJECTED_BY_JUDGE"
    then: ESCALATE_TO_DLQ
    action:
      - "store in dead letter queue"
      - "send daily digest to Editor"
      - "capture rejection pattern for analysis"
```

### 3.4 Decision Tree: Judge → Ops + Pixel (Parallel) or Scribe (Iterate)

```yaml
decision_point: Judge_compliance_check
conditions:
  - if: all_checks_passed == true
    then: 
      - ROUTE_TO_Pixel (parallel)
      - ROUTE_TO_Ops (parallel)
    wait_for: "both_agents_complete"
    timeout_sec: 300  # 5 min, Pixel can timeout
  
  - if: failed_checks > 0 AND iteration_count < 3
    then: ROUTE_BACK_TO_Scribe
    attach: rejection_feedback
    
  - if: failed_checks > 0 AND iteration_count >= 3
    then: ESCALATE_TO_DLQ
    reason: "Max retries exceeded"
```

---

## 4. Error Handling & Retry Logic

### 4.1 Retry Policies by Agent

| Agent | Max Retries | Backoff Strategy | On Final Failure |
|-------|------------|------------------|-----------------|
| **Scout** (external APIs) | 3 | Exponential (1s, 2s, 4s) | Use cached headlines; alert Editor |
| **Prof** (external APIs) | 2 | Linear (2s, 4s) | Proceed with lower confidence; flag |
| **Scribe** (LLM generation) | 1 per iteration | N/A (iteration is explicit) | Return to Scribe (iteration loop) |
| **Judge** (compliance check) | 0 | N/A (decision is final) | Escalate rejection or pass |
| **Pixel** (DALL-E 3) | 2 | Linear (5s, 10s) | Publish without image; log alert |
| **Ops** (GitHub + publish) | 3 | Exponential (2s, 4s, 8s) | DLQ + manual intervention |

### 4.2 Timeout Handling

```yaml
timeout_policies:
  
  scout_ingest:
    timeout_sec: 45
    on_timeout: "discard_partial_data; fall_back_to_cache"
  
  prof_research:
    timeout_sec: 120
    on_timeout: "return_partial_research; flag_confidence_low"
  
  scribe_generation:
    timeout_sec: 60
    on_timeout: "retry_once; then_escalate"
    
  judge_check:
    timeout_sec: 30  # Should be fast
    on_timeout: "treat_as_PASS_with_warning"  # Don't block publication
    
  pixel_image_gen:
    timeout_sec: 120
    on_timeout: "abandon_image; use_default_brand_image"
    on_final_timeout: "publish_without_image"
    
  ops_publish:
    timeout_sec: 60
    on_timeout: "retry_with_backoff"
```

---

## 5. Feedback Loop: Judge's Learning

### 5.1 Rejection Pattern Collection

**Judge stores every rejection in Cosmos DB:**

```json
{
  "id": "judge_rejection_20260214_001",
  "pitch_id": "story_2026_02_14_001",
  "timestamp": "2026-02-14T10:45:30Z",
  "rejection_type": "absolute_claim",
  "rejected_text": "This model will eliminate the need for human review",
  "rule_violated": "No absolute claims (bug-free, guaranteed, always)",
  "rule_id": "brand_rule_005",
  "vector_embedding": [0.12, 0.45, 0.67, ...],  // Semantic embedding
  "scribe_response": "ACCEPTED_FEEDBACK_ON_RETRY_2",
  "final_outcome": "PASSED_AFTER_REVISION"
}
```

### 5.2 Weekly Rulebook Update Pipeline

**Process (automated, runs weekly):**

```
1. Query Cosmos DB: "All rejections from past 7 days"

2. Cluster rejections by type (semantic similarity):
   - "Absolute claims" cluster: 12 instances
   - "Competitor disparagement" cluster: 3 instances
   - "Tone inconsistency" cluster: 5 instances

3. For each cluster with >5 instances:
   - Extract common pattern
   - Generate updated rule text
   - Compute new vector embedding
   - Update Azure AI Search index

4. Example transformation:
   OLD RULE:
     "Avoid absolute claims"
   
   NEW RULE (data-driven):
     "Avoid absolute claims like 'will eliminate', 'bug-free', 'always', 
      'guaranteed', 'impossible to defeat'. Use instead: 'may reduce', 
      'aims to improve', 'generally', 'designed to', 'typically'."

5. Update Judge's system prompt with refined rules

6. Send weekly digest to Editor:
   "5 new rejection patterns detected. Rulebook updated."
```

---

## 6. Escalation Paths

### 6.1 Editor Escalation Triggers

```yaml
escalation_triggers:
  
  scout_filter_rate:
    condition: "< 2 pitches per 15 min"
    action: "Alert Editor: 'Scout found minimal stories'"
    context: "May indicate news drought or API issue"
  
  judge_rejection_spike:
    condition: "rejection_rate > 15% in past 24h"
    action: "Alert Editor: 'Judge rejecting too many drafts'"
    context: "May indicate rulebook too strict OR Scribe quality degrading"
  
  scribe_max_retries:
    condition: "Scribe fails Judge 3x on same draft"
    action: "Send to DLQ + Alert Editor"
    context: "Manual intervention needed; add to daily digest"
  
  prof_low_confidence:
    condition: "Prof research confidence < 0.70"
    action: "Flag pitch with note: 'Research uncertain'"
    context: "Editor can decide: proceed at risk or discard"
  
  pixel_generation_fail:
    condition: "DALL-E fails after 2 retries"
    action: "Allow Ops to publish without image; notify Editor"
    context: "Image-less article is acceptable"
  
  ops_publish_fail:
    condition: "GitHub API fails after 3 retries"
    action: "Add to DLQ + Alert Editor"
    context: "Manual push to GitHub may be needed"
```

### 6.2 Dead Letter Queue (DLQ) Processing

**Daily Digest Email (9 AM):**

```
Subject: AAN Dead Letter Queue Summary — {Date}

Failed Stories: 3

1. Story ID: story_2026_02_13_042
   Failure Point: Judge rejection (iteration 3)
   Reason: Absolute claim not resolved ("will guarantee performance")
   Action Needed: Editor must either:
     a) Manually fix draft + republish
     b) Mark as rejected
     c) Change angle

2. Story ID: story_2026_02_13_051
   Failure Point: Ops publish (GitHub API timeout)
   Reason: GitHub API rate limit exceeded
   Action Needed: Retry publish when rate limit resets (2 PM UTC)

3. Story ID: story_2026_02_13_067
   Failure Point: Prof research (corroboration < 0.70)
   Reason: Insufficient sources found for claim
   Action Needed: Scout rescan with different keywords, OR discard

---

Trends (Past 7 Days):
- Judge rejection rate: 8.3% (target: < 10%) ✅
- Ops publish failure rate: 2.1% (target: < 1%) ⚠️
- Avg time-to-publish: 2.4 hours ✅
```

---

## 7. Message Ordering & Concurrency

### 7.1 Sequential vs. Parallel Stages

```
SEQUENTIAL (must complete in order):
  Scout → (Editor approval) → Prof → Scribe → Judge

PARALLEL (can run simultaneously):
  Judge completes + sends messages to:
    ├─ Pixel (image generation)
    ├─ Ops (GitHub commit)
    └─ (wait for both to complete before publishing)

CONDITIONAL SEQUENTIAL:
  Prof research insufficient?
    → Send rescan to Scout
    → Wait for Scout response (timeout: 10 min)
    → Continue to Scribe
```

### 7.2 Conversation Threading (Foundry)

**All agent messages belong to a single conversation thread per pitch:**

```
Thread ID: conv_story_2026_02_14_001

Message 1: Scout → "Here's your pitch"
Message 2: Editor (human) → "Approved"
Message 3: Prof → "Research brief ready"
Message 4: Scribe → "Draft v1 ready"
Message 5: Judge → "Rejected - fix absolute claim"
Message 6: Scribe → "Draft v2 ready"
Message 7: Judge → "Passed"
Message 8: Pixel → "Image ready"
Message 9: Ops → "Published to prod"

→ Full audit trail in single conversation
→ Easy to replay, debug, or review
```

---

## 8. Example: Full Story Lifecycle

### Scenario: "OpenAI Vision Model" Story

**T+00:00 — Scout Detects**
```
Scout runs 15-min sweep
↓
Finds: "OpenAI releases vision model" in 23 sources
Relevance Score: 8.7 (high interest keywords)
Confidence: 0.92
→ Sends Teams Pitch Card to Editor
```

**T+00:15 — Editor Approves**
```
Editor clicks: ✅ Approve & Publish
→ Foundry routes to Prof
```

**T+00:15 — Prof Researches**
```
Prof searches Azure AI Search for:
  - Past coverage on OpenAI announcements
  - Competitor mentions (Anthropic)
  - Technical details from arxiv

Finds:
  - 15 high-credibility sources
  - Corroboration level: 0.94

Sends research brief to Scribe
```

**T+00:35 — Scribe Drafts**
```
Scribe receives research brief
Writes: 850-word article in "technical_blog" tone
Draft includes:
  - Headline: "OpenAI Advances in Multimodal AI"
  - 5 sections (What, Why, Impact, etc.)
  - Sources appendix

Sends draft v1 to Judge
```

**T+00:45 — Judge Reviews v1**
```
Judge runs semantic checks:
  ✓ Tone consistency: PASS
  ✓ Factual corroboration: PASS (per Prof)
  ✗ Absolute claims: FAIL
    - Found: "will eliminate human review"
    - Rule: "No absolute claims"
    - Feedback: Soften to "may reduce"

Sends rejection with specific feedback to Scribe
```

**T+00:50 — Scribe Revises (Iteration 2)**
```
Scribe receives feedback
Updates sentence: "may reduce reliance on human review"
Sends draft v2 to Judge
```

**T+00:55 — Judge Reviews v2**
```
Judge re-checks the problematic sentence
Semantic similarity to "no absolute claims" rule: 0.88 (pass)
All other checks: PASS

→ Sends APPROVAL message (and simultaneously to Pixel + Ops)
```

**T+01:00 — Pixel Generates Image + Ops Publishes**

```
PIXEL:
  1. Prompts DALL-E: "Modern, professional image about AI advancement"
  2. Receives image from DALL-E
  3. Post-processes: gradient overlay, headline text, logo stamp
  4. Sends image URL to Ops

OPS (parallel):
  1. Commits Markdown to GitHub (drafts branch)
  2. Triggers Static Web Apps build
  3. Preview URL: peaceful-sand-xyz.azurestaticapps.net
  4. Sends Teams card: "Preview Ready — [Preview] [Publish] [Reject]"
```

**T+01:05 — Editor Final Review**
```
Editor clicks preview link
- Reviews article on preview site
- Checks image quality
- Clicks: ✅ Publish to Production
```

**T+01:06 — Merge & Publish**
```
Ops merges drafts → main branch
GitHub Actions triggers production build
Article goes live on newsroom.company.com
Social media posts triggered via Logic Apps
```

**T+01:10 — Logging & Analytics**
```
Cosmos DB logs:
  - Pitch ID, relevance score, editor approval time
  - Prof confidence (0.94)
  - Scribe iterations (1 revision)
  - Judge rejections (1, then pass)
  - Time-to-publish: 70 minutes
  - Tokens used: GPT-4o (2,150 input + 890 output), GPT-4o-mini (80 input)
  - Cost: $0.32
  - Image URL + generation cost: $0.10

Application Insights updated:
  - Daily pitch count: +1
  - Daily approval rate: 66% (2/3)
  - Judge rejection rate: 33% (on Scribe submissions)
  - Avg time-to-publish: 75 min
```

---

## 9. Foundry Configuration (YAML Example)

```yaml
agents:
  scout:
    type: "connected_agent"
    model: "gpt-4o-mini"
    instructions: |
      You are Scout, the Watchdog. Your job is to:
      1. Ingest 500+ headlines from news/social feeds
      2. Filter for relevance to our audience
      3. Calculate a Relevance Score (0-10)
      4. Generate story pitches
    tools:
      - bing_news_api
      - cosmos_db_read
    max_retries: 3
    timeout_sec: 45
  
  prof:
    type: "connected_agent"
    model: "gpt-4o"
    instructions: |
      You are Prof, the Researcher. Your job is to:
      1. Deep-dive on approved pitches
      2. Gather corroborating evidence
      3. Identify brand sensitivities
      4. Can request Scout to rescan
    tools:
      - bing_search_v7
      - azure_ai_search_vector
      - cosmos_db_read
    communication:
      can_send_to: ["scout", "scribe"]
      can_receive_from: ["scout", "editor", "orchest
rator"]
    max_retries: 2
    timeout_sec: 120
  
  scribe:
    type: "connected_agent"
    model: "gpt-4o"
    instructions: |
      You are Scribe, the Writer. Your job is to:
      1. Draft markdown articles
      2. Adapt tone per editor preferences
      3. Learn from Judge's feedback
      4. Iterate up to 3 times
    tools:
      - gpt_4o_write
      - file_system_local
      - cosmos_db_write
    communication:
      can_send_to: ["judge"]
      can_receive_from: ["prof", "judge", "orchestrator"]
    max_retries: 0  # Iteration is explicit, not retry
    timeout_sec: 60
  
  judge:
    type: "connected_agent"
    model: "gpt-4o-mini"
    instructions: |
      You are Judge, the Critic. Your job is to:
      1. Validate brand alignment
      2. Check for hallucinations
      3. Enforce compliance rules
      4. Provide specific feedback
    tools:
      - azure_content_safety
      - azure_ai_search_vector  # Brand rules lookup
      - cosmos_db_write  # Log rejections
    communication:
      can_send_to: ["scribe", "pixel", "ops"]
      can_receive_from: ["scribe", "orchestrator"]
    max_retries: 0  # Judge decision is final
    timeout_sec: 30
  
  pixel:
    type: "connected_agent"
    model: null  # No LLM; tool-driven
    instructions: |
      You are Pixel, the Media Lead. Your job is to:
      1. Generate branded images (DALL-E 3)
      2. Post-process with logo/fonts
      3. QA with vision model
    tools:
      - dall_e_3_generate
      - python_pil_processing
      - claude_vision_qa
      - azure_blob_upload
    communication:
      can_send_to: ["ops"]
      can_receive_from: ["judge", "orchestrator"]
    max_retries: 2
    timeout_sec: 120
  
  ops:
    type: "connected_agent"
    model: null  # No LLM; tool-driven
    instructions: |
      You are Ops, the Publisher. Your job is to:
      1. Commit to GitHub (drafts branch)
      2. Monitor build + preview URL
      3. Merge to main (on editor approval)
      4. Trigger social media posts
    tools:
      - github_api
      - static_web_apps_api
      - azure_logic_apps
      - service_bus_dlq
    communication:
      can_send_to: ["dui_teams", "service_bus"]
      can_receive_from: ["judge", "pixel", "orchestrator"]
    max_retries: 3
    timeout_sec: 60

orchestrator:
  service: "foundry_agent_service"
  routing_strategy: "conditional_mesh"
  
  workflows:
    - name: "story_pitch"
      trigger: "scout_ready"
      steps:
        - agent: "scout"
          on_complete: "send_teams_card"
        - wait_for: "editor_approval"
        - conditional:
            - if: "approved"
              then: "route_to_prof, route_to_dui"
            - if: "low_confidence_rescan_needed"  
              then: "message_scout_rescan"
            - if: "rejected"
              then: "store_in_analytics"
    
    - name: "content_generation"
      trigger: "prof_complete"
      steps:
        - agent: "scribe"
        - wait_for: "judge_review"
        - conditional:
            - if: "judge_pass"
              then: "route_to_pixel, route_to_ops"
              wait_for: "both_complete"
            - if: "judge_fail"
              then: "check_iteration_count"
              - if: "iteration < 3"
                then: "route_back_to_scribe"
              - if: "iteration >= 3"
                then: "escalate_to_dlq"
  
  observability:
    traces: true
    logging_level: "INFO"
    metrics: ["token_usage", "latency", "error_rate"]
    app_insights: true
```

---

**Document Version:** 1.0  
**Last Updated:** February 14, 2026  
**Status:** Ready for Foundry Implementation ✅
