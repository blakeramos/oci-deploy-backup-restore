# Enhanced Storage Configuration with Immutable Backups and Lifecycle Management

# Immutable backup vault with retention locks (ransomware protection)
resource "oci_objectstorage_bucket" "immutable_backup_vault" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "${var.display_name_prefix}-immutable-vault"
  access_type    = "NoPublicAccess"
  
  versioning = "Enabled" # Keep version history
  
  # Server-side encryption with KMS
  kms_key_id = oci_kms_key.object_storage_key.id
  
  # Retention rule - backups cannot be deleted for 90 days (WORM compliance)
  retention_rules {
    display_name = "ransomware-protection-90d"
    
    duration {
      time_amount = 90
      time_unit   = "DAYS"
    }
    
    # Lock the retention rule after 24 hours (cannot be modified/deleted)
    time_rule_locked = timeadd(timestamp(), "24h")
  }

  freeform_tags = merge(
    var.freeform_tags,
    {
      "Purpose"      = "ImmutableBackupVault",
      "Security"     = "WORM-Compliant",
      "Retention"    = "90-days",
      "Ransomware"   = "Protected"
    }
  )
}

# Standard backup bucket with lifecycle policies
resource "oci_objectstorage_bucket" "backup_storage" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "${var.display_name_prefix}-backup-storage"
  access_type    = "NoPublicAccess"
  
  versioning = "Enabled"
  
  # Encryption with KMS
  kms_key_id = oci_kms_key.object_storage_key.id
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "Purpose"  = "BackupStorage",
      "Tiering"  = "Enabled"
    }
  )
}

# Lifecycle policy for automatic tiering (cost optimization)
resource "oci_objectstorage_object_lifecycle_policy" "backup_lifecycle" {
  bucket    = oci_objectstorage_bucket.backup_storage.name
  namespace = data.oci_objectstorage_namespace.ns.namespace

  # Archive backups older than 30 days (80% cost reduction)
  rules {
    action      = "ARCHIVE"
    is_enabled  = true
    name        = "archive-old-backups"
    time_amount = 30
    time_unit   = "DAYS"
    target      = "objects"
    
    object_name_filter {
      inclusion_prefixes = ["backup-"]
    }
  }

  # Move to Infrequent Access after 7 days (40% cost reduction)
  rules {
    action      = "INFREQUENT_ACCESS"
    is_enabled  = true
    name        = "tier-to-infrequent-access"
    time_amount = 7
    time_unit   = "DAYS"
    target      = "objects"
    
    object_name_filter {
      inclusion_prefixes = ["backup-"]
    }
  }

  # Delete backups older than retention period
  rules {
    action      = "DELETE"
    is_enabled  = var.enable_auto_delete
    name        = "delete-expired-backups"
    time_amount = var.backup_retention_days
    time_unit   = "DAYS"
    target      = "objects"
    
    object_name_filter {
      inclusion_prefixes = ["backup-"]
    }
  }

  # Archive logs after 90 days
  rules {
    action      = "ARCHIVE"
    is_enabled  = true
    name        = "archive-old-logs"
    time_amount = 90
    time_unit   = "DAYS"
    target      = "objects"
    
    object_name_filter {
      inclusion_prefixes = ["logs-"]
    }
  }
}

# Metadata bucket for backup catalog and indices
resource "oci_objectstorage_bucket" "backup_metadata" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "${var.display_name_prefix}-metadata"
  access_type    = "NoPublicAccess"
  
  versioning = "Enabled"
  
  # Fast tier - no archiving for metadata
  storage_tier = "Standard"
  
  kms_key_id = oci_kms_key.object_storage_key.id
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "Purpose" = "BackupMetadata"
    }
  )
}

# Enhanced backup repository block volume with auto-tuning
resource "oci_core_volume" "backup_repository" {
  compartment_id      = var.compartment_ocid
  availability_domain = var.availability_domain != "" ? var.availability_domain : data.oci_identity_availability_domain.ad.name
  display_name        = "${var.display_name_prefix}-backup-repo"
  
  size_in_gbs = var.backup_repo_volume_size_gbs
  
  # OCI's secret sauce - automatic performance tuning
  vpus_per_gb = var.backup_repo_vpus_per_gb
  
  # Enable auto-tuned performance (adjusts IOPS/throughput automatically)
  auto_tuned_vpus_per_gb = var.enable_auto_tuned_storage ? "true" : "false"
  
  # Encryption with KMS
  kms_key_id = oci_kms_key.volume_backup_key.id
  
  # Enable backup policy
  is_auto_tune_enabled = true
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "Purpose"         = "BackupRepository",
      "PerformanceMode" = "Auto-Tuned",
      "Encryption"      = "KMS-HSM"
    }
  )
}

# Backup volume group for consistent snapshots
resource "oci_core_volume_group" "backup_volume_group" {
  compartment_id      = var.compartment_ocid
  availability_domain = var.availability_domain != "" ? var.availability_domain : data.oci_identity_availability_domain.ad.name
  display_name        = "${var.display_name_prefix}-backup-vg"
  
  source_details {
    type       = "volumeIds"
    volume_ids = [oci_core_volume.backup_repository.id]
  }
  
  freeform_tags = var.freeform_tags
}

# Cross-region replication for disaster recovery
resource "oci_objectstorage_replication_policy" "backup_dr_replication" {
  count = var.enable_cross_region_replication ? 1 : 0
  
  bucket              = oci_objectstorage_bucket.immutable_backup_vault.name
  destination_bucket  = "${var.display_name_prefix}-immutable-vault-dr"
  destination_region  = var.dr_region
  name                = "${var.display_name_prefix}-dr-replication"
  namespace           = data.oci_objectstorage_namespace.ns.namespace
}

# Data source for availability domain
data "oci_identity_availability_domain" "ad" {
  compartment_id = var.compartment_ocid
  ad_number      = 1
}

# Outputs
output "immutable_vault_name" {
  description = "Name of the immutable backup vault"
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
