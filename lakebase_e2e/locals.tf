locals {
  project_id = "futurefund-${var.domain}"

  common_tags = {
    owner       = "futurefund"
    domain      = var.domain
    environment = var.environment
    cost_center = var.cost_center
    managed_by  = "terraform"
  }
}
