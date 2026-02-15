# Azure Service Bus Module (Dead-Letter Queue & message routing)

resource "azurerm_servicebus_namespace" "main" {
  name                = "${var.resource_prefix}-sb"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.sku

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Topic: Dead Letter Queue
resource "azurerm_servicebus_topic" "dlq" {
  name         = "dead-letter-queue"
  namespace_id = azurerm_servicebus_namespace.main.id
  default_message_ttl = "P14D"  # 14 days
}

resource "azurerm_servicebus_subscription" "dlq_sub" {
  name               = "dlq-handler"
  topic_id           = azurerm_servicebus_topic.dlq.id
  max_delivery_count = 1
  lock_duration      = "PT5M"
}

# Topic: Agent Events
resource "azurerm_servicebus_topic" "agent_events" {
  name         = "agent-events"
  namespace_id = azurerm_servicebus_namespace.main.id
  default_message_ttl = "P1D"  # 1 day

  enable_partitioning = true
}

resource "azurerm_servicebus_subscription" "agent_events" {
  name               = "agent-subscribers"
  topic_id           = azurerm_servicebus_topic.agent_events.id
  max_delivery_count = 3
  lock_duration      = "PT1M"
}

# Topic: Quality Metrics (Judge feedback)
resource "azurerm_servicebus_topic" "quality_metrics" {
  name         = "quality-metrics"
  namespace_id = azurerm_servicebus_namespace.main.id
  default_message_ttl = "P30D"  # 30 days
}

resource "azurerm_servicebus_subscription" "quality_metrics" {
  name               = "metrics-analyzer"
  topic_id           = azurerm_servicebus_topic.quality_metrics.id
  max_delivery_count = 1
}

output "namespace_name" {
  value = azurerm_servicebus_namespace.main.name
}

output "namespace_id" {
  value = azurerm_servicebus_namespace.main.id
}

output "dlq_topic_id" {
  value = azurerm_servicebus_topic.dlq.id
}
