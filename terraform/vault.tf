# OCI Vault (KMS) for Backup Encryption
# Provides hardware-backed encryption keys (FIPS 140-2 Level 3 certified)

resource "oci_kms_vault" "backup_vault" {
  compartment_id = var.compartment_ocid
  display_name   = "${var.display_name_prefix}-backup-vault"
  vault_type     = "DEFAULT" # Hardware-backed HSM
  freeform_tags  = merge(
    var.freeform_tags,
    {
      "Purpose" = "BackupEncryption",
      "Security" = "FIPS-140-2-Level-3"
    }
  )
}

resource "oci_kms_key" "backup_master_key" {
  compartment_id      = var.compartment_ocid
  display_name        = "${var.display_name_prefix}-master-key"
  management_endpoint = oci_kms_vault.backup_vault.management_endpoint

  key_shape {
    algorithm = "AES"
    length    = 256
  }

  protection_mode = "HSM" # Hardware Security Module backed

  freeform_tags = merge(
    var.freeform_tags,
    {
      "Purpose" = "MasterEncryptionKey",
      "KeyRotation" = "Enabled"
    }
  )
}

# Key for block volume backups
resource "oci_kms_key" "volume_backup_key" {
  compartment_id      = var.compartment_ocid
  display_name        = "${var.display_name_prefix}-volume-key"
  management_endpoint = oci_kms_vault.backup_vault.management_endpoint

  key_shape {
    algorithm = "AES"
    length    = 256
  }

  protection_mode = "HSM"

  freeform_tags = merge(
    var.freeform_tags,
    {
      "Purpose" = "VolumeBackupEncryption"
    }
  )
}

# Key for object storage encryption
resource "oci_kms_key" "object_storage_key" {
  compartment_id      = var.compartment_ocid
  display_name        = "${var.display_name_prefix}-object-key"
  management_endpoint = oci_kms_vault.backup_vault.management_endpoint

  key_shape {
    algorithm = "AES"
    length    = 256
  }

  protection_mode = "HSM"

  freeform_tags = merge(
    var.freeform_tags,
    {
      "Purpose" = "ObjectStorageEncryption"
    }
  )
}

# IAM Policy for backup instances to use KMS
resource "oci_identity_policy" "backup_kms_policy" {
  compartment_id = var.tenancy_ocid
  description    = "Allow backup instances to use KMS keys"
  name           = "${var.display_name_prefix}-kms-policy"

  statements = [
    "Allow dynamic-group ${var.display_name_prefix}-backup-dg to use keys in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${var.display_name_prefix}-backup-dg to use key-delegate in compartment id ${var.compartment_ocid}",
    "Allow service blockstorage to use keys in compartment id ${var.compartment_ocid}",
    "Allow service objectstorage-${var.region} to use keys in compartment id ${var.compartment_ocid}"
  ]
}

# Outputs for use in other modules
output "vault_id" {
  description = "OCID of the backup vault"
  value       = oci_kms_vault.backup_vault.id
}

output "master_key_id" {
  description = "OCID of the master encryption key"
  value       = oci_kms_key.backup_master_key.id
}

output "volume_backup_key_id" {
  description = "OCID of the volume backup encryption key"
  value       = oci_kms_key.volume_backup_key.id
}

output "object_storage_key_id" {
  description = "OCID of the object storage encryption key"
  value       = oci_kms_key.object_storage_key.id
}

output "vault_management_endpoint" {
  description = "Management endpoint for the vault"
  value       = oci_kms_vault.backup_vault.management_endpoint
}
