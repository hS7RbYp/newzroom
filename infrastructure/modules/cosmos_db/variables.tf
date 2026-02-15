variable "resource_prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "consistency_level" {
  type    = string
  default = "Session"
}

variable "backup_retention_hours" {
  type    = number
  default = 168  # 7 days
}

variable "enable_analytics" {
  type    = bool
  default = true
}

variable "tags" {
  type = map(string)
}
