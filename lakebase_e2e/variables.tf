variable "databricks_host" {
  description = "Workspace URL, e.g. https://adb-1234567890.0.azuredatabricks.net"
  type        = string
}

variable "databricks_client_id" {
  description = "OAuth M2M service principal application ID"
  type        = string
  sensitive   = true
}

variable "databricks_client_secret" {
  description = "OAuth M2M service principal client secret"
  type        = string
  sensitive   = true
}

variable "domain" {
  description = "Business domain identifier (e.g. portfolio, risk, esg). Becomes the project suffix."
  type        = string
  default     = "portfolio"
}

variable "environment" {
  description = "Environment tag (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "cost_center" {
  description = "Cost-centre tag applied to all resources"
  type        = string
  default     = "data-platform"
}

variable "uc_source_catalog" {
  description = "Unity Catalog catalog hosting the source Delta tables for sync"
  type        = string
  default     = "main"
}

variable "uc_source_schema" {
  description = "Unity Catalog schema hosting the source Delta tables for sync"
  type        = string
  default     = "default"
}

variable "app_service_principal_application_id" {
  description = "Application ID of the service principal that the Databricks App runs as. This SP is granted SUPERUSER on the Lakebase database."
  type        = string
}

variable "analyst_group_display_name" {
  description = "Existing Databricks group whose members get read-only Postgres access"
  type        = string
  default     = "futurefund-analysts"
}
