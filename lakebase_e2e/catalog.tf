resource "databricks_postgres_catalog" "app" {
  catalog_id = "ff_${var.domain}_app"

  spec = {
    postgres_database          = databricks_postgres_database.app.spec.postgres_database
    create_database_if_missing = false
    branch                     = databricks_postgres_branch.main.name
  }

  depends_on = [databricks_postgres_database.app]
}
