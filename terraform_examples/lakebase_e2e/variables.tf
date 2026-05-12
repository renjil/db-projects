variable "databricks_host" {
  description = "Workspace URL, e.g. https://adb-1234567890.0.azuredatabricks.net"
  type        = string
}

variable "databricks_client_id" {
  description = "OAuth M2M service principal application ID used by Terraform itself"
  type        = string
  sensitive   = true
}

variable "databricks_client_secret" {
  description = "OAuth M2M service principal client secret used by Terraform itself"
  type        = string
  sensitive   = true
}

variable "org_prefix" {
  description = "Short organisation/team identifier used as the prefix for the Lakebase project name and tag values. Lowercase alphanumeric + underscore only (no hyphens - UC catalog names cannot contain hyphens)."
  type        = string
  default     = "acme"

  validation {
    condition     = can(regex("^[a-z0-9_]+$", var.org_prefix))
    error_message = "org_prefix must contain only lowercase letters, digits, and underscores."
  }
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

variable "db_owner_service_principal_application_id" {
  description = "Application ID (UUID) of the service principal that owns the Lakebase database. Granted SUPERUSER inside the Postgres branch, AND CAN_USE on the workspace project."
  type        = string
}

variable "analyst_group_display_name" {
  description = "Existing Databricks group whose members get read-only Postgres access AND workspace-level CAN_USE on the project."
  type        = string
  default     = "lakebase-analysts"
}

variable "uc_source_catalog" {
  description = "Unity Catalog catalog hosting the source Delta table to be synced into Lakebase"
  type        = string
  default     = "main"
}

variable "uc_source_schema" {
  description = "Unity Catalog schema hosting the source Delta table to be synced into Lakebase"
  type        = string
  default     = "default"
}

variable "uc_source_table" {
  description = "Source Delta table name (within uc_source_catalog.uc_source_schema) to be synced into Lakebase. Must exist before terraform apply."
  type        = string
}

variable "synced_table_primary_key_columns" {
  description = "Primary key column(s) in the source Delta table. Required for the synced table - must uniquely identify a row."
  type        = list(string)
}
