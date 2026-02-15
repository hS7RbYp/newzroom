variable "resource_prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "sku" {
  type    = string
  default = "standard"
}

variable "replicas" {
  type    = number
  default = 3

  validation {
    condition     = var.replicas >= 1 && var.replicas <= 12
    error_message = "Replicas must be between 1 and 12"
  }
}

variable "partitions" {
  type    = number
  default = 1

  validation {
    condition     = var.partitions >= 1 && var.partitions <= 12
    error_message = "Partitions must be between 1 and 12"
  }
}

variable "public_network_access" {
  type    = bool
  default = true
}

variable "tags" {
  type = map(string)
}
