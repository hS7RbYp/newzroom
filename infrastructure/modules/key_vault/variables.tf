variable "resource_prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "current_principal_id" {
  type = string
  description = "Principal ID of current user/service principal"
}

variable "foundry_principal_id" {
  type = string
  description = "Principal ID of Azure Foundry Agent Service"
}

variable "openai_key" {
  type      = string
  sensitive = true
}

variable "cosmos_key" {
  type      = string
  sensitive = true
}

variable "search_key" {
  type      = string
  sensitive = true
}

variable "tags" {
  type = map(string)
}
