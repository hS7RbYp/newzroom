# Memory Architecture: 3-Tier System

**Document Version:** 1.0  
**Date:** February 14, 2026  
**Purpose:** Detailed specification of immediate, working, and long-term memory layers

---

## 1. Overview: Why 3 Tiers?

**Problem with Single Memory Pool:**
- Storing every agent interaction in one place → bloated indexes
- Agent can't quickly retrieve "recent decisions" vs. "patterns over time"
- Vector embeddings expensive at scale; need selective embedding
- Retention policies conflicting (e.g., cache headlines 24h but archive brand rules forever)

**Solution: Layered Memory**

| Tier | Purpose | Storage | TTL | Query Pattern | Size |
|------|---------|---------|-----|---------------|------|
| **Immediate** | Real-time task state | Agent Thread (Foundry) | 1-2 hours | Fast, in-context | ~50 KB/pitch |
| **Working** | Recent history & decisions | Cosmos DB | 30 days | SQL query (agent history, editor decisions) | ~500 GB |
| **Long-term** | Semantic knowledge & rules | AI Search (Vector) | Permanent | Semantic search (brand rules, patterns) | ~50 GB vectors |

---

## 2. Tier 1: Immediate (Agent Thread Memory)

### 2.1 What It Stores

The **conversation thread** for a single pitch, managed by Foundry Agent Service.

**Example Thread: `conv_story_2026_02_14_openai_vision`**

```
Message 1 [10:00:00] Scout → Orchestrator
  Type: pitch_ready
  Payload: {headline, summary, relevance_score, URLs...}

Message 2 [10:05:00] Orchestrator → Editor (Teams)
  Type: pitch_card_rendered
  Action buttons: [✅ Approve] [🔄 Research] [❌ Skip]

Message 3 [10:12:00] Editor → Orchestrator
  Type: human_approval
  Action: APPROVED
  Note: "Great angle on this"

Message 4 [10:12:30] Orchestrator → Prof
  Type: route_message
  Content: pitch_details + research_request

Message 5 [10:35:00] Prof → Orchestrator
  Type: research_brief_ready
  Payload: {facts, sources, confidence_score...}

Message 6 [10:35:15] Orchestrator → Scribe
  Type: route_message
  Content: research_brief + writing_instructions

Message 7 [10:50:00] Scribe → Orchestrator
  Type: draft_ready
  Payload: {markdown_content, word_count, tone...}

Message 8 [10:51:00] Orchestrator → Judge
  Type: compliance_check_request
  Content: markdown_content

Message 9 [10:52:00] Judge → Orchestrator
  Type: compliance_result
  Status: REJECTED
  Reason: absolute_claim_in_para_2
  Feedback: "Replace 'will guarantee' with 'aims to'"

Message 10 [10:53:00] Orchestrator → Scribe
  Type: revision_request
  Content: Judge's feedback

... (continues until passage or escalation)
```

### 2.2 Characteristics

- **Scope:** Single pitch lifecycle (from Scout detection to publication or DLQ)
- **Lifetime:** Active until story published or moved to DLQ (~2-4 hours typical)
- **Access:** Only relevant agents in the thread
- **Immutability:** Once message sent, cannot be edited (audit trail)
- **Queries:** "Show me all messages from this pitch" → O(1) lookup by thread ID

### 2.3 Foundry Thread API

```python
# Pseudo-code: Foundry SDK
from foundry import AgentThread

# Create thread for a new pitch
thread = client.threads.create(
    metadata={
        "pitch_id": "story_2026_02_14_001",
        "headline": "OpenAI Releases Vision Model",
        "topic": "AI",
        "created_by": "Scout"
    }
)

# Add messages (agent → orchestrator → agent)
thread.add_message(
    role="agent",  # or "user" for human, "assistant"
    agent_id="scout_001",
    content="Here is story pitch X"
)

# Retrieve all messages (for audit)
messages = thread.get_messages()

# Auto-cleanup after 2 hours (or when story published)
thread.archive()  # Moves to working memory (Cosmos DB)
```

### 2.4 Benefits

✅ **Fast:** Conversation history stays in-memory (Foundry manages)  
✅ **Auditable:** Every message timestamped and immutable  
✅ **Scoped:** Only "active" conversations; old ones archive automatically  
✅ **Token-efficient:** Can include full thread in agent context window without bloat  

---

## 3. Tier 2: Working Memory (Azure Cosmos DB)

### 3.1 Data Schema

**Container: `pitches` (Partitioned by `agent_id` + `date`)**

```json
{
  "id": "story_2026_02_14_001",
  "pk": "agent/scout/2026-02-14",  // Partition key for scaling
  "pitch_id": "story_2026_02_14_001",
  "headline": "OpenAI Releases Multimodal Model",
  "scout_data": {
    "detected_at": "2026-02-14T10:00:00Z",
    "relevance_score": 8.7,
    "confidence": 0.92,
    "sources_count": 23,
    "keywords": ["OpenAI", "AI", "Vision", "Model"],
    "source_urls": [
      "https://openai.com/blog/...",
      "https://techcrunch.com/..."
    ]
  },
  "editor_decision": {
    "action": "APPROVED",
    "timestamp": "2026-02-14T10:12:00Z",
    "note": "Great angle"
  },
  "prof_data": {
    "research_started": "2026-02-14T10:12:30Z",
    "research_completed": "2026-02-14T10:35:00Z",
    "facts": [
      {
        "claim": "Model shows 15% improvement",
        "sources": ["paper_url", "blog_url"],
        "confidence": 0.99
      }
    ],
    "corroboration_level": 0.94,
    "brand_sensitivity_risks": [
      {
        "competitor": "Anthropic",
        "sentiment": "neutral",
        "risk_level": "low"
      }
    ]
  },
  "scribe_iterations": [
    {
      "iteration": 1,
      "draft_start_time": "2026-02-14T10:35:15Z",
      "draft_content": "# OpenAI Releases...",
      "status": "SUBMITTED_TO_JUDGE"
    },
    {
      "iteration": 2,
      "draft_start_time": "2026-02-14T10:53:00Z",
      "draft_content": "# OpenAI Releases...", // Updated version
      "status": "SUBMITTED_TO_JUDGE"
    }
  ],
  "judge_feedback": [
    {
      "iteration": 1,
      "timestamp": "2026-02-14T10:52:00Z",
      "status": "REJECTED",
      "reason": "absolute_claim",
      "location": "para 2, sentence 3",
      "feedback": "Replace 'will guarantee' with 'aims to'",
      "matched_rule_id": "brand_rule_005",
      "rule_text": "No absolute claims"
    },
    {
      "iteration": 2,
      "timestamp": "2026-02-14T10:54:30Z",
      "status": "PASSED",
      "all_checks_passed": [
        "tone_consistency",
        "factual_accuracy",
        "brand_alignment",
        "competitor_sensitivity"
      ]
    }
  ],
  "pixel_data": {
    "image_generation_started": "2026-02-14T10:54:30Z",
    "image_url": "https://blob.azure.com/newsroom/2026-02-14-001.jpg",
    "image_metadata": {
      "dalle_prompt": "Modern professional...",
      "quality_score": 0.97,
      "format": "JPEG",
      "size_kb": 150
    }
  },
  "ops_data": {
    "github_commit_time": "2026-02-14T10:55:00Z",
    "commit_sha": "abc123def456",
    "draft_branch": "draft-story-001",
    "preview_url": "https://peaceful-sand-xyz.azurestaticapps.net",
    "editor_final_approval": {
      "timestamp": "2026-02-14T11:05:00Z",
      "action": "MERGE_TO_MAIN"
    },
    "publish_time": "2026-02-14T11:06:00Z",
    "social_posts": [
      {
        "platform": "twitter",
        "post_id": "1234567890",
        "timestamp": "2026-02-14T11:06:30Z"
      }
    ]
  },
  "metrics": {
    "time_to_publish_sec": 4260,  // 71 minutes
    "scout_to_approval_sec": 720,
    "prof_research_sec": 1350,
    "scribe_iterations": 2,
    "judge_rejections": 1,
    "total_tokens": {
      "gpt_4o": {"input": 2150, "output": 890},
      "gpt_4o_mini": {"input": 380, "output": 120}
    },
    "estimated_cost_usd": 0.42
  },
  "created_at": "2026-02-14T10:00:00Z",
  "updated_at": "2026-02-14T11:06:00Z",
  "ttl": 2592000  // 30 days in seconds; auto-delete after 30 days
}
```

### 3.2 Additional Containers

**Container: `judge_feedback` (Partitioned by `rejection_type`)**
```json
// Stores ALL judge rejections for analysis
{
  "id": "judge_rejection_20260214_001",
  "pk": "rejection/absolute_claim/2026-02-14",
  "pitch_id": "story_2026_02_14_001",
  "rejection_type": "absolute_claim",
  "original_text": "This model will eliminate human review",
  "feedback": "Remove absolute language; use 'may', 'aims', 'typically'",
  "vector_embedding": [0.12, 0.45, 0.67, ...],  // text-embedding-3-small
  "rule_id": "brand_rule_005",
  "iteration_resolved": 2,  // Scribe fixed it on iteration 2
  "outcome": "RESOLVED",
  "timestamp": "2026-02-14T10:52:00Z"
}
```

**Container: `editor_decisions` (Partitioned by `editor_id`)**
```json
// Tracks editor preferences over time
{
  "id": "decision_20260214_001",
  "pk": "editor/jane.doe/2026-02-14",
  "pitch_id": "story_2026_02_14_001",
  "action": "APPROVED",
  "reason": "Great angle on AI competition",
  "topic": "AI",
  "relevance_score": 8.7,
  "timestamp": "2026-02-14T10:12:00Z"
}
```

### 3.3 Queries & Analytics

**Query 1: "Show me all pitches approved by Editor this week"**
```sql
SELECT * FROM pitches
WHERE editor_decision.action = "APPROVED"
  AND editor_decision.timestamp > "2026-02-08T00:00:00Z"
ORDER BY editor_decision.timestamp DESC
```

**Query 2: "What types of stories does Judge reject most?"**
```sql
SELECT judge_feedback[0].reason, COUNT(*) as count
FROM pitches
WHERE judge_feedback[0].status = "REJECTED"
GROUP BY judge_feedback[0].reason
ORDER BY count DESC
```

**Query 3: "Average time-to-publish by topic"**
```sql
SELECT scout_data.keywords[0] as topic,
       AVG(metrics.time_to_publish_sec) as avg_seconds
FROM pitches
WHERE metrics.time_to_publish_sec > 0  // Published only
GROUP BY scout_data.keywords[0]
```

### 3.4 Cost Optimization

**TTL Policy:** 
- Pitches automatically deleted after 30 days
- Cost: ~$0.50 per 1 GB stored
- Expected volume: ~500 GB (1 year of history = 12 × 500 stories/day × 1 MB each)
- Estimated storage cost: ~$250/month

**Indexing Strategy:**
- Composite index: `(agent_id, date, created_at)` for fast range queries
- Single-field index: `pitch_id` for direct lookups
- No-index on: `draft_content`, `judge_feedback.vector_embedding` (too large)

---

## 4. Tier 3: Long-Term Memory (Azure AI Search — Vector Store)

### 4.1 Purpose

**Store semantic knowledge that agents reference repeatedly:**
- Brand voice guidelines (reusable, vector-searchable)
- Past editorial decisions (why stories were approved/rejected)
- Competitor intelligence
- Topic-specific rules (e.g., "financial claims require 2 sources")
- Hallucination patterns (e.g., "claims to fix XYZ without evidence")

### 4.2 Index Structure

**Index: `brand_knowledge`**

```json
{
  "index": "brand_knowledge",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false
    },
    {
      "name": "document_type",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true
      // Values: "brand_voice", "competitor_rule", "financial_rule", etc.
    },
    {
      "name": "rule_text",
      "type": "Edm.String",
      "searchable": true,
      "analyzer": "standard"
    },
    {
      "name": "embedding",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "filterable": false,
      "sortable": false,
      "facetable": false,
      "analyzer": null,
      "dimensions": 1536,  // text-embedding-3-small
      "vectorSearchProfile": "myHnswProfile"
    },
    {
      "name": "examples",
      "type": "Collection(Edm.String)",
      "searchable": true
      // Examples of what this rule means
    },
    {
      "name": "severity",
      "type": "Edm.String",
      "filterable": true
      // "critical", "high", "medium", "low"
    },
    {
      "name": "last_updated",
      "type": "Edm.DateTimeOffset",
      "filterable": true,
      "sortable": true
    },
    {
      "name": "created_from_rejection_count",
      "type": "Edm.Int32"
      // How many Judge rejections created this rule?
    }
  ]
}
```

### 4.3 Sample Documents

**Document 1: Brand Voice Rule**
```json
{
  "id": "brand_rule_005",
  "document_type": "brand_voice",
  "rule_text": "Avoid absolute claims. Use words like 'may', 'aims', 'typically', 'generally', 'designed to' instead of 'will', 'guarantee', 'always', 'impossible'.",
  "embedding": [0.123, 0.456, 0.789, ...],  // Semantic vector
  "examples": [
    "❌ BAD: 'This will eliminate human review'",
    "✅ GOOD: 'This may reduce reliance on human review'",
    "❌ BAD: 'Bug-free software'",
    "✅ GOOD: 'Aims to minimize bugs'"
  ],
  "severity": "critical",
  "last_updated": "2026-02-14T09:00:00Z",
  "created_from_rejection_count": 12
}
```

**Document 2: Competitor Rule**
```json
{
  "id": "brand_rule_comp_001",
  "document_type": "competitor_rule",
  "rule_text": "Anthropic (Claude) is a peer/friend. Never disparage their technology. Acknowledge their innovations. Frame competition as 'everyone pushing AI forward'.",
  "embedding": [0.234, 0.567, 0.890, ...],
  "examples": [
    "❌ BAD: 'Claude is inferior at reasoning'",
    "✅ GOOD: 'Claude excels at long-context reasoning; our model focuses on multi-modal understanding'"
  ],
  "severity": "high",
  "created_from_rejection_count": 3
}
```

**Document 3: Financial Rule**
```json
{
  "id": "brand_rule_fin_002",
  "document_type": "financial_rule",
  "rule_text": "Any financial projections or revenue claims require corroboration from at least 2 independent sources.",
  "embedding": [0.345, 0.678, 0.901, ...],
  "examples": [
    "❌ Single source projections → Rejected",
    "✅ Multi-source corroboration → Approved"
  ],
  "severity": "critical",
  "created_from_rejection_count": 5
}
```

### 4.4 Vector Embedding Pipeline

**Step 1: Draft Brand Rulebook (Markdown)**
```markdown
# Brand Guidelines

## Voice & Tone

### Rule: Avoid Absolute Claims
Never use language that suggests certainty where uncertainty exists:
- Never: "bug-free", "guarantee", "always", "will eliminate"
- Use instead: "may", "aims to", "typically", "designed to"

Example:
- ❌ "This solution eliminates all performance issues"
- ✅ "This solution aims to reduce performance issues by 30-40%"

### Rule: Competitor Respect
Anthropic (Claude) and other labs are doing great work. Frame as:
"Everyone is advancing AI. Our approach focuses on [our difference]."

Example:
- ❌ "Claude is inferior..."
- ✅ "Claude excels at long-context; we focus on multi-modal understanding"
```

**Step 2: Semantic Chunking**
```
Chunk 1:
  "Avoid Absolute Claims: Never use 'bug-free', 'guarantee', 'always'. 
   Use 'may', 'aims to', 'typically'."

Chunk 2:
  "Example rule violation: 'This eliminates all issues' → Instead: 
   'This aims to reduce issues by 30-40%'"

Chunk 3:
  "Competitor Respect: Anthropic is advancing AI. Frame as 'everyone pushing 
   forward' and explain our difference."
```

**Step 3: Embed & Index**
```python
import openai
import azure.search.documents

# For each chunk:
response = openai.Embedding.create(
    input=chunk_text,
    model="text-embedding-3-small",
    dimensions=1536
)
embedding = response['data'][0]['embedding']

# Upload to AI Search
search_client.upload_documents(
    documents=[{
        "id": "brand_rule_005",
        "rule_text": chunk_text,
        "embedding": embedding,
        "severity": "critical"
    }]
)
```

### 4.5 Query: Judge's Semantic Search

**Scenario: Judge receives draft with text "This will guarantee performance improvements"**

```python
# Judge runs semantic search before compliance check
query = "Does this text violate absolute claim rules?"
query_embedding = openai.Embedding.create(
    input=query,
    model="text-embedding-3-small"
)['data'][0]['embedding']

# Search for matching rules
results = search_client.search(
    search_text=query,
    vector_queries=[
        VectorQuery(
            vector=query_embedding,
            k_nearest_neighbors=5,
            fields="embedding"
        )
    ],
    filters="severity eq 'critical'"
)

# Results:
# 1. "Avoid absolute claims..." (similarity: 0.92) ← TOP MATCH
# 2. "Financial rule: 2 sources..." (similarity: 0.45)

# Judge extracts rule #1:
# "Avoid absolute claims. Never use 'guarantee'."
# 
# Compares with draft text: "will guarantee performance improvements"
# Match confidence: 0.95 (FAIL)
# Feedback: "Remove 'guarantee'; use 'aims to' instead"
```

### 4.6 Weekly Auto-Update Mechanism

**Process (runs every Monday 1 AM UTC):**

```python
# 1. Query Cosmos: "All Judge rejections from past 7 days"
rejections = cosmos_db.query(
    "SELECT * FROM judge_feedback WHERE timestamp > DATEADD(day, -7, NOW())"
)

# 2. Cluster rejections by type (semantic similarity)
clusters = sklearn.cluster.AgglomerativeClustering(
    n_samples=len(rejections)
).fit(extract_vectors(rejections))

# 3. For each cluster with > 5 instances:
#    Generate updated rule text
for cluster_id, instances in enumerate(clusters):
    if len(instances) > 5:
        # Extract common pattern
        pattern = extract_pattern(instances)
        
        # Generate new rule text (via GPT-4o)
        new_rule = gpt.create_completion(
            prompt=f"""
            Based on these {len(instances)} rejected examples:
            {format_instances(instances)}
            
            Generate a concise brand rule that would catch these issues.
            """
        )
        
        # Embed new rule
        embedding = embed(new_rule.text)
        
        # Check if similar rule already exists
        existing = search_index.search(
            vector=embedding,
            k=1,
            similarity_threshold=0.85
        )
        
        if existing:
            # Update existing rule
            update_document(existing[0]['id'], {
                "rule_text": new_rule.text,
                "embedding": embedding,
                "created_from_rejection_count": len(instances)
            })
        else:
            # Add new rule
            add_document({
                "id": f"auto_rule_{uuid()}",
                "rule_text": new_rule.text,
                "embedding": embedding,
                "severity": classify_severity(instances),
                "created_from_rejection_count": len(instances)
            })

# 4. Send summary to Editor
send_email(
    to="editor@company.com",
    subject="Weekly Brand Rule Updates",
    body=f"""
    {N_new_rules} new rules auto-detected.
    {N_updated_rules} existing rules refined.
    
    Top rejection patterns:
    - Absolute claims: 8 instances
    - Competitor disparagement: 2 instances
    ...
    """
)
```

---

## 5. Cross-Tier Data Flow

### 5.1 Pitch Lifecycle Memory Usage

```
DAY 0 (Immediate → Working):
  Scout creates thread (immediate)
    ↓
  Editor approves (immediate)
    ↓
  Profile/Scribe iterate (immediate)
    ↓
  Published → Thread archived (Cosmos DB)

DAY 1-30 (Working Memory):
  Query: "Show all AI stories published this week"
  → Reads from Cosmos DB
  
DAY 31+ (Long-Term):
  Pitch details deleted (TTL expired)
  BUT: Judge feedback patterns remain in AI Search
  → Used for future brand rule updates

ALWAYS (Long-Term):
  Brand voice rules → AI Search
  Judge uses semantic search on every draft review
```

### 5.2 Memory Size Estimates

| Tier | Data Type | Size/Item | Volume/Day | Storage |
|------|-----------|-----------|------------|---------|
| Immediate | Thread (2h active) | 500 KB | N/A | Managed by Foundry |
| Working | Cosmos DB (30-day) | 1 MB | 500 pitches | 15 GB |
| Long-term | Vector (rules) | 10 KB | 1-2 new rules | 500 MB |

**Monthly Cost:**
- Foundry threads: ~$100 (included in base)
- Cosmos DB: ~$250
- AI Search: ~$150
- **Total:** ~$500/month

---

## 6. Privacy & Compliance

### 6.1 Data Retention

| Tier | Retention | Reason | Deletion |
|------|-----------|--------|----------|
| Immediate | 2-4 hours | Active session only | Auto-archive to Cosmos |
| Working | 30 days | Recent history for analysis | TTL auto-delete |
| Long-term | Permanent | Brand rules are evergreen | Manual deletion only |

### 6.2 Access Control

**Immediate:** Only agents in thread  
**Working:** Editors + analytics team (via RBAC)  
**Long-term:** Judge agent + data analysts (via Entra ID)

### 6.3 Audit Trail

All tiers maintain immutable logs:
- Who accessed what data
- When it was accessed
- For what purpose
- Stored in Application Insights

---

**Document Version:** 1.0  
**Last Updated:** February 14, 2026  
**Status:** Ready for Implementation ✅
