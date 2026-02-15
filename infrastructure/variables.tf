variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "aan"

  validation {
    condition     = length(var.project_name) <= 10
    error_message = "Project name must be <= 10 characters"
  }
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}

variable "azure_region" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "phase" {
  description = "Implementation phase (0-4)"
  type        = string
  default     = "0"

  validation {
    condition     = contains(["0", "1", "2", "3", "4", "ga"], var.phase)
    error_message = "Phase must be 0, 1, 2, 3, 4, or ga"
  }
}

# ============================================================================
# AZURE OPENAI CONFIGURATION
# ============================================================================
variable "openai_sku_name" {
  description = "OpenAI SKU (Standard)"
  type        = string
  default     = "S0"
}

variable "gpt4o_deployment" {
  description = "Enable GPT-4o deployment"
  type        = bool
  default     = true
}

variable "gpt4o_mini_deployment" {
  description = "Enable GPT-4o-mini deployment"
  type        = bool
  default     = true
}

variable "dall_e_deployment" {
  description = "Enable DALL-E 3 deployment"
  type        = bool
  default     = true
}

# ============================================================================
# COSMOS DB CONFIGURATION
# ============================================================================
variable "cosmos_consistency_level" {
  description = "Cosmos DB consistency level"
  type        = string
  default     = "Session"

  validation {
    condition     = contains(["Strong", "BoundedStaleness", "Session", "ConsistentPrefix", "Eventual"], var.cosmos_consistency_level)
    error_message = "Invalid consistency level"
  }
}

variable "cosmos_max_throughput" {
  description = "Cosmos DB max throughput (autoscale)"
  type        = number
  default     = 4000

  validation {
    condition     = var.cosmos_max_throughput >= 1000 && var.cosmos_max_throughput <= 1000000
    error_message = "Throughput must be between 1000 and 1000000"
  }
}

# ============================================================================
# AZURE AI SEARCH CONFIGURATION
# ============================================================================
variable "search_sku" {
  description = "AI Search SKU"
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["free", "basic", "standard", "standard2", "standard3"], var.search_sku)
    error_message = "Invalid SKU"
  }
}

variable "search_partitions" {
  description = "Number of search partitions"
  type        = number
  default     = 1

  validation {
    condition     = var.search_partitions >= 1 && var.search_partitions <= 12
    error_message = "Partitions must be between 1 and 12"
  }
}

variable "search_replicas" {
  description = "Number of search replicas"
  type        = number
  default     = 3

  validation {
    condition     = var.search_replicas >= 1 && var.search_replicas <= 12
    error_message = "Replicas must be between 1 and 12"
  }
}

# ============================================================================
# NETWORK & SECURITY CONFIGURATION
# ============================================================================
variable "enable_public_network_access" {
  description = "Enable public network access"
  type        = bool
  default     = true
}

variable "enable_managed_identity" {
  description = "Enable managed service identity"
  type        = bool
  default     = true
}

# ============================================================================
# BACKUP & DISASTER RECOVERY
# ============================================================================
variable "backup_retention_days" {
  description = "Cosmos DB backup retention in days"
  type        = number
  default     = 7

  validation {
    condition     = var.backup_retention_days >= 7 && var.backup_retention_days <= 35
    error_message = "Retention must be between 7 and 35 days"
  }
}

variable "enable_analytics" {
  description = "Enable analytics and monitoring"
  type        = bool
  default     = true
}

# ============================================================================
# COST OPTIMIZATION
# ============================================================================
variable "enable_autoscale_cosmos" {
  description = "Enable autoscaling for Cosmos DB"
  type        = bool
  default     = true
}

variable "staging_domain" {
  description = "Staging environment domain"
  type        = string
  default     = ""
}

variable "prod_domain" {
  description = "Production environment domain"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
