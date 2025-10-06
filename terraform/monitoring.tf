# OCI Monitoring and Alerting for Backup Operations

# Notification topic for backup alerts
resource "oci_ons_notification_topic" "backup_alerts" {
  compartment_id = var.compartment_ocid
  name           = "${var.display_name_prefix}-backup-alerts"
  description    = "Notification topic for backup job alerts"
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "Purpose" = "BackupAlerting"
    }
  )
}

# Email subscription for critical alerts
resource "oci_ons_subscription" "email_alerts" {
  count = var.alert_email != "" ? 1 : 0
  
  compartment_id = var.compartment_ocid
  topic_id       = oci_ons_notification_topic.backup_alerts.id
  protocol       = "EMAIL"
  endpoint       = var.alert_email
  
  freeform_tags = var.freeform_tags
}

# Slack/webhook subscription for alerts
resource "oci_ons_subscription" "webhook_alerts" {
  count = var.alert_webhook_url != "" ? 1 : 0
  
  compartment_id = var.compartment_ocid
  topic_id       = oci_ons_notification_topic.backup_alerts.id
  protocol       = "HTTPS"
  endpoint       = var.alert_webhook_url
  
  freeform_tags = var.freeform_tags
}

# Alarm: Backup Job Failure
resource "oci_monitoring_alarm" "backup_job_failure" {
  compartment_id        = var.compartment_ocid
  display_name          = "${var.display_name_prefix}-backup-job-failure"
  is_enabled            = true
  metric_compartment_id = var.compartment_ocid
  namespace             = "oci_backup_metrics"
  
  query = <<-EOQ
    BackupJobStatus[1m]{status="FAILED"}.count() > 0
  EOQ
  
  severity = "CRITICAL"
  
  message_format = "ONS_OPTIMIZED"
  body = <<-BODY
    Backup job has failed!
    
    Details:
    - Alarm: {alarmName}
    - Severity: {severity}
    - Timestamp: {timestamp}
    - Query: {query}
    
    Action Required: Investigate failed backup job immediately.
  BODY
  
  destinations = [oci_ons_notification_topic.backup_alerts.id]
  
  repeat_notification_duration = "PT2H" # Repeat every 2 hours if not resolved
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "AlertType" = "BackupFailure",
      "Severity"  = "Critical"
    }
  )
}

# Alarm: High Backup Duration
resource "oci_monitoring_alarm" "high_backup_duration" {
  compartment_id        = var.compartment_ocid
  display_name          = "${var.display_name_prefix}-high-backup-duration"
  is_enabled            = true
  metric_compartment_id = var.compartment_ocid
  namespace             = "oci_backup_metrics"
  
  query = <<-EOQ
    BackupDuration[5m].mean() > ${var.backup_duration_threshold_minutes * 60}
  EOQ
  
  severity = "WARNING"
  
  message_format = "ONS_OPTIMIZED"
  body = <<-BODY
    Backup jobs are taking longer than expected.
    
    Current Duration: Exceeds ${var.backup_duration_threshold_minutes} minutes
    Threshold: ${var.backup_duration_threshold_minutes} minutes
    
    This may indicate performance issues or increased data volume.
  BODY
  
  destinations = [oci_ons_notification_topic.backup_alerts.id]
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "AlertType" = "Performance",
      "Severity"  = "Warning"
    }
  )
}

# Alarm: Storage Capacity Warning
resource "oci_monitoring_alarm" "storage_capacity_warning" {
  compartment_id        = var.compartment_ocid
  display_name          = "${var.display_name_prefix}-storage-capacity-warning"
  is_enabled            = true
  metric_compartment_id = var.compartment_ocid
  namespace             = "oci_objectstorage"
  
  query = <<-EOQ
    StorageUsed[5m]{bucketName="${oci_objectstorage_bucket.backup_storage.name}"}.mean() > ${var.backup_repo_volume_size_gbs * 0.8}
  EOQ
  
  severity = "WARNING"
  
  message_format = "ONS_OPTIMIZED"
  body = <<-BODY
    Backup storage capacity is running low!
    
    Current Usage: > 80% of allocated storage
    
    Action Required: Consider increasing storage capacity or reviewing retention policies.
  BODY
  
  destinations = [oci_ons_notification_topic.backup_alerts.id]
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "AlertType" = "Capacity",
      "Severity"  = "Warning"
    }
  )
}

# Alarm: Instance Pool Scaling
resource "oci_monitoring_alarm" "instance_pool_cpu_high" {
  compartment_id        = var.compartment_ocid
  display_name          = "${var.display_name_prefix}-instance-pool-cpu-high"
  is_enabled            = true
  metric_compartment_id = var.compartment_ocid
  namespace             = "oci_computeagent"
  
  query = <<-EOQ
    CpuUtilization[5m]{resourceId="${oci_core_instance_pool.pool.id}"}.mean() > 85
  EOQ
  
  severity = "INFO"
  
  message_format = "ONS_OPTIMIZED"
  body = <<-BODY
    Instance pool CPU utilization is high.
    
    Current: > 85%
    Status: Autoscaling should activate automatically
    
    This is informational - no action required unless sustained.
  BODY
  
  destinations = [oci_ons_notification_topic.backup_alerts.id]
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "AlertType" = "Autoscaling",
      "Severity"  = "Info"
    }
  )
}

# Alarm: Backup Validation Failure
resource "oci_monitoring_alarm" "backup_validation_failure" {
  compartment_id        = var.compartment_ocid
  display_name          = "${var.display_name_prefix}-validation-failure"
  is_enabled            = true
  metric_compartment_id = var.compartment_ocid
  namespace             = "oci_backup_metrics"
  
  query = <<-EOQ
    BackupValidationStatus[5m]{status="FAILED"}.count() > 0
  EOQ
  
  severity = "CRITICAL"
  
  message_format = "ONS_OPTIMIZED"
  body = <<-BODY
    Backup validation has failed!
    
    This indicates that a backup may be corrupted or unrecoverable.
    
    Action Required: IMMEDIATE - Investigate and re-run backup if necessary.
  BODY
  
  destinations = [oci_ons_notification_topic.backup_alerts.id]
  
  repeat_notification_duration = "PT1H"
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "AlertType" = "DataIntegrity",
      "Severity"  = "Critical"
    }
  )
}

# Alarm: Immutable Vault Access Attempt
resource "oci_monitoring_alarm" "immutable_vault_access" {
  compartment_id        = var.compartment_ocid
  display_name          = "${var.display_name_prefix}-vault-access-attempt"
  is_enabled            = true
  metric_compartment_id = var.compartment_ocid
  namespace             = "oci_objectstorage"
  
  query = <<-EOQ
    UnauthorizedRequests[1m]{bucketName="${oci_objectstorage_bucket.immutable_backup_vault.name}"}.count() > 0
  EOQ
  
  severity = "CRITICAL"
  
  message_format = "ONS_OPTIMIZED"
  body = <<-BODY
    SECURITY ALERT: Unauthorized access attempt to immutable backup vault!
    
    Bucket: ${oci_objectstorage_bucket.immutable_backup_vault.name}
    
    This could indicate a ransomware attack or unauthorized access attempt.
    
    Action Required: IMMEDIATE security review required.
  BODY
  
  destinations = [oci_ons_notification_topic.backup_alerts.id]
  
  repeat_notification_duration = "PT30M"
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "AlertType" = "Security",
      "Severity"  = "Critical"
    }
  )
}

# Alarm: Encryption Key Rotation Needed
resource "oci_monitoring_alarm" "key_rotation_needed" {
  compartment_id        = var.compartment_ocid
  display_name          = "${var.display_name_prefix}-key-rotation-needed"
  is_enabled            = true
  metric_compartment_id = var.compartment_ocid
  namespace             = "oci_kms"
  
  query = <<-EOQ
    KeyAge[1d]{keyId="${oci_kms_key.backup_master_key.id}"}.max() > ${var.key_rotation_days * 86400}
  EOQ
  
  severity = "WARNING"
  
  message_format = "ONS_OPTIMIZED"
  body = <<-BODY
    Encryption key rotation is recommended.
    
    Key: ${oci_kms_key.backup_master_key.display_name}
    Age: > ${var.key_rotation_days} days
    
    Action Required: Schedule key rotation for security best practices.
  BODY
  
  destinations = [oci_ons_notification_topic.backup_alerts.id]
  
  freeform_tags = merge(
    var.freeform_tags,
    {
      "AlertType" = "Security",
      "Severity"  = "Warning"
    }
  )
}

# Custom metric namespace for backup operations
resource "oci_monitoring_metric" "backup_success_rate" {
  compartment_id = var.compartment_ocid
  name           = "BackupSuccessRate"
  namespace      = "oci_backup_metrics"
  
  dimensions = {
    resourceId = "backup-service"
  }
}

# Dashboard for monitoring (exported as JSON)
locals {
  monitoring_dashboard = jsonencode({
    displayName = "${var.display_name_prefix} Backup Monitoring"
    description = "Real-time monitoring for backup operations"
    widgets = [
      {
        type = "line"
        title = "Backup Success Rate"
        query = "BackupSuccessRate[1h].mean()"
      },
      {
        type = "line"
        title = "Storage Usage Trend"
        query = "StorageUsed[1h].mean()"
      },
      {
        type = "number"
        title = "Active Jobs"
        query = "ActiveBackupJobs[1m].sum()"
      },
      {
        type = "number"
        title = "Failed Jobs (24h)"
        query = "BackupJobStatus[24h]{status=\"FAILED\"}.count()"
      }
    ]
  })
}

# Outputs
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
    backup_failure        = oci_monitoring_alarm.backup_job_failure.id
    high_duration        = oci_monitoring_alarm.high_backup_duration.id
    storage_capacity     = oci_monitoring_alarm.storage_capacity_warning.id
    cpu_high             = oci_monitoring_alarm.instance_pool_cpu_high.id
    validation_failure   = oci_monitoring_alarm.backup_validation_failure.id
    vault_access         = oci_monitoring_alarm.immutable_vault_access.id
    key_rotation         = oci_monitoring_alarm.key_rotation_needed.id
  }
}
