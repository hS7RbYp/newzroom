# Azure AI Search Module

resource "azurerm_search_service" "main" {
  name                = "${var.resource_prefix}-search"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.sku
  replica_count       = var.replicas
  partition_count     = var.partitions

  public_network_access_enabled = var.public_network_access

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

output "search_endpoint" {
  value       = azurerm_search_service.main.primary_search_endpoint
  description = "Azure AI Search primary endpoint"
}

output "search_id" {
  value       = azurerm_search_service.main.id
  description = "Azure AI Search resource ID"
}

output "search_key" {
  value       = azurerm_search_service.main.primary_admin_key
  sensitive   = true
  description = "Azure AI Search primary admin key"
}

output "search_principal_id" {
  value       = try(azurerm_search_service.main.identity[0].principal_id, "")
  description = "Azure AI Search managed identity principal ID"
}
