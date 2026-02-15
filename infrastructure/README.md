# Azure Autonomous Newsroom - Infrastructure as Code

This directory contains Terraform configurations for deploying all Azure resources needed for the Autonomous Newsroom system.

## 📁 Structure

```
infrastructure/
├── main.tf                    # Root module - Azure resource setup
├── variables.tf               # Input variables for all resources
├── infrastructure.tf          # Module composition
├── outputs.tf                 # Output values exported after deploy
├── .terraform/                # Terraform state & cache (ignored)
├── modules/                   # Reusable infrastructure modules
│   ├── azure_openai/          # GPT-4o, GPT-4o-mini, DALL-E
│   ├── cosmos_db/             # Document & working memory
│   ├── ai_search/             # Vector search for brand rules
│   ├── key_vault/             # Secrets management
│   ├── app_insights/          # Observability & logging
│   ├── service_bus/           # Agent messaging & DLQ
│   └── static_web_apps/       # UI hosting
├── environments/              # Environment-specific configs
│   ├── dev.tfvars
│   ├── staging.tfvars
│   └── prod.tfvars
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Terraform >= 1.5
- Azure CLI (`az login`)
- Azure subscription with Contributor role

### Deploy Development Environment
```bash
cd infrastructure
terraform init
terraform plan -var-file=environments/dev.tfvars
terraform apply -var-file=environments/dev.tfvars
```

### Deploy Production Environment
```bash
terraform plan -var-file=environments/prod.tfvars -out=prod.tfplan
terraform apply prod.tfplan
```

## 📊 Environment Configurations

| Variable | Dev | Staging | Prod | Description |
|----------|-----|---------|------|-------------|
| `search_replicas` | 1 | 3 | 6 | AI Search high availability |
| `cosmos_throughput` | 4000 | 8000 | 40000 | Database autoscale max |
| `enable_public_network_access` | true | true | false | Private Link only in prod |
| `consistency_level` | Session | Session | Strong | Data consistency guarantee |

## 🔑 Key Modules

### Azure OpenAI
- **GPT-4o**: Scribe agent (50 capacity), Prof agent (50 capacity)
- **GPT-4o-mini**: Scout agent (100 capacity), Judge agent (100 capacity)
- **DALL-E 3**: Pixel image generation agent (3 capacity)

**Cost Estimation (Dev)**: ~$200/month  
**Cost Estimation (Prod)**: ~$2,000/month

### Cosmos DB (Serverless)
- Working memory for active articles
- Agent state tracking
- TTL: 30 days for articles, 7 days for state
- Automatic backups with 7-30 day retention

**Cost**: Consumption-based (Dev ~$50/month, Prod ~$500/month)

### Azure AI Search
- Semantic search for brand rule enforcement
- Vector embeddings (1536 dims)
- Analytics & monitoring
- High availability in staging/prod

**Cost**: Reserved capacity (Dev $100/month, Prod $1,500/month)

### Key Vault
- Stores OpenAI, Cosmos, Search keys
- RBAC-controlled access
- 90-day soft delete protection

**Cost**: ~$0.6/vault/month

### Application Insights
- Structured JSON logging
- Performance tracing
- Custom metrics for agent scoring
- 90-day retention

**Cost**: ~$50/month

## 🔐 Security

- **Network**: Private Link endpoints (prod)
- **Identity**: Managed identities for Foundry service
- **Secrets**: Key Vault with RBAC
- **Compliance**: SOC2-ready tagging & audit logs

## 📈 Scaling Strategy

### Horizontal Scaling
```bash
# Increase AI Search replicas
terraform apply -var="search_replicas=6"

# Increase Cosmos throughput
terraform apply -var="cosmos_max_throughput=80000"
```

### Regional Redundancy (Future)
```hcl
# Add geo-replication in modules/cosmos_db/main.tf
geo_location {
  location          = "westus"
  failover_priority = 1
}
```

## 🧪 Validate Before Deploy

```bash
# Syntax check
terraform validate

# Format check
terraform fmt -recursive

# Security scan
tfsec .

# Cost estimation
terraform plan -var-file=environments/prod.tfvars | grep -i cost
```

## 📝 State Management

```bash
# View current state
terraform state list
terraform state show azurerm_resource_group.main

# Backup state (IMPORTANT)
terraform state pull > backup.tfstate

# Remove resource from state (careful!)
terraform state rm module.service_bus
```

## 🚨 Disaster Recovery

### Backup Cosmos DB
```bash
az cosmosdb backup restore \
  --resource-group rg-aan-prod \
  --account-name aan-prod-cosmos \
  --target-database articles \
  --timestamp 2024-02-14T00:00:00Z
```

### Restore Search Index
```bash
# Rebuild from backup
az search admin-index delete --resource-group rg-aan-prod --search-service-name aan-prod-search --index-name brand-rules
az search admin-index create --resource-group rg-aan-prod --search-service-name aan-prod-search --index-name brand-rules --index-definition @index-backup.json
```

## 📞 Troubleshooting

### Terraform State Lock
```bash
# Release stuck lock
terraform force-unlock <LOCK_ID>
```

### Azure Authentication Failed
```bash
az logout
az login
az account set --subscription <SUBSCRIPTION_ID>
```

### Deployment Timeout
```bash
# Increase timeout
terraform apply -var="timeout_minutes=30"
```

## 📚 Related Documentation

- [System Design v3.0](/docs/SYSTEM_DESIGN_v3.0.md#infrastructure)
- [Agent Mesh Communication](/docs/AGENT_MESH_COMMUNICATION.md)
- [Implementation Roadmap](/docs/IMPLEMENTATION_ROADMAP.md) - Phase 0

## ✅ Validation Checklist

- [ ] terraform init completes
- [ ] terraform validate passes
- [ ] terraform plan shows expected resources
- [ ] terraform apply completes without errors
- [ ] All module outputs are populated
- [ ] Azure Portal shows resources created
- [ ] Key Vault secrets are accessible
- [ ] AI Search indexes are created
- [ ] Cosmos DB endpoints respond
- [ ] Application Insights receives data

---

**Maintained by:** Infrastructure Team  
**Last Updated:** 2026-02-14  
**Terraform Version:** 1.5+
