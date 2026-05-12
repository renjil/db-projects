resource "databricks_postgres_endpoint" "main_primary" {
  endpoint_id = "primary"
  parent      = databricks_postgres_branch.main.name

  spec = {
    endpoint_type            = "ENDPOINT_TYPE_READ_WRITE"
    no_suspension            = true
    autoscaling_limit_min_cu = 1.0
    autoscaling_limit_max_cu = 9.0

    group = {
      min                         = 2
      max                         = 2
      enable_readable_secondaries = true
    }
  }

  replace_existing = true
}

resource "databricks_postgres_endpoint" "main_read_replica" {
  endpoint_id = "read-replica"
  parent      = databricks_postgres_branch.main.name

  spec = {
    endpoint_type            = "ENDPOINT_TYPE_READ_ONLY"
    autoscaling_limit_min_cu = 0.5
    autoscaling_limit_max_cu = 8.0
    suspend_timeout_duration = "600s"
  }
}

resource "databricks_postgres_endpoint" "dev_primary" {
  endpoint_id = "primary"
  parent      = databricks_postgres_branch.dev.name

  spec = {
    endpoint_type            = "ENDPOINT_TYPE_READ_WRITE"
    autoscaling_limit_min_cu = 0.5
    autoscaling_limit_max_cu = 2.0
    suspend_timeout_duration = "300s"
  }

  replace_existing = true
}
