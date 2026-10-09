# Cloudflare CDS on GCP

This folder contains Terraform source for deploying Cloudflare CDS on Google Cloud.

## Prerequisites

- Terraform >= 1.9.3
- Google Cloud project with billing enabled
- Authenticated `gcloud` session or service account credentials

## Usage

```powershell
cd infra/terraform/cloudflare-cds-gcp
terraform init
terraform validate
terraform plan
terraform apply
```

## Notes

- Do not commit generated `.terraform` directories or state files.
- Keep `terraform.tfvars` aligned with the target project and region.
