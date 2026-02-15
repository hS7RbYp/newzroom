# Azure OpenAI Module - Simplified
# Note: Model deployments must be created via Azure Portal or Azure CLI
# due to resource API limitations in Terraform

resource "azurerm_cognitive_account" "openai" {
  name                = "${var.resource_prefix}-openai"
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = var.sku_name
  custom_subdomain_name = var.resource_prefix

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Outputs for .env configuration
output "openai_endpoint" {
  value       = azurerm_cognitive_account.openai.endpoint
  description = "Azure OpenAI endpoint URL"
}

output "openai_id" {
  value       = azurerm_cognitive_account.openai.id
  description = "Azure OpenAI resource ID"
}

output "openai_key" {
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
  description = "Azure OpenAI primary access key"
}

output "openai_principal_id" {
  value       = try(azurerm_cognitive_account.openai.identity[0].principal_id, "")
  description = "Azure OpenAI managed identity principal ID"
}
