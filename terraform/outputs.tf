# Terraform Outputs - Enhanced OCI Backup Infrastructure

# === Networking Outputs ===
output "vcn_id" {
  description = "OCID of the VCN"
  value       = oci_core_virtual_network.vcn.id
}

output "subnet_id" {
  description = "OCID of the subnet"
  value       = oci_core_subnet.subnet.id
}

output "internet_gateway_id" {
  description = "OCID of the internet gateway"
  value       = oci_core_internet_gateway.igw.id
}

# === Compute Outputs ===
output "instance_pool_id" {
  description = "OCID of the instance pool"
  value       = oci_core_instance_pool.pool.id
}

output "instance_configuration_id" {
  description = "OCID of the instance configuration"
  value       = oci_core_instance_configuration.instance_config.id
}

output "autoscaling_configuration_id" {
  description = "OCID of the autoscaling configuration"
  value       = oci_autoscaling_auto_scaling_configuration.pool_autoscale.id
}

# === Storage Outputs ===
output "immutable_vault_name" {
  description = "Name of the immutable backup vault (ransomware protected)"
  value       = oci_objectstorage_bucket.immutable_backup_vault.name
}

output "backup_storage_name" {
  description = "Name of the standard backup storage bucket"
  value       = oci_objectstorage_bucket.backup_storage.name
}

output "metadata_bucket_name" {
  description = "Name of the metadata bucket"
  value       = oci_objectstorage_bucket.backup_metadata.name
}

output "backup_repository_id" {
  description = "OCID of the backup repository volume"
  value       = oci_core_volume.backup_repository.id
}

output "storage_namespace" {
  description = "Object storage namespace"
  value       = data.oci_objectstorage_namespace.ns.namespace
}

# === Security Outputs (KMS/Vault) ===
output "vault_id" {
  description = "OCID of the backup vault"
  value       = oci_kms_vault.backup_vault.id
}

output "master_key_id" {
  description = "OCID of the master encryption key"
  value       = oci_kms_key.backup_master_key.id
  sensitive   = true
}

output "volume_backup_key_id" {
  description = "OCID of the volume backup encryption key"
  value       = oci_kms_key.volume_backup_key.id
  sensitive   = true
}

output "object_storage_key_id" {
  description = "OCID of the object storage encryption key"
  value       = oci_kms_key.object_storage_key.id
  sensitive   = true
}

output "vault_management_endpoint" {
  description = "Management endpoint for the vault"
  value       = oci_kms_vault.backup_vault.management_endpoint
}

# === Monitoring Outputs ===
output "alert_topic_id" {
  description = "OCID of the backup alerts notification topic"
  value       = oci_ons_notification_topic.backup_alerts.id
}

output "monitoring_dashboard" {
  description = "Monitoring dashboard configuration (JSON)"
  value       = local.monitoring_dashboard
}

output "alarm_ids" {
  description = "OCIDs of all configured alarms"
  value = {
    backup_failure      = oci_monitoring_alarm.backup_job_failure.id
    high_duration       = oci_monitoring_alarm.high_backup_duration.id
    storage_capacity    = oci_monitoring_alarm.storage_capacity_warning.id
    cpu_high            = oci_monitoring_alarm.instance_pool_cpu_high.id
    validation_failure  = oci_monitoring_alarm.backup_validation_failure.id
    vault_access        = oci_monitoring_alarm.immutable_vault_access.id
    key_rotation        = oci_monitoring_alarm.key_rotation_needed.id
  }
}

# === IAM Outputs ===
output "dynamic_group_id" {
  description = "OCID of the backup service dynamic group"
  value       = oci_identity_dynamic_group.backup_instances.id
}

output "backup_policy_id" {
  description = "OCID of the backup service IAM policy"
  value       = oci_identity_policy.backup_service_policy.id
}

output "tag_namespace_id" {
  description = "OCID of the backup tag namespace"
  value       = oci_identity_tag_namespace.backup_tags.id
}

output "tag_keys" {
  description = "Tag keys for backup operations"
  value = {
    backup_type     = oci_identity_tag.backup_type.name
    backup_policy   = oci_identity_tag.backup_policy.name
    retention_class = oci_identity_tag.retention_class.name
  }
}

# === Summary Output ===
output "deployment_summary" {
  description = "Summary of the deployed backup infrastructure"
  value = {
    region                = var.region
    compartment_id        = var.compartment_ocid
    instance_pool_size    = "${var.instance_pool_min}-${var.instance_pool_max} instances"
    storage_encrypted     = "Yes (KMS HSM-backed)"
    immutable_backups     = "Yes (90-day retention lock)"
    monitoring_enabled    = "Yes (7 alarms configured)"
    auto_scaling_enabled  = "Yes (CPU-based)"
    auto_tuned_storage    = var.enable_auto_tuned_storage ? "Yes" : "No"
    cross_region_dr       = var.enable_cross_region_replication ? "Yes (${var.dr_region})" : "No"
    alert_email           = var.alert_email != "" ? "Configured" : "Not configured"
    alert_webhook         = var.alert_webhook_url != "" ? "Configured" : "Not configured"
  }
}

# === Quick Start Commands ===
output "quick_start_commands" {
  description = "Commands to get started with backup operations"
  value = <<-EOT
    
    === OCI DataProtect MVP - Quick Start ===
    
    1. SSH to an instance in the pool:
       oci compute instance list --compartment-id ${var.compartment_ocid} \
         --instance-pool-id ${oci_core_instance_pool.pool.id}
    
    2. Run a backup:
       cd /opt/backup
       python3 backup.py --compartment ${var.compartment_ocid} --instance <instance-ocid>
    
    3. View backups in Object Storage:
       oci os object list --bucket-name ${oci_objectstorage_bucket.backup_storage.name} \
         --namespace ${data.oci_objectstorage_namespace.ns.namespace}
    
    4. Check monitoring alarms:
       oci monitoring alarm list --compartment-id ${var.compartment_ocid}
    
    5. View encryption keys:
       oci kms management key list --compartment-id ${var.compartment_ocid} \
         --management-endpoint ${oci_kms_vault.backup_vault.management_endpoint}
    
    === Key Features Demonstrated ===
    ✅ Instance Principals (zero-key auth)
    ✅ Auto-tuned Block Storage
    ✅ Immutable Backups (ransomware protection)
    ✅ Hardware-backed Encryption (FIPS 140-2 Level 3)
    ✅ Automated Monitoring & Alerting
    ✅ Cost Optimization (lifecycle policies)
    ✅ Flexible Compute Shapes
    ✅ Auto-scaling Instance Pools
    
    For more information, see README.md
    
  EOT
}
