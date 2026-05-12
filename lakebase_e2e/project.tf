resource "databricks_postgres_project" "this" {
  project_id = local.project_id

  spec = {
    pg_version                 = 17
    display_name               = "Future Fund - ${title(var.domain)} (${upper(var.environment)})"
    history_retention_duration = "2592000s"

    default_endpoint_settings = {
      autoscaling_limit_min_cu = 1.0
      autoscaling_limit_max_cu = 8.0
      suspend_timeout_duration = "86400s"
    }
  }
}
