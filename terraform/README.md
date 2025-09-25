# OCI Terraform Deployment for Backup Orchestrator

This module deploys the infrastructure required to run the **OCI Backup & Restore (Python SDK)** service in a scalable and optimized way.

---

## Features

- **Networking**
  - Virtual Cloud Network (VCN)
  - Subnet, Route Table, Internet Gateway
  - Security List (SSH + egress)

- **Compute**
  - **Instance Configuration** using a **flexible shape** (e.g., `VM.Standard.E4.Flex`)
  - **Instance Pool** with autoscaling rules based on CPU utilization
  - Support for vertical scaling by adjusting OCPUs and memory in the shape config

- **Storage**
  - Block volume for backup repository with **Dynamic Performance Scaling** (`Auto_tuned`)
  - Object Storage bucket for metadata and lifecycle management

- **Autoscaling**
  - Policy to **scale out** when CPU > 70%
  - Policy to **scale in** when CPU < 25%
  - Configurable min, max, and initial pool sizes

---

## Prerequisites

- Terraform v1.3+
- OCI CLI/API key authentication, or instance principal with permissions
- Required variables defined (see `variables.tf`)

### IAM Policies

For instances in the pool to perform backups/restores, create a **Dynamic Group** and attach a policy, for example:

```hcl
Allow dynamic-group backup-dg to manage instance-family in compartment <compartment-name>
Allow dynamic-group backup-dg to manage volume-family in compartment <compartment-name>
Allow dynamic-group backup-dg to use buckets in compartment <compartment-name>
```

---

## Usage

1. Initialize Terraform
   ```bash
   terraform init
   ```

2. Plan deployment
   ```bash
   terraform plan \
     -var="tenancy_ocid=ocid1.tenancy.oc1..xxxxx" \
     -var="compartment_ocid=ocid1.compartment.oc1..yyyyy" \
     -var="image_id=ocid1.image.oc1..zzzzz" \
     -var="ssh_public_key=$(cat ~/.ssh/id_rsa.pub)"
   ```

3. Apply deployment
   ```bash
   terraform apply
   ```

---

## Key Variables

- `instance_shape` – flexible shape (default: `VM.Standard.E4.Flex`)
- `instance_ocpus` – number of OCPUs (default: 2)
- `instance_memory_in_gbs` – memory in GBs (default: 8)
- `instance_pool_min` – minimum instances in pool
- `instance_pool_max` – maximum instances in pool
- `instance_pool_initial_size` – initial instance count
- `backup_repo_volume_size_gbs` – backup repository block volume size

See `variables.tf` for full list.

---

## Notes

- **Dynamic Performance Scaling**: all block volumes are created with `block_volume_performance = "Auto_tuned"` to automatically adjust IOPS/throughput.  
- **Flexible Compute Shapes**: adjust OCPUs/memory by changing `instance_ocpus` and `instance_memory_in_gbs` without redeploying.  
- **Object Storage Lifecycle Rules**: can be applied to bucket to tier old backups to Infrequent Access or Archive storage.  

---

## Security Best Practices

- Use instance principals (Dynamic Groups) instead of embedding API keys.  
- Tag resources with `freeform_tags` for cost tracking.  
- Use OCI Vault for sensitive credentials and KMS for backup encryption keys.  

---

## References

- [OCI Terraform Provider](https://registry.terraform.io/providers/oracle/oci/latest)  
- [Flexible Shapes](https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm)  
- [Dynamic Block Volume Performance](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumeperformance.htm)  
- [Autoscaling](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/autoscalinginstancepools.htm)  
