output "project_name" {
  description = "Lakebase project name (full resource path: projects/<project_id>)"
  value       = databricks_postgres_project.this.name
}

output "project_id" {
  description = "Lakebase project ID (short form, e.g. acme-portfolio)"
  value       = databricks_postgres_project.this.project_id
}

output "main_primary_host" {
  description = "Main branch primary read-write endpoint hostname"
  value       = databricks_postgres_endpoint.main_primary.status.hosts.host
}

output "main_read_replica_host" {
  description = "Main branch read-only replica hostname"
  value       = databricks_postgres_endpoint.main_read_replica.status.hosts.host
}

output "dev_primary_host" {
  description = "Dev branch primary endpoint hostname"
  value       = databricks_postgres_endpoint.dev_primary.status.hosts.host
}

output "postgres_connection_string_primary" {
  description = "Connection string for the main primary endpoint (Databricks OAuth handles auth; do not embed a password)"
  value       = "postgresql://${databricks_postgres_endpoint.main_primary.status.hosts.host}:5432/${databricks_postgres_database.app.spec.postgres_database}?sslmode=require"
}

output "uc_catalog_name" {
  description = "Unity Catalog catalog registered against the Lakebase database"
  value       = databricks_postgres_catalog.app.catalog_id
}
