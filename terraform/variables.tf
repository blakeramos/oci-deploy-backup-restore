variable "tenancy_ocid" { type = string }
variable "compartment_ocid" { type = string }
variable "region" { type = string, default = "us-ashburn-1" }

variable "display_name_prefix" { type = string, default = "example-style-backup" }

variable "vcn_cidr" { type = string, default = "10.0.0.0/16" }
variable "subnet_cidr" { type = string, default = "10.0.1.0/24" }
variable "availability_domain" { type = string, default = "" }

variable "instance_shape" { type = string, default = "VM.Standard.E5.Flex" }
variable "instance_ocpus" { type = number, default = 2 }
variable "instance_memory_in_gbs" { type = number, default = 8 }
variable "image_id" { type = string }
variable "ssh_public_key" { type = string }

variable "instance_pool_min" { type = number, default = 1 }
variable "instance_pool_max" { type = number, default = 4 }
variable "instance_pool_initial_size" { type = number, default = 1 }

variable "backup_repo_volume_size_gbs" { type = number, default = 200 }

variable "bootstrap_script" { type = string, default = "" }

variable "freeform_tags" { type = map(string), default = { Owner = "devops" } }

# === Enhanced Storage Variables ===

variable "enable_auto_delete" {
  type        = bool
  default     = false
  description = "Enable automatic deletion of backups after retention period"
}

variable "backup_retention_days" {
  type        = number
  default     = 90
  description = "Number of days to retain backups before deletion"
}

variable "enable_cross_region_replication" {
  type        = bool
  default     = false
  description = "Enable cross-region replication for disaster recovery"
}

variable "dr_region" {
  type        = string
  default     = "us-phoenix-1"
  description = "Disaster recovery region for backup replication"
}

variable "backup_repo_vpus_per_gb" {
  type        = number
  default     = 10
  description = "VPUs per GB for backup repository (10=Balanced, 20=High Performance)"
}

variable "enable_auto_tuned_storage" {
  type        = bool
  default     = true
  description = "Enable auto-tuned performance for block volumes (OCI's automatic IOPS scaling)"
}

# === Monitoring & Alerting Variables ===

variable "alert_email" {
  type        = string
  default     = ""
  description = "Email address for backup alerts (leave empty to disable)"
}

variable "alert_webhook_url" {
  type        = string
  default     = ""
  description = "Webhook URL for alerts (e.g., Slack webhook, leave empty to disable)"
}

variable "backup_duration_threshold_minutes" {
  type        = number
  default     = 120
  description = "Threshold in minutes for backup duration alerts"
}

variable "key_rotation_days" {
  type        = number
  default     = 90
  description = "Number of days before encryption key rotation alert"
}
