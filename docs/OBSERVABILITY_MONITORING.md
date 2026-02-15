# Observability & Monitoring Strategy

**Document Version:** 1.0  
**Date:** February 14, 2026  
**Purpose:** Comprehensive observability architecture for production AAN system

---

## 1. Observability Stack

### 1.1 Layers of Observability

```
┌─────────────────────────────────────────┐
│  DASHBOARDS & ALERTS (User Facing)      │
│  (Power BI, Azure Monitor, Teams Bots)  │
└─────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────┐
│  METRICS (Quantitative Data)            │
│  (Pitch count, approval rate, latency)  │
└─────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────┐
│  TRACES (Execution Flow)                │
│  (Agent start→end, tool calls, retries) │
└─────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────┐
│  LOGS (Structured Event Records)        │
│  (JSON, error details, decisions)       │
└─────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────┐
│  COLLECTION LAYER (Agents & Services)   │
│  (Foundry native + custom instrument.)  │
└─────────────────────────────────────────┘
```

### 1.2 Data Destinations

```
Agents/Services
  ├→ Foundry Native Tracing (built-in)
  │   └→ Application Insights
  │       ├→ Power BI (dashboards)
  │       ├→ Azure Monitor (alerts)
  │       └→ Log Analytics (queries)
  │
  ├→ Custom Logs (JSON-structured)
  │   └→ Application Insights
  │
  ├→ Metrics (OpenTelemetry format)
  │   └→ Application Insights
  │
  └→ Errors/Exceptions
      └→ Application Insights
          └→ Alert Rules (Slack, Teams, PagerDuty)
```

---

## 2. Logs: Structured Event Recording

### 2.1 Log Schema (JSON)

Every agent action logs a structured event:

```json
{
  "timestamp": "2026-02-14T10:30:45.123Z",
  "level": "INFO",  // INFO, WARN, ERROR, DEBUG
  "component": "scout_agent",
  "agent_id": "scout_001",
  "action": "ingest_complete",
  "pitch_id": "story_2026_02_14_001",
  
  // Operational context
  "foundry_thread_id": "conv_story_2026_02_14_openai_vision",
  "execution_id": "exec_abc123def456",
  "parent_execution_id": "parent_xyz",  // For tracing parent-child relationships
  
  // Agent-specific data
  "headlines_ingested": 523,
  "headlines_after_filter": 18,
  "relevance_scores": {
    "min": 4.2,
    "max": 9.1,
    "mean": 6.8
  },
  "top_stories": [
    {
      "headline": "OpenAI Releases Vision Model",
      "relevance_score": 8.7,
      "source": "openai.com"
    }
  ],
  
  // Performance metrics
  "duration_ms": 3250,
  "api_calls": {
    "bing_news": {
      "count": 1,
      "latency_ms": 1200
    },
    "twitter_api": {
      "count": 1,
      "latency_ms": 800
    }
  },
  
  // Cost tracking
  "cost": {
    "api_calls_usd": 0.02,
    "tokens_used": 0
  },
  
  // Errors (if any)
  "error": null,  // or {code, message, stack_trace}
  
  // Custom fields
  "user_id": "editor_jane",
  "custom_context": {
    "user_interest_profile": ["AI", "tech", "local"],
    "filter_version": "2.1"
  }
}
```

### 2.2 Log Categories by Agent

**Scout Logs:**
- `scout.ingest_start` / `scout.ingest_complete`
- `scout.filter_applied` (keyword matching)
- `scout.relevance_score_calculated`
- `scout.pitch_card_sent` (to Teams)
- `scout.api_error` (circuit breaker triggered)
- `scout.cache_fallback_used`

**Prof Logs:**
- `prof.research_start` / `prof.research_complete`
- `prof.search_query_executed` (sources found)
- `prof.corroboration_assessed`
- `prof.brand_risk_identified`
- `prof.rescan_requested` (back to Scout)

**Scribe Logs:**
- `scribe.generation_start` / `scribe.generation_complete`
- `scribe.tone_selected`
- `scribe.word_count_tracked`
- `scribe.iteration_N_submitted` (to Judge)

**Judge Logs:**
- `judge.compliance_check_start` / `judge.compliance_check_complete`
- `judge.rule_matched` (vector search result)
- `judge.check_passed` / `judge.check_failed`
- `judge.feedback_generated`

**Pixel Logs:**
- `pixel.generation_start` / `pixel.generation_complete`
- `pixel.dalle_call_made`
- `pixel.image_processed` (PIL operations)
- `pixel.vision_qa_performed`
- `pixel.upload_to_blob` (success/failure)

**Ops Logs:**
- `ops.commit_start` / `ops.commit_complete`
- `ops.github_api_called`
- `ops.build_triggered`
- `ops.preview_url_ready`
- `ops.merge_executed`
- `ops.social_post_queued`

### 2.3 Log Sampling & Retention

```yaml
log_sampling:
  scout_ingest:
    sample_rate: 1.0  # Log every ingest (high value, low volume)
  
  profgen_query:
    sample_rate: 0.5  # Log 50% of searches (reduce noise)
  
  judge_passed:
    sample_rate: 0.1  # Log only 10% of passes (reduce noise)
  
  errors:
    sample_rate: 1.0  # ALWAYS log errors

retention:
  hot_logs: 7  # Full detail for 7 days
  cold_logs: 90  # Summary only for 90 days
```

---

## 3. Traces: Execution Flow

### 3.1 Foundry Native Traces

Foundry Agent Service automatically captures:

```json
{
  "traceId": "traceabc123",
  "duration": 70.2,  // seconds (end-to-end: Scout → Publish)
  "startTime": "2026-02-14T10:00:00Z",
  "endTime": "2026-02-14T11:10:15Z",
  "stages": [
    {
      "stage": "scout",
      "agent": "scout_001",
      "duration": 2.1,
      "toolCalls": [
        {
          "tool": "bing_news_api",
          "duration": 1.2,
          "result": "success",
          "itemsReturned": 523
        }
      ],
      "output": "Pitch generated"
    },
    {
      "stage": "human_approval",
      "waitTime": 420,  // 7 minutes
      "approval": "approved"
    },
    {
      "stage": "prof",
      "agent": "prof_001",
      "duration": 22.5,
      "toolCalls": [
        {
          "tool": "azure_ai_search",
          "duration": 0.8,
          "resultsReturned": 12
        },
        {
          "tool": "bing_search_v7",
          "duration": 3.2,
          "resultsReturned": 25
        }
      ]
    },
    {
      "stage": "scribe",
      "agent": "scribe_001",
      "duration": 15.3,
      "iterations": 2,
      "tokenUsage": {
        "input": 2150,
        "output": 890
      }
    },
    {
      "stage": "judge",
      "agent": "judge_001",
      "duration": 2.1,
      "rulesApplied": 8,
      "result": "passed_after_2_iterations"
    },
    // ... pixel and ops stages ...
  ]
}
```

### 3.2 Custom Trace Instrumentation

```python
# Example: Scribe agent
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def generate_draft(research_brief, tone):
    with tracer.start_as_current_span("scribe_generation") as span:
        span.set_attribute("tone", tone)
        span.set_attribute("research_confidence", research_brief.confidence)
        
        # Step 1: Prompt engineering
        with tracer.start_as_current_span("prompt_engineering"):
            prompt = build_prompt(research_brief, tone)
            span.set_attribute("prompt_tokens", count_tokens(prompt))
        
        # Step 2: LLM call
        with tracer.start_as_current_span("llm_call"):
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[...],
                temperature=0.7
            )
            span.set_attribute("output_tokens", response.usage.completion_tokens)
            span.set_attribute("finish_reason", response.choices[0].finish_reason)
        
        # Step 3: Validation
        with tracer.start_as_current_span("draft_validation"):
            word_count = count_words(response.content)
            span.set_attribute("word_count", word_count)
        
        return response.content
```

---

## 4. Metrics: Quantitative KPIs

### 4.1 Custom Metrics (via Application Insights)

```
Metric: scout_pitches_generated
  Unit: count
  Aggregation: sum
  Dimensions: [topic, time_bucket]
  
Metric: scout_relevance_score
  Unit: (0-10 scale)
  Aggregation: histogram (p50, p95, p99)
  
Metric: judge_rejection_rate
  Unit: percentage
  Aggregation: average
  Dimensions: [rejection_type, rejection_reason]
  
Metric: time_to_publish
  Unit: seconds
  Aggregation: histogram (p50, mean, p95, max)
  Dimensions: [editor_id, topic]
  
Metric: cost_per_article
  Unit: USD
  Aggregation: average
  Dimensions: [topic, gpt_model_used]
  
Metric: api_latency
  Unit: milliseconds
  Aggregation: histogram
  Dimensions: [api_name, region, result_status]
```

### 4.2 Prometheus-Compatible Metrics

```
# HELP aan_pitched_stories_total Total number of stories pitched
# TYPE aan_pitched_stories_total counter
aan_pitched_stories_total{topic="AI",scout="scout_001"} 150

# HELP aan_editor_approval_ratio Ratio of approved pitches
# TYPE aan_editor_approval_ratio gauge
aan_editor_approval_ratio{editor="jane"} 0.42

# HELP aan_judge_rejection_seconds_bucket Judge check duration
# TYPE aan_judge_rejection_seconds_bucket histogram
aan_judge_rejection_seconds_bucket{le="0.5",reason="absolute_claim"} 12
aan_judge_rejection_seconds_bucket{le="1.0",reason="absolute_claim"} 18
aan_judge_rejection_seconds_bucket{le="+Inf",reason="absolute_claim"} 25

# HELP aan_publish_duration_seconds End-to-end publish time
# TYPE aan_publish_duration_seconds histogram
aan_publish_duration_seconds_bucket{le="600"} 8
aan_publish_duration_seconds_bucket{le="3600"} 28
aan_publish_duration_seconds_bucket{le="7200"} 30
```

---

## 5. Dashboards

### 5.1 Main Operations Dashboard (Power BI)

**Refresh:** Every 5 minutes

**Cards:**
```
┌─────────────────────┬─────────────────────┐
│ Stories Today       │ Approval Rate       │
│ 14 (↑ 2 from avg)   │ 42% (↓ 5% from avg) │
└─────────────────────┴─────────────────────┘

┌─────────────────────┬─────────────────────┐
│ Avg Time-to-Publish │ Judge Rejection %   │
│ 2h 15m (↓ 10m)      │ 8.4% (↑ 0.5%)       │
└─────────────────────┴─────────────────────┘

┌─────────────────────────────────────────┐
│ Cumulative Cost Today                   │
│ $47.82 (↑ from $45 yesterday)           │
└─────────────────────────────────────────┘
```

**Charts:**
1. **Pitches by Hour** (line chart)
   - X-axis: Hour of day (0-23)
   - Y-axis: Count
   - Annotation: Target line (3-4 per hour)

2. **Approval Rate by Topic** (horizontal bar chart)
   - AI: 52%
   - Tech: 48%
   - Finance: 35%
   - Local: 28%

3. **Judge Rejection Reasons** (pie chart)
   - Absolute claims: 40%
   - Competitor disparagement: 15%
   - Factual unverifiable: 25%
   - Tone inconsistency: 20%

4. **Time-to-Publish Distribution** (histogram)
   - Shows p50, p95, p99 over time
   - Target: < 2 hours for 90% of articles

5. **Cost Breakdown** (stacked bar)
   - LLM tokens (GPT-4o, GPT-4o-mini)
   - DALL-E image generation
   - API calls (Bing, GitHub)
   - Infrastructure (Cosmos, Storage)

### 5.2 Cost Dashboard

**Refresh:** Daily (7 AM)

```
Cost Last 30 Days: $4,280
Average per Article: $5.12

Model Breakdown:
├─ GPT-4o: 55% ($2,354)
├─ GPT-4o-mini: 18% ($770)
├─ DALL-E 3: 15% ($642)
├─ APIs: 8% ($342)
└─ Infrastructure: 4% ($172)

Optimization Opportunities:
├─ Scribe is using GPT-4o for revisions → consider gpt-4o-mini for iterations
├─ Image generation skipped on 12% of articles → cost-effective
└─ Judge consuming 5% of budget; consider separating rule evaluation from LLM
```

### 5.3 Quality Dashboard

**Refresh:** Hourly

```
Quality Score: 94/100

Metrics:
├─ Judge Pass Rate (First Try): 85% (↑ target: 80%)
├─ Edit Rate (Editor Modifications): 12% (↓ target: < 15%)
├─ Factual Accuracy (Post-Publish Audit): 98% ✅
├─ Brand Tone Consistency: 91% (↑ target: 90%)
└─ Image Quality Score (ML-validated): 8.7/10

Risks:
├─ ⚠️ Competitor mentions: 2 articles violated rules (fixed by Judge)
└─ ⚠️ Low-confidence research: 3 articles flagged this week

Trends:
├─ Absolute claims rejections: ↓ declining (training working)
├─ Financial claims accuracy: ↑ improving
└─ Time-to-publish: ↓ 15% faster than last week
```

---

## 6. Alerts & Remediation

### 6.1 Alert Definitions

**Alert 1: High Judge Rejection Rate**
```yaml
alert:
  name: "HIGH_JUDGE_REJECTION_RATE"
  condition: "rejection_rate > 15% in past 24h"
  severity: "warning"
  actions:
    - send_to: "slack"
      channel: "#aan-ops"
      message: "⚠️ Judge rejection rate is {{rejection_rate}}%. 
                Check if rulebook is too strict or Scribe quality degraded."
    - send_to: "teams"
      recipient: "editor@company.com"
      notification: true
```

**Alert 2: API Circuit Breaker Activated**
```yaml
alert:
  name: "API_CIRCUIT_BREAKER_OPEN"
  condition: "any_circuit_breaker == OPEN"
  severity: "critical"
  actions:
    - send_to: "pagerduty"
      escalation_policy: "on-call-ai-ops"
    - send_to: "slack"
      channel: "#aan-incidents"
      message: "🔴 {{api_name}} circuit breaker open. 
                Fallback: {{fallback_strategy}}. ETA: {{recovery_time}}"
    - auto_remediate: "restart_scout"  # Restart if it's Scout's API
```

**Alert 3: Cost Spike**
```yaml
alert:
  name: "COST_SPIKE_DETECTED"
  condition: "cost_per_article > baseline * 1.5"
  severity: "info"
  actions:
    - send_to: "slack"
      message: "💰 Cost per article increased to ${{cost}}. 
                Top driver: {{top_cost_driver}}"
```

**Alert 4: DLQ Backlog Growing**
```yaml
alert:
  name: "DLQ_BACKLOG_HIGH"
  condition: "dlq_queue_length > 5"
  severity: "warning"
  actions:
    - send_to: "teams"
      recipient: "editor@company.com"
      message: "Manual review needed: {{dlq_queue_length}} failed stories"
    - action: "send_daily_digest"
      time: "09:00 UTC"
```

### 6.2 Runbooks (Auto-Remediation)

**Runbook 1: Restart Scout (API Failure)**
```
Trigger: Bing API failures > 3 in 5 minutes
Action:
  1. Open circuit breaker
  2. Switch to cached headlines from past 24h
  3. Log warning: "Using cached headlines; Bing API unavailable"
  4. Retry Bing connection every 2 minutes
  5. On recovery: Close circuit breaker, resume normal
  6. Send Slack notification
Cost: Zero (uses existing cache)
```

**Runbook 2: Reduce Model to GPT-4o-mini if Costs High**
```
Trigger: Cost per article > $7
Actions:
  1. Enable "lightweight mode"
  2. Scribe uses GPT-4o-mini for iterations (not first draft)
  3. Judge uses mini for low-severity checks
  4. Log decision with justification
  5. Monitor Judge rejection rate (may increase)
  6. Auto-revert if rejection rate > 20%
Estimated savings: 40-50%
```

---

## 7. Incident Response Playbook

### 7.1 Severity Levels

| Severity | Example | SLA | Action |
|----------|---------|-----|--------|
| **Critical** (🔴) | Scout down; no pitches generated for 2h | 15 min | Page on-call-ai |
| **High** (🟠) | Judge rejection rate > 25% | 1 hour | Alert ops team |
| **Medium** (🟡) | Cost spike; time-to-publish > 3h | 4 hours | Monitor, investigate |
| **Low** (🟢) | Single API call timed out | 24 hours | Log, no action |

### 7.2 Incident Response Flow

```
Incident Detected (via alert)
  ↓
Notify relevant team (Slack/PagerDuty)
  ↓
Assign on-call engineer
  ↓
Check runbook (pre-defined remediation)
  ↓
Does runbook apply?
  ├─YES→ Execute auto-remediation
  │       ↓
  │       Monitor recovery
  │       ↓
  │       Post-incident review (if critical)
  │
  └─NO→ Manual investigation
        ↓
        Execute remediation
        ↓
        Create/update runbook
        ↓
        Post-incident review
```

### 7.3 Post-Incident Review (PIR)

**Template:**
```markdown
# PIR: {{incident_name}} on {{date}}

## Impact
- Duration: {{duration}}
- Stories affected: {{count}}
- Estimated cost: ${{cost}}

## Root Cause
{{Root cause analysis}}

## Timeline
- {{time}}: Issue detected
- {{time}}: Alert fired
- {{time}}: Remediation started
- {{time}}: System recovered

## Action Items
- [ ] {{action}} (Owner: {{person}}, Due: {{date}})
- [ ] {{action}} (Owner: {{person}}, Due: {{date}})

## Lessons Learned
{{What did we learn?}}
```

---

## 8. Custom Visualizations

### 8.1 Agent Health Status Widget

```
┌─────────────────────────────────────────┐
│  AGENT HEALTH STATUS (Real-time)        │
├─────────────────────────────────────────┤
│ Scout        🟢 Healthy                 │
│ Prof         🟢 Healthy                 │
│ Scribe       🟡 Degraded (slow)         │
│ Judge        🟢 Healthy                 │
│ Pixel        🟠 Circuit Breaker Open    │
│ Ops          🟢 Healthy                 │
│                                          │
│ Overall: 🟡 Degraded                    │
└─────────────────────────────────────────┘
```

### 8.2 Story Lifecycle Heat Map

```
Time-of-Day vs. Approval Rate

       10am  11am  12pm  1pm  2pm  3pm   4pm  5pm
Mon    45%   48%   42%   50%  52%  49%   43%  41%
Tue    44%   51%   47%   53%  51%  48%   45%  42%
Wed    48%   50%   48%   52%  50%  47%   46%  44%
Thu    52%   55%   50%   54%  53%  51%   48%  46%
Fri    38%   41%   39%   43%  44%  42%   40%  38%

Insight: Mid-day (11am-2pm) optimal for approvals
         Friday morning: Editor less engaged
```

---

## 9. Observability Checklist

- [ ] All agents emit structured logs (JSON)
- [ ] Foundry native tracing enabled
- [ ] Custom metrics registered (OpenTelemetry)
- [ ] Power BI dashboards deployed (refresh every 5 min)
- [ ] Alert rules configured (all severity levels)
- [ ] Runbooks documented (in wiki)
- [ ] PagerDuty/Slack/Teams integration tested
- [ ] Log retention policies set (hot: 7d, cold: 90d)
- [ ] Cost dashboards reviewed daily
- [ ] PIR template adopted by team
- [ ] Monthly observability review scheduled
- [ ] Team trained on dashboards + alerts

---

**Document Version:** 1.0  
**Last Updated:** February 14, 2026  
**Status:** Ready for Implementation ✅
