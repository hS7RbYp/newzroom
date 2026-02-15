# Azure Autonomous Newsroom - Cost Optimization Guide

**Date:** February 14, 2026  
**Current Environment:** Development (rg-aan-dev)  
**Region:** eastus

---

## 📊 Current Infrastructure Costs

### Monthly Cost Breakdown (Estimates)

| Service | SKU | Config | Est. Monthly Cost | Notes |
|---------|-----|--------|-------------------|-------|
| **Azure OpenAI** | S0 (Standard) | Pay-per-use | $0.002-0.15 per 1K tokens* | **HIGHEST VARIABILITY** |
| **Cosmos DB** | Standard | Session, Single-region | $50-200+ | Depends on RU/s provisioning |
| **AI Search** | Standard | 1 partition, 1 replica | $255/month | Fixed (~$0.30 per hour × 730 hrs) |
| **Service Bus** | Standard | Namespace | $10-15 | Low cost |
| **Log Analytics** | Pay-as-you-go | Workspace | $2-5 | Data ingestion/retention |
| **Static Web Apps** | Free | (Phase 1+) | $0 | Free hosting |
| **Key Vault** | Standard | (Phase 1+) | $0.60/month | 10 operations/month |
| **Application Insights** | Standard | (Phase 1+) | $2-10 | Data ingestion |
| | | | | |
| **TOTAL (Conservative)** | | | **$320-495/month** | + OpenAI token costs |
| **TOTAL (With Heavy Usage)** | | | **$500-1000+/month** | If OpenAI processes 100M tokens/month |

*OpenAI pricing example: 100M tokens/month ≈ $100-150, depending on model mix (GPT-4o vs GPT-4o-mini)

---

## 🔴 Highest Cost Drivers (In Order)

### 1. **Azure AI Search (Standard Tier) - $255/month**
- **Why it's expensive:** Fixed hourly rate ($0.30/hr) regardless of usage
- **Your config:** Standard tier (1 partition, 1 replica)
- **Impact:** ~26% of total infrastructure cost

**Cost Reduction Options:**
- **BEST:** Delete for dev environment, use in-memory vector search with Cosmos DB
  - Save: **$255/month (-52%)**
  - Trade-off: Slower semantic search, need to build custom vector indexing
  
- **GOOD:** Switch to Free tier (if applicable)
  - Save: **$255/month** 
  - Limit: 50K documents/index only, great for MVP testing
  - Action: `az search service delete --name aan-dev-search --resource-group rg-aan-dev`

- **OKAY:** Keep for now, no replicas/partitions needed in dev
  - Current: 1 replica × 1 partition = $255
  - Free tier unavailable after initial creation, but Standard is minimum paid tier

---

### 2. **Azure OpenAI - Pay-Per-Token (Variable)**
- **Why it's expensive:** GPT-4o = $15/MTok input, $60/MTok output
- **Your config:** S0 SKU (Standard, unlimited quotas) 
- **Impact:** Scales with usage - could be $100-500/month depending on agent activity

**Cost Reduction Options:**
- **BEST:** Use GPT-4o-mini for lightweight agents, GPT-4o only for complex tasks
  - GPT-4o-mini: $0.15/MTok input, $0.60/MTok output (90% cheaper)
  - Scout Agent (article extraction) → **GPT-4o-mini**
  - Scribe Agent (formatting) → **GPT-4o-mini**
  - Prof Agent (analysis) → **GPT-4o** (as needed)
  - Judge Agent (QA) → **GPT-4o-mini** (basic checks)
  - Pixel Agent (images) → **Fixed 7-second calls to DALL-E**
  - **Save:** ~70% on token costs = **$40-100/month**

- **GOOD:** Cache prompts using Azure OpenAI prompt caching
  - System prompts + brand rules cached once = 50% cost reduction
  - Scout/Scribe system prompts could save $10-15/month

- **OKAY:** Batch API (off-peak processing)
  - Batch API: 50% discount on token costs
  - Not suitable for real-time news, but good for bulk analysis
  - Trade-off: 24-hour turnaround

---

### 3. **Cosmos DB - RU/s Provisioning (Variable)**
- **Why it's expensive:** Default provisioned RU/s can be high ($0.012-0.15 per RU/s/hour)
- **Your config:** Session consistency, single region (optimal)
- **Impact:** Likely $50-200/month depending on provisioning

**Cost Reduction Options:**
- **BEST:** Use Cosmos DB serverless (auto-scaling)
  - Pricing: $0.25 per 1M read operations
  - Good for: Bursty workloads (typical dev/test)
  - Save: **$30-80/month** vs standard provisioning
  - Action: Cannot migrate existing DB, must create new one
  
- **GOOD:** Reduce provisioned RU/s if overprovisioned
  - Check: `az cosmosdb sql database throughput show --account-name aan-dev-cosmos --database-name articles --resource-group rg-aan-dev`
  - Recommendation: Start with 400 RU/s (minimum), scale up as needed
  - Save: **$20-50/month** per 100 RU/s reduction

- **OKAY:** Enable autoscale (max provisioned)
  - Scales down during off-hours
  - Slightly more expensive but prevents over-paying for idle capacity
  - Save: **$10-20/month** if workload is bursty

---

### 4. **Service Bus - Lower Priority ($10-15/month)**
- **Your config:** Standard tier, single namespace
- **Cost Reduction:** Already optimized for dev
  - Could downgrade to **Free tier** ($0/month) if < 12.5M operations/month
  - Check: `az servicebus namespace show --name aan-dev-bus --resource-group rg-aan-dev --query "sku.name"`
  - Action: Delete and recreate with Free tier

---

### 5. **Log Analytics - Lower Priority ($2-10/month)**
- **Your config:** Workspace-based ingestion
- **Cost Reduction:**
  - Reduce retention from 30 days to 7 days: **Save $2-5/month**
  - Use sampling (50% of logs in dev): **Save $1-3/month**
  - Delete workspace if not actively monitoring: **$0/month**

---

## 💡 Recommended Cost Optimization Strategy

### **Phase 1: Immediate Savings (Launch Today) - Save $120-180/month**
1. **Delete Azure AI Search** service
   ```bash
   az search service delete --name aan-dev-search --resource-group rg-aan-dev
   ```
   - Savings: **$255/month** (-100%)
   - Replacement: Use Cosmos DB vector search with Azure OpenAI embeddings
   - Timeline: < 5 minutes
   - Code impact: Modify agent code to query Cosmos DB directly

2. **Tune Cosmos DB to 400 RU/s**
   ```bash
   az cosmosdb sql database throughput update \
     --account-name aan-dev-cosmos \
     --database-name articles \
     --resource-group rg-aan-dev \
     --throughput 400
   ```
   - Savings: **$20-50/month** (-30%)
   - Timeline: ~2 minutes
   - Risk: May need to scale up if Scout agent writes too fast

3. **Switch Scout/Scribe agents to GPT-4o-mini**
   - Edit [agents/scout.py](agents/scout.py#L45) and [agents/scribe.py](agents/scribe.py#L60)
   - Change: `model="gpt-4o"` → `model="gpt-4o-mini"`
   - Savings: **$40-80/month** (-60%)
   - Timeline: ~10 minutes
   - Risk: May need to verify output quality

**Subtotal Savings: $315-385/month (-64%)**

---

### **Phase 2: Smart Architecture (Week 1) - Save $50-100/month**
1. **Enable Cosmos DB serverless** (new database)
   - Create new articles database with serverless billing
   - Migrate data from provisioned version
   - Savings: **$30-80/month**
   - Timeline: 30 minutes
   - Cost: $0 during setup, then $0.25 per 1M reads

2. **Implement prompt caching** for Scout/Judge agents
   - Cache system prompts + brand rules (cached tokens = 90% discount)
   - Savings: **$10-20/month**
   - Timeline: 2-3 hours (code implementation)

3. **Enable Service Bus Free tier**
   - Delete current Standard namespace, recreate as Free
   - Savings: **$10-15/month** 
   - Timeline: 5 minutes
   - Limit: 12.5M operations/month (typical workload)

**Subtotal Savings: $50-115/month**

---

### **Phase 3: Production Optimization (Month 2+) - Ongoing Efficiency**
1. **Use Batch API for non-real-time analysis**
   - Defer complex Prof agent work to batch processing
   - Savings: **50% discount on batch operations** ($20-50/month)

2. **Archive old articles to Blob Storage** (not Cosmos)
   - Cosmos DB: $0.25 per 1M reads
   - Blob Storage: $0.02 per 10K reads
   - Savings: **$5-10/month** if > 100K articles

3. **Monitor and right-size** via Azure Cost Management
   - Set budgets, get alerts at $400, $600, $800/month
   - Review monthly: Turn off unused agents during off-hours

---

## 📈 Estimated Final Costs (All Optimizations)

### Development Environment (Optimized)
| Service | Old Cost | New Cost | Savings |
|---------|----------|----------|---------|
| Azure OpenAI | $100-150 | $30-50 | **-70%** |
| Cosmos DB | $100-150 | $0.25/1M reads | **-80%** |
| AI Search | $255 | $0 | **-100%** |
| Service Bus | $12 | $0 | **-100%** |
| Log Analytics | $5 | $2 | **-60%** |
| **TOTAL** | **$472-572** | **$32-52** | **-92%** |

---

### Production Environment (Medium Scale - 100K article/month)
| Service | Config | Est. Monthly |
|---------|--------|--------------|
| Azure OpenAI | GPT-4o-mini heavy, GPT-4o for complex | $80-120 |
| Cosmos DB | Serverless (4M reads = $1) | $5-10 |
| AI Search | Free tier (50K docs limit) + Blob *overflow* | $0 |
| Service Bus | Standard | $12 |
| App Insights | Standard | $5 |
| Static Web Apps | Free tier | $0 |
| CDN (for images) | Standard | $0.087/GB | ~$50 (if 500GB images) |
| **TOTAL** | | **$152-197/month** |

---

## 🎯 Action Plan (Recommended)

### ✅ Do Today (Save $315/month)
1. Delete AI Search service:
```bash
az search service delete --name aan-dev-search --resource-group rg-aan-dev
```

2. Update .env to remove SEARCH_* variables (agents will use Cosmos direct query)

3. Update Scout agent code:
   - File: [agents/scout.py](agents/scout.py)
   - Change model to gpt-4o-mini
   - Add Cosmos vector query instead of Search query

4. Tune Cosmos DB throughput to 400 RU/s (minimum viable)

### ⏭ Do This Week
1. Implement Cosmos DB vector search in agents
2. Enable prompt caching for system prompts
3. Migrate Service Bus to Free tier
4. Test all agents with cost-optimized configuration

### 📋 Do This Month
1. Set up Azure Cost Management alerts
2. Monitor actual token usage per agent
3. Create cost-tracking dashboard
4. Plan production migration with optimized pricing

---

## ⚠️ Cost-Quality Trade-offs

| Change | Benefit | Risk | Mitigation |
|--------|---------|------|-----------|
| Delete AI Search | -$255/month | Slower vector search | Use Cosmos vector search + pagination |
| GPT-4o-mini for Scout | -$40/month | May miss nuanced articles | Monitor F1 scores, A/B test |
| 400 RU/s Cosmos | -$50/month | May throttle during spikes | Set autoscale max to 1000 RU/s |
| Free Service Bus | -$12/month | 12.5M op/month limit | Monitor queue depth, size accordingly |

---

## 💰 Pricing References

### Azure OpenAI (Tokens)
- **GPT-4o:** $15/MTok input, $60/MTok output
- **GPT-4o-mini:** $0.15/MTok input, $0.60/MTok output
- **DALL-E 3:** 1024×1024 = $0.02, 1024×1792 = $0.03

### Cosmos DB
- **Provisioned (Session):** $0.012/RU/hr (= ~$9/month per 100 RU/s)
- **Serverless:** $0.25 per 1M read operations

### Azure AI Search
- **Free:** $0/month (50K docs limit)
- **Standard:** $0.30/hr = $255/month (1M docs, 1 partition)
- **Basic/S1/S2:** $0.30-1.20/hr

### Service Bus
- **Free:** $0/month (12.5M ops/month)
- **Standard:** $0.05 per operation (after 12.5M/month free ops)
- **Premium:** $1.27/hour (dedicated capacity)

### Application Insights
- **Free:** $0 (1GB/day limit)
- **Standard:** $2.30 per GB ingested + $0.50/GB retention

---

## 📞 Questions & Follow-up

1. **What is expected monthly article volume?** (affects AI Search value vs Cosmos DB cost)
2. **What is target response time?** (affects provisioning choices)
3. **Do you need real-time publishing or batch processing is okay?** (affects OpenAI model choice)
4. **Is image generation core to the product?** (DALL-E costs can add up)

---

## 🔗 References

- [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)
- [Cosmos DB Cost Calculator](https://cosmos.azure.com/capacitycalculator/)
- [Azure Cost Management](https://portal.azure.com/#blade/Microsoft_Azure_Cost/CostMenuBlade/Overview)
- [Right-size resources in Azure](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-optimization-solution-overview)
