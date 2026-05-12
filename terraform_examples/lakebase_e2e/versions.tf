terraform {
  required_version = ">= 1.5"

  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.112"
    }
  }

  # Remote state is REQUIRED - Lakebase Autoscaling resources have no drift detection,
  # so local state is unsafe for any multi-operator workflow.
  # Replace the placeholder bucket/table/region below with your own (or swap for azurerm / gcs).
  backend "s3" {
    bucket         = "REPLACE-ME-tfstate"
    key            = "lakebase/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "REPLACE-ME-tfstate-lock"
    encrypt        = true
  }
}
