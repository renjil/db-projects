resource "databricks_postgres_synced_table" "holdings" {
  synced_table_id = "${databricks_postgres_catalog.app.catalog_id}.public.holdings_synced"

  spec = {
    source_table_full_name             = "${var.uc_source_catalog}.${var.uc_source_schema}.holdings"
    primary_key_columns                = ["holding_id"]
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
