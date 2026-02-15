# Application Insights Module (Observability)

resource "azurerm_application_insights" "main" {
  name                = "${var.resource_prefix}-insights"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
  retention_in_days   = var.retention_days

  tags = var.tags
}

# Log Analytics Workspace (for KQL queries)
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.resource_prefix}-logs"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_days

  tags = var.tags
}

# Connect App Insights to Log Analytics
resource "azurerm_monitor_diagnostic_setting" "app_insights" {
  name                       = "app-insights-logs"
  target_resource_id         = azurerm_application_insights.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "AppServiceAppLogs"
  }

  enabled_log {
    category = "AppServiceConsoleLogs"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

output "instrumentation_key" {
  value     = azurerm_application_insights.main.instrumentation_key
  sensitive = true
}

output "app_insights_id" {
  value = azurerm_application_insights.main.id
}

output "workspace_id" {
  value = azurerm_log_analytics_workspace.main.workspace_id
}
