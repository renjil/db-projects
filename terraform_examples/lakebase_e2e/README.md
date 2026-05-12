# Future Fund - Lakebase Autoscaling Terraform (End-to-End)

End-to-end Terraform template for deploying Lakebase Autoscaling at Future Fund. Combines patterns from:

- Databricks Field Engineering internal demo `lakebase_financial_commodities_demo`
- Public reference `mousastech/sgp`
- Official provider docs `databricks/terraform-provider-databricks`

## What this deploys

A single business-domain Lakebase project with:

- 1 Lakebase Autoscaling **project** (`futurefund-<domain>`) with project-level default endpoint settings + 30-day PITR
- 2 **branches**: `main` (protected, always-on) and `dev` (TTL-bound, scale-to-zero)
- 3 **endpoints**: HA primary RW (2 nodes + readable secondaries), prod read-replica, dev primary RW
- 1 **app database** + 1 **service principal role** (OAuth M2M, SUPERUSER)
- 1 **human analyst role** (USER, read-only group)
- 1 **Unity Catalog catalog** registering the Postgres database
- 1 **synced table** example (Delta → Postgres, snapshot scheduling)
- 1 **Databricks App** consuming Lakebase via the resource block
- Outputs for connection strings, hostnames, app URL

## File layout

```
lakebase_terraform_e2e/
├── README.md
├── versions.tf            # provider pins + S3 remote backend
├── providers.tf
├── variables.tf
├── locals.tf
├── project.tf             # databricks_postgres_project
├── branches.tf            # main + dev branches
├── endpoints.tf           # primary HA + read replica + dev
├── roles_and_database.tf  # service principal + human roles, app database
├── catalog.tf             # Unity Catalog registration
├── synced_table.tf        # Delta -> Postgres sync example
├── app.tf                 # Databricks App consuming Lakebase
└── outputs.tf
```

## Prerequisites

1. Terraform >= 1.5
2. An OAuth M2M service principal in the target workspace with permission to manage Lakebase resources
3. Environment variables exported:
   ```bash
   export DATABRICKS_HOST="https://<workspace>.cloud.databricks.com"
   export DATABRICKS_CLIENT_ID="<sp-application-id>"
   export DATABRICKS_CLIENT_SECRET="<sp-secret>"
   ```
4. A remote state backend (S3/Azure Blob/GCS) - **required**, Autoscaling has no drift detection so local state is unsafe

## Usage

```bash
# 1. Edit terraform.tfvars (or pass -var flags) with futurefund-specific values
cp terraform.tfvars.example terraform.tfvars
$EDITOR terraform.tfvars

# 2. Init (configures backend, downloads provider)
terraform init

# 3. Review plan
terraform plan

# 4. Apply
terraform apply

# 5. Connect to Lakebase using outputs
terraform output -raw postgres_connection_string_primary
```

## Three behaviours to know before applying

1. **No drift detection** - changes made outside Terraform will not be picked up. Pick TF or UI as your source of truth.
2. **Remote state is mandatory** - configured via the `backend "s3"` block in `versions.tf`.
3. **`spec` vs `status`** - `spec` is intent, `status` is computed. Removing a field from `spec` does NOT revert the server value.

## Scaling this pattern

To deploy multiple business domains (FE financial commodities pattern):

- Wrap the whole module in `terraform-module/lakebase-project` and call it once per domain
- Or duplicate `project.tf` + `endpoints.tf` blocks with different `var.domain` values per project

## References

- [Get started with Terraform for Lakebase](https://docs.databricks.com/aws/en/oltp/projects/automate-with-terraform)
- [Lakebase Autoscaling API guide](https://docs.databricks.com/aws/en/oltp/projects/api-usage)
- [`databricks_postgres_project` provider doc](https://github.com/databricks/terraform-provider-databricks/blob/main/docs/resources/postgres_project.md)
