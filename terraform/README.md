# Terraform Deployment Instructions

## Prerequisites
- Terraform v1.3+
- OCI CLI or API keys configured

## Usage
```bash
cd terraform
terraform init
terraform plan -var="tenancy_ocid=..." -var="compartment_ocid=..." -var="image_id=..." -var="ssh_public_key=$(cat ~/.ssh/id_rsa.pub)"
terraform apply
```

## Features
- VCN, subnet, IGW, route tables, security list
- Object Storage bucket for backups
- Instance pool with autoscaling (CPU utilization)
- Flexible compute shapes for vertical scaling
- Block volumes with Dynamic Performance Scaling (Auto_tuned)
