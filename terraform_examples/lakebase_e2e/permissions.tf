# Workspace-level access to the Lakebase project.
# This is separate from the Postgres roles in roles_and_database.tf:
#   - This file grants principals the right to USE the project at the workspace level
#     (without this, they can't connect to the project at all).
#   - The Postgres roles grant SQL-level identity inside the database.
# Both layers are needed for a principal to actually read/write data.
resource "databricks_permissions" "project_usage" {
  database_project_name = databricks_postgres_project.this.project_id

  access_control {
    service_principal_name = var.db_owner_service_principal_application_id
    permission_level       = "CAN_USE"
  }

  access_control {
    group_name       = var.analyst_group_display_name
    permission_level = "CAN_USE"
  }
}
