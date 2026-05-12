resource "databricks_postgres_branch" "main" {
  branch_id = "main"
  parent    = databricks_postgres_project.this.name

  spec = {
    no_expiry    = true
    is_protected = true
  }

  replace_existing = true
}

resource "databricks_postgres_branch" "dev" {
  branch_id = "dev"
  parent    = databricks_postgres_project.this.name

  spec = {
    ttl = "1209600s"
  }
}
