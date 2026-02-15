variable "resource_prefix" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "sku_size" {
  type    = string
  default = "Free"
}

variable "staging_domain" {
  type = string
  description = "Staging environment domain (e.g., staging.newsroom.example.com)"
}

variable "prod_domain" {
  type = string
  description = "Production environment domain (e.g., newsroom.example.com)"
}

variable "enable_prod_domain" {
  type    = bool
  default = true
}

variable "tags" {
  type = map(string)
}
