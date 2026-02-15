# Azure Static Web Apps Module

resource "azurerm_static_site" "main" {
  name                = "${var.resource_prefix}-static"
  location            = "eastus"  # SWA limited regions
  resource_group_name = var.resource_group_name
  sku_size            = var.sku_size
  sku_tier            = "Free"

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Staging environment
resource "azurerm_static_site_custom_domain" "staging" {
  static_site_id            = azurerm_static_site.main.id
  domain_name               = var.staging_domain
  validation_type           = "dns-txt-token"
}

# Production environment
resource "azurerm_static_site_custom_domain" "prod" {
  count                     = var.enable_prod_domain ? 1 : 0
  static_site_id            = azurerm_static_site.main.id
  domain_name               = var.prod_domain
  validation_type           = "dns-txt-token"
}

output "default_host_name" {
  value = azurerm_static_site.main.default_host_name
}

output "api_key" {
  value     = azurerm_static_site.main.api_key
  sensitive = true
}

output "static_site_id" {
  value = azurerm_static_site.main.id
}
