# Cosmos DB Module

resource "azurerm_cosmosdb_account" "main" {
  name                = "${var.resource_prefix}-cosmos"
  location            = var.location
  resource_group_name = var.resource_group_name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level       = var.consistency_level
    max_staleness_prefix    = 100000
    max_interval_in_seconds = 300
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }

  # Enable serverless
  capabilities {
    name = "EnableServerless"
  }

  # For backups
  backup {
    type                = "Continuous"
    interval_in_minutes = 60
    retention_in_hours  = var.backup_retention_hours
    storage_redundancy  = "Geo"
  }

  # Analytical storage for analytics
  analytical_storage_enabled = var.enable_analytics

  tags = var.tags
}

# Main database for working memory
resource "azurerm_cosmosdb_sql_database" "articles" {
  name                = "articles"
  account_name        = azurerm_cosmosdb_account.main.name
  resource_group_name = var.resource_group_name
}

# Articles container (working memory)
resource "azurerm_cosmosdb_sql_container" "articles_container" {
  name                = "articles"
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.articles.name
  resource_group_name = var.resource_group_name
  partition_key_path  = "/publisherId"
  throughput          = 0  # Serverless, no provisioned throughput

  unique_key {
    paths = ["/id"]
  }

  indexing_policy {
    indexing_mode = "Consistent"

    included_path {
      path = "/*"
    }

    excluded_path {
      path = "/\"_etag\"/?"
    }
  }

  default_ttl_seconds = 2592000  # 30 days
}

# Status/agents container (for tracking agent state)
resource "azurerm_cosmosdb_sql_container" "agent_state" {
  name                = "agent-state"
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.articles.name
  resource_group_name = var.resource_group_name
  partition_key_path  = "/agentId"
  throughput          = 0  # Serverless

  indexing_policy {
    indexing_mode = "Consistent"

    included_path {
      path = "/*"
    }
  }

  default_ttl_seconds = 604800  # 7 days
}

output "cosmos_endpoint" {
  value = azurerm_cosmosdb_account.main.endpoint
}

output "cosmos_account_name" {
  value = azurerm_cosmosdb_account.main.name
}

output "cosmos_id" {
  value = azurerm_cosmosdb_account.main.id
}
