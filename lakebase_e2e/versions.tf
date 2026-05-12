terraform {
  required_version = ">= 1.5"

  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.112"
    }
  }

  backend "s3" {
    bucket         = "futurefund-tfstate"
    key            = "lakebase/terraform.tfstate"
    region         = "ap-southeast-2"
    dynamodb_table = "futurefund-tfstate-lock"
    encrypt        = true
  }
}
