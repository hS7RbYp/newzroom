# ============================================================================
# INFRASTRUCTURE COMPOSITION
# ============================================================================
# This file orchestrates all Azure resources for the Autonomous Newsroom

# Azure OpenAI
module "azure_openai" {
  source = "./modules/azure_openai"

  resource_prefix     = local.resource_prefix
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  sku_name              = var.openai_sku_name
  gpt4o_deployment      = var.gpt4o_deployment
  gpt4o_mini_deployment = var.gpt4o_mini_deployment
  dalle_deployment      = var.dall_e_deployment

  tags = local.common_tags
}

# Cosmos DB
module "cosmos_db" {
  source = "./modules/cosmos_db"

  resource_prefix     = local.resource_prefix
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  consistency_level       = var.cosmos_consistency_level
  backup_retention_hours  = var.backup_retention_days * 24
  enable_analytics        = var.enable_analytics

  tags = local.common_tags
}

# Azure AI Search
module "ai_search" {
  source = "./modules/ai_search"

  resource_prefix     = local.resource_prefix
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  sku       = var.search_sku
  replicas  = var.search_replicas
  partitions = var.search_partitions
  public_network_access = var.enable_public_network_access

  tags = local.common_tags
}

# Key Vault
# TODO: Configure with actual service keys after deployment
# module "key_vault" {
#   ...
# }

# Application Insights
module "app_insights" {
  source = "./modules/app_insights"

  resource_prefix     = local.resource_prefix
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  retention_days      = 90

  tags = local.common_tags
}

# Service Bus
module "service_bus" {
  source = "./modules/service_bus"

  resource_prefix     = local.resource_prefix
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"

  tags = local.common_tags
}

# Static Web Apps
# TODO: Deploy after Phase 1
#module "static_web_apps" {
#  source = "./modules/static_web_apps"
#
#  resource_prefix     = local.resource_prefix
#  resource_group_name = azurerm_resource_group.main.name
#  staging_domain      = var.staging_domain != "" ? var.staging_domain : "${local.resource_prefix}-staging.azurestaticapps.net"
#  prod_domain         = var.prod_domain != "" ? var.prod_domain : "${local.resource_prefix}-prod.azurestaticapps.net"
#  enable_prod_domain  = var.environment == "prod"
#
#  tags = local.common_tags
#}

# ============================================================================
# FOUNDRY AGENT SERVICE - MANAGED IDENTITY
# ============================================================================
# TODO: Configure after Phase 1 when Foundry service is set up
# resource "azurerm_user_assigned_identity" "foundry" {
#   name                = "${local.resource_prefix}-foundry-msi"
#   location            = azurerm_resource_group.main.location
#   resource_group_name = azurerm_resource_group.main.name
#
#   tags = local.common_tags
# }
#
# resource "azurerm_role_assignment" "foundry_reader" {
#   scope              = azurerm_resource_group.main.id
#   role_definition_name = "Reader"
#   principal_id       = azurerm_user_assigned_identity.foundry.principal_id
# }

# ============================================================================
# MONITORING ALERTS
# ============================================================================
# TODO: Add alerts after Phase 1
#resource "azurerm_monitor_action_group" "main" {
#  name                = "${local.resource_prefix}-actiongroup"
#  resource_group_name = azurerm_resource_group.main.name
#  short_name          = "AAN"
#}

# ============================================================================
# OUTPUTS
# ============================================================================
output "openai_endpoint" {
  value       = module.azure_openai.openai_endpoint
  description = "Azure OpenAI endpoint"
}

output "openai_key" {
  value       = module.azure_openai.openai_key
  sensitive   = true
  description = "Azure OpenAI primary access key"
}

output "cosmos_endpoint" {
  value       = module.cosmos_db.cosmos_endpoint
  description = "Cosmos DB endpoint"
}

output "cosmos_key" {
  value       = module.cosmos_db.cosmos_key
  sensitive   = true
  description = "Cosmos DB primary key"
}

output "search_endpoint" {
  value       = module.ai_search.search_endpoint
  description = "Azure AI Search endpoint"
}

output "search_key" {
  value       = module.ai_search.search_key
  sensitive   = true
  description = "Azure AI Search admin key"
}

output "app_insights_instrumentation_key" {
  value       = module.app_insights.instrumentation_key
  sensitive   = true
  description = "Application Insights instrumentation key"
}

output "service_bus_namespace" {
  value       = module.service_bus.namespace_name
  description = "Service Bus namespace"
}

output "deployment_summary" {
  value = {
    openai    = module.azure_openai.openai_endpoint
    cosmos    = module.cosmos_db.cosmos_endpoint
    search    = module.ai_search.search_endpoint
    appins    = module.app_insights.app_insights_id
    servicebus = module.service_bus.namespace_name
  }
  description = "Summary of deployed resources"
}
