locals {
  project_id = "${var.org_prefix}-${var.domain}"

  common_tags = {
    owner       = var.org_prefix
    domain      = var.domain
    environment = var.environment
    cost_center = var.cost_center
    managed_by  = "terraform"
  }
}
