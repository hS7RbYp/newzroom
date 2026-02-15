variable "resource_prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "retention_days" {
  type    = number
  default = 90
}

variable "tags" {
  type = map(string)
}
