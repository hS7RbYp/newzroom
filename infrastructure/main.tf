terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "~> 1.10"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
    cognitive_account {
      purge_soft_delete_on_destroy = false
    }
  }
}

provider "azapi" {
  # Uses AZURE_SUBSCRIPTION_ID environment variable
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.azure_region

  tags = local.common_tags
}

# Data source for current user
data "azurerm_client_config" "current" {}

# ============================================================================
# LOCAL VARIABLES & TAGS
# ============================================================================
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    CreatedDate = timestamp()
    ManagedBy   = "Terraform"
    Phase       = var.phase
  }

  resource_prefix = "${var.project_name}-${var.environment}"
}

# ============================================================================
# OUTPUTS
# ============================================================================
output "resource_group_id" {
  value = azurerm_resource_group.main.id
}

output "resource_group_name" {
  value = azurerm_resource_group.main.name
}
