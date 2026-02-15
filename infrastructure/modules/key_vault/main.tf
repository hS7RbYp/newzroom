# Azure Key Vault Module

resource "azurerm_key_vault" "main" {
  name                = "kv-${var.resource_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  sku_name            = "standard"

  enabled_for_deployment          = true
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  enable_rbac_authorization       = true
  purge_protection_enabled        = true
  soft_delete_retention_days      = 90

  tags = var.tags
}

# Store OpenAI key
resource "azurerm_key_vault_secret" "openai_key" {
  name         = "openai-key"
  value        = var.openai_key
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_role_assignment.self_secrets
  ]
}

# Store Cosmos db key
resource "azurerm_key_vault_secret" "cosmos_key" {
  name         = "cosmos-key"
  value        = var.cosmos_key
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_role_assignment.self_secrets
  ]
}

# Store AI Search key
resource "azurerm_key_vault_secret" "search_key" {
  name         = "search-key"
  value        = var.search_key
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_role_assignment.self_secrets
  ]
}

# RBAC role assignment for current user (to manage the vault)
resource "azurerm_role_assignment" "self_secrets" {
  scope              = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id       = var.current_principal_id
}

# RBAC role assignment for Foundry service
resource "azurerm_role_assignment" "foundry_secrets" {
  scope              = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id       = var.foundry_principal_id
}

output "key_vault_id" {
  value = azurerm_key_vault.main.id
}

output "key_vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}
