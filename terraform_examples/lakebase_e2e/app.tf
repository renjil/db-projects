resource "databricks_app" "this" {
  name        = "lakebase-${var.domain}-app"
  description = "${title(var.domain)} application backed by Lakebase Autoscaling"

  resources = [
    {
      name = "lakebase"
      database = {
        database_name = databricks_postgres_database.app.spec.postgres_database
        instance_name = databricks_postgres_project.this.name
        permission    = "CAN_CONNECT_AND_CREATE"
      }
    }
  ]

  compute_size = "MEDIUM"
}
