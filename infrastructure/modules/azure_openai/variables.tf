variable "resource_prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "sku_name" {
  type    = string
  default = "S0"
}

variable "gpt4o_deployment" {
  type    = bool
  default = true
}

variable "gpt4o_mini_deployment" {
  type    = bool
  default = true
}

variable "dalle_deployment" {
  type    = bool
  default = true
}

variable "tags" {
  type = map(string)
}
