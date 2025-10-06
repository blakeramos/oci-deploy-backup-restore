# IAM Configuration for Backup Service
# Creates dynamic groups and policies for instance principals

# Dynamic group for backup instances
resource "oci_identity_dynamic_group" "backup_instances" {
  compartment_id = var.tenancy_ocid
  name           = "${var.display_name_prefix}-backup-dg"
  description    = "Dynamic group for backup service instances"
  
  # Match instances in the backup instance pool
  matching_rule = "ANY {instance.compartment.id = '${var.compartment_ocid}', instance.id = '${oci_core_instance_pool.pool.id}'}"
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "Purpose" = "BackupServiceAuth"
    }
  )
}

# Comprehensive IAM policy for backup operations
resource "oci_identity_policy" "backup_service_policy" {
  compartment_id = var.compartment_ocid
  name           = "${var.display_name_prefix}-backup-policy"
  description    = "Allows backup service to manage compute, storage, and encryption"
  
  statements = [
    # Compute permissions
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to manage instance-family in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to manage volume-family in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to manage volume-backups in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to manage boot-volume-backups in compartment id ${var.compartment_ocid}",
    
    # Storage permissions
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to manage object-family in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to manage buckets in compartment id ${var.compartment_ocid}",
    
    # Vault/KMS permissions
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to use keys in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to use key-delegate in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to manage vaults in compartment id ${var.compartment_ocid}",
    
    # Monitoring permissions
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to use metrics in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to use alarms in compartment id ${var.compartment_ocid}",
    
    # Notification permissions
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to use ons-topics in compartment id ${var.compartment_ocid}",
    
    # Instance pool permissions
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to manage instance-pools in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to manage instance-configurations in compartment id ${var.compartment_ocid}",
    
    # Networking permissions
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to use virtual-network-family in compartment id ${var.compartment_ocid}",
    
    # Tagging permissions
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_instances.name} to use tag-namespaces in compartment id ${var.compartment_ocid}"
  ]
  
  freeform_tags = var.freeform_tags
}

# Service policy for OCI services to interact with KMS
resource "oci_identity_policy" "service_kms_policy" {
  compartment_id = var.tenancy_ocid
  name           = "${var.display_name_prefix}-service-kms-policy"
  description    = "Allows OCI services to use KMS keys for encryption"
  
  statements = [
    # Block Storage service needs to use KMS for encrypted volumes
    "Allow service blockstorage to use keys in compartment id ${var.compartment_ocid}",
    "Allow service blockstorage to use key-delegate in compartment id ${var.compartment_ocid}",
    
    # Object Storage service needs to use KMS for encrypted buckets
    "Allow service objectstorage-${var.region} to use keys in compartment id ${var.compartment_ocid}",
    "Allow service objectstorage-${var.region} to use key-delegate in compartment id ${var.compartment_ocid}",
    
    # FssOc1 (File Storage) service for potential future use
    "Allow service FssOc1 to use keys in compartment id ${var.compartment_ocid} where target.key.id = '${oci_kms_key.backup_master_key.id}'"
  ]
  
  freeform_tags = var.freeform_tags
}

# Policy for cross-region replication (if enabled)
resource "oci_identity_policy" "cross_region_replication" {
  count = var.enable_cross_region_replication ? 1 : 0
  
  compartment_id = var.tenancy_ocid
  name           = "${var.display_name_prefix}-cross-region-policy"
  description    = "Allows cross-region backup replication"
  
  statements = [
    "Allow service objectstorage-${var.region} to manage object-family in compartment id ${var.compartment_ocid}",
    "Allow service objectstorage-${var.dr_region} to manage object-family in compartment id ${var.compartment_ocid}",
    "Define tenancy replication as ${var.tenancy_ocid}",
    "Allow service objectstorage-${var.region}, objectstorage-${var.dr_region} to manage object-family in tenancy replication"
  ]
  
  freeform_tags = var.freeform_tags
}

# Tag namespace for backup operations (for better cost tracking and organization)
resource "oci_identity_tag_namespace" "backup_tags" {
  compartment_id = var.compartment_ocid
  name           = "${var.display_name_prefix}-tags"
  description    = "Tag namespace for backup operations"
  
  is_retired = false
  
  freeform_tags = var.freeform_tags
}

# Defined tags for backup tracking
resource "oci_identity_tag" "backup_type" {
  tag_namespace_id = oci_identity_tag_namespace.backup_tags.id
  name             = "BackupType"
  description      = "Type of backup (Full, Incremental, Differential)"
  
  validator {
    validator_type = "ENUM"
    values         = ["Full", "Incremental", "Differential"]
  }
  
  is_retired = false
}

resource "oci_identity_tag" "backup_policy" {
  tag_namespace_id = oci_identity_tag_namespace.backup_tags.id
  name             = "BackupPolicy"
  description      = "Backup policy applied to this resource"
  
  validator {
    validator_type = "DEFAULT"
    values         = ["Daily", "Weekly", "Monthly", "Custom"]
  }
  
  is_retired = false
}

resource "oci_identity_tag" "retention_class" {
  tag_namespace_id = oci_identity_tag_namespace.backup_tags.id
  name             = "RetentionClass"
  description      = "Retention classification for compliance"
  
  validator {
    validator_type = "ENUM"
    values         = ["Standard", "Extended", "LongTerm", "Permanent"]
  }
  
  is_retired = false
}

# Outputs
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
