resource "databricks_postgres_synced_table" "this" {
  synced_table_id = "${databricks_postgres_catalog.app.catalog_id}.public.${var.uc_source_table}_synced"

  spec = {
    source_table_full_name             = "${var.uc_source_catalog}.${var.uc_source_schema}.${var.uc_source_table}"
    primary_key_columns                = var.synced_table_primary_key_columns
    scheduling_policy                  = "SNAPSHOT"
    postgres_database                  = databricks_postgres_database.app.spec.postgres_database
    branch                             = databricks_postgres_branch.main.name
    create_database_objects_if_missing = true

    new_pipeline_spec = {
      storage_catalog = var.uc_source_catalog
      storage_schema  = var.uc_source_schema
    }
  }
}
