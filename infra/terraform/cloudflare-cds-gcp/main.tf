terraform {
  required_version = ">= 1.9.3"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.17.0"
    }
  }
}

provider "google" {
  project = var.project_id
}

module "cloudflare_cds" {
  source     = "git::https://github.com/cloudflare/cf-product-infrastructure-templates.git//cds/terraform/gcp?ref=cds-latest"
  project_id = var.project_id
  region     = var.region
}
