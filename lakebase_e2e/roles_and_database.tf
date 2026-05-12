resource "databricks_postgres_role" "app_owner" {
  role_id = "app-owner"
  parent  = databricks_postgres_branch.main.name

  spec = {
    identity_type    = "SERVICE_PRINCIPAL"
    postgres_role    = var.app_service_principal_application_id
    auth_method      = "LAKEBASE_OAUTH_V1"
    membership_roles = ["DATABRICKS_SUPERUSER"]
  }
}

resource "databricks_postgres_role" "analyst_group" {
  role_id = "analyst-readonly"
  parent  = databricks_postgres_branch.main.name

  spec = {
    identity_type = "GROUP"
    postgres_role = var.analyst_group_display_name
  }
}

resource "databricks_postgres_database" "app" {
  database_id = "app"
  parent      = databricks_postgres_branch.main.name

  spec = {
    postgres_database = "app"
    role              = databricks_postgres_role.app_owner.name
  }
}
