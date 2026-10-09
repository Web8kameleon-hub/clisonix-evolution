variable "project_id" {
  description = "The identifier for the project to which the Cloudflare CDS deployment is deployed"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy all resources"
  type        = string
}
