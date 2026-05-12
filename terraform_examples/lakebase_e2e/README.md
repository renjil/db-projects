# Lakebase Autoscaling Terraform - End-to-End Example

End-to-end Terraform template for deploying [Databricks Lakebase Autoscaling](https://docs.databricks.com/aws/en/oltp/projects/) (managed Postgres with scale-to-zero) using the official [`databricks/databricks`](https://registry.terraform.io/providers/databricks/databricks/latest/docs) provider.

This example is scoped to **Lakebase only** - Postgres project, branches, endpoints, roles, database, UC registration, and one Delta-to-Postgres synced table. App deployment, model serving, and other Databricks features are intentionally out of scope - integrate them separately once Lakebase is up.

## What this deploys

| # | Resource | Purpose |
|---|---|---|
| 1 | `databricks_postgres_project` | PG17, 30-day PITR, project-level default endpoint settings (CU 1-8, 24h suspend) |
| 2 | `databricks_postgres_branch` (`main`) | Protected, no-expiry. Note: the project also auto-creates a `production` default branch which is **not** managed by this Terraform - `main` is created as a peer. |
| 3 | `databricks_postgres_branch` (`dev`) | 14-day TTL, scale-to-zero. Demonstrates copy-on-write env branching. |
| 4 | `databricks_postgres_endpoint` (`main_primary`) | HA: 2 nodes, readable secondaries, no-suspend, CU 1-9 |
| 5 | `databricks_postgres_endpoint` (`main_read_replica`) | Read-only, scale-to-zero (10min), CU 0.5-8 |
| 6 | `databricks_postgres_endpoint` (`dev_primary`) | Read-write, scale-to-zero (5min), CU 0.5-2 |
| 7 | `databricks_postgres_role` (`app_owner`) | Postgres role bound to a service principal, SUPERUSER, `LAKEBASE_OAUTH_V1` |
| 8 | `databricks_postgres_role` (`analyst_group`) | Postgres role bound to an existing Databricks group, read-only |
| 9 | `databricks_postgres_database` (`app`) | Logical Postgres database owned by `app_owner` |
| 10 | `databricks_permissions` | Workspace-level CAN_USE on the project for both the SP and the analyst group (see "Two layers of access" below) |
| 11 | `databricks_postgres_catalog` | Registers the Lakebase database as a Unity Catalog catalog |
| 12 | `databricks_postgres_synced_table` | Snapshot sync of a Delta table into the Lakebase database |

## File layout

```
lakebase_e2e/
├── README.md
├── versions.tf            # provider pin + remote backend placeholder
├── providers.tf
├── variables.tf
├── locals.tf
├── project.tf
├── branches.tf            # main (protected) + dev (TTL)
├── endpoints.tf           # HA primary + read replica + dev
├── roles_and_database.tf  # Postgres-level: SP role + group role + database
├── permissions.tf         # Workspace-level: CAN_USE on the project
├── catalog.tf             # Unity Catalog registration
├── synced_table.tf        # Delta -> Postgres sync example
└── outputs.tf
```

## Two layers of access (important)

Lakebase has two separate permission layers. Both are needed for a principal to actually read/write data:

| Layer | What it grants | Where to see it | TF resource in this example |
|---|---|---|---|
| **A. Workspace ACL on the project** | The right to "use" the project at all - connect to endpoints, see branches, etc. | Project's **Permissions** tab in the Databricks UI | `databricks_permissions` (`permissions.tf`) |
| **B. Postgres role inside the branch** | The Postgres-level SQL identity (what `current_user` returns and what GRANTs are wired to) | psql `\du`, or branch Roles UI | `databricks_postgres_role` (`roles_and_database.tf`) |

Granting layer B without layer A leaves principals unable to even connect. This example wires both for the SP and the group.

## Prerequisites

1. **Terraform >= 1.5**
2. **OAuth M2M service principal for Terraform** in the target workspace, with permission to manage Lakebase resources. Credentials via `terraform.tfvars` or env vars:
   ```bash
   export DATABRICKS_HOST="https://<workspace>.cloud.databricks.com"
   export DATABRICKS_CLIENT_ID="<sp-application-id>"
   export DATABRICKS_CLIENT_SECRET="<sp-secret>"
   ```
3. **`CREATE CATALOG` on the workspace's UC metastore** for the principal running `terraform apply` (required by `databricks_postgres_catalog`). A metastore admin can grant this with:
   ```sql
   GRANT CREATE CATALOG ON METASTORE TO `<principal>`;
   ```
4. **A service principal** that will own the Lakebase database (`db_owner_service_principal_application_id`). Granted SUPERUSER in Postgres and CAN_USE on the project.
5. **An existing Databricks group** (default `lakebase-analysts`) that gets read-only Postgres access and CAN_USE on the project.
6. **A source Delta table** in Unity Catalog at `<uc_source_catalog>.<uc_source_schema>.<uc_source_table>` with the primary key column(s) you specify. The synced table reads from this.
7. **A remote state backend** (S3/Azure Blob/GCS) - **required**, Autoscaling has no drift detection so local state is unsafe. The example pins an `s3` backend with placeholder values in `versions.tf` - replace before `terraform init`.

## Usage

```bash
# 1. Configure variables
cp terraform.tfvars.example terraform.tfvars
$EDITOR terraform.tfvars

# 2. Configure remote state backend
$EDITOR versions.tf   # replace REPLACE-ME placeholders

# 3. Init (configures backend, downloads provider)
terraform init

# 4. Review plan
terraform plan

# 5. Apply
terraform apply

# 6. Connect to Lakebase using outputs
terraform output -raw postgres_connection_string_primary
```

## Three behaviours to know before applying

1. **No drift detection** - changes made outside Terraform will not be picked up. Pick TF or UI as your source of truth.
2. **Remote state is mandatory** - configured via the `backend "s3"` block in `versions.tf`.
3. **`spec` vs `status`** - `spec` is intent, `status` is computed. Removing a field from `spec` does NOT revert the server value.

## Destroying resources

The `main` branch is created with `is_protected = true`. Lakebase refuses to delete endpoints attached to a protected branch, so a plain `terraform destroy` will fail with:

```
endpoint cannot be deleted for a protected branch
```

To tear down the deployment, flip the protection off first:

1. In `branches.tf`, change `is_protected = true` to `false` on `databricks_postgres_branch.main`.
2. Apply that single change to lift protection:
   ```bash
   terraform apply -target=databricks_postgres_branch.main
   ```
3. Now destroy as normal:
   ```bash
   terraform destroy
   ```

## Scaling this pattern

To deploy multiple business domains (e.g. portfolio, risk, esg):

- Wrap this folder as a Terraform module and call it once per domain with different `var.domain` and `var.uc_source_*` values, or
- Duplicate the resource blocks with different `var.domain` values per project.

## References

- [Get started with Terraform for Lakebase](https://docs.databricks.com/aws/en/oltp/projects/automate-with-terraform)
- [Lakebase Autoscaling API guide](https://docs.databricks.com/aws/en/oltp/projects/api-usage)
- [`databricks_postgres_project` provider doc](https://github.com/databricks/terraform-provider-databricks/blob/main/docs/resources/postgres_project.md)
- [`databricks_permissions` provider doc](https://github.com/databricks/terraform-provider-databricks/blob/main/docs/resources/permissions.md)
