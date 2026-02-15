# Terraform outputs - exported values for production use

output "infrastructure_summary" {
  description = "Summary of deployed infrastructure"
  value = {
    region            = azurerm_resource_group.main.location
    resource_group    = azurerm_resource_group.main.name
    openai_endpoint   = module.azure_openai.openai_endpoint
    cosmos_endpoint   = module.cosmos_db.cosmos_endpoint
    search_endpoint   = module.ai_search.search_endpoint
    key_vault         = module.key_vault.key_vault_uri
    app_insights_id   = module.app_insights.app_insights_id
    service_bus       = module.service_bus.namespace_name
    web_app_hostname  = module.static_web_apps.default_host_name
  }
}

output "connection_strings" {
  description = "Connection strings for application configuration"
  value = {
    cosmos_endpoint = module.cosmos_db.cosmos_endpoint
    search_endpoint = module.ai_search.search_endpoint
    openai_endpoint = module.azure_openai.openai_endpoint
    key_vault_uri   = module.key_vault.key_vault_uri
  }
  sensitive = false
}

output "deployment_info" {
  description = "Deployment information"
  value = {
    deployed_at      = timestamp()
    terraform_version = "~> 1.5"
    provider_version  = "~> 3.85"
  }
}
