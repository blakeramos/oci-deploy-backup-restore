variable "tenancy_ocid" { type = string }
variable "compartment_ocid" { type = string }
variable "region" { type = string, default = "us-ashburn-1" }

variable "display_name_prefix" { type = string, default = "cohesity-style-backup" }

variable "vcn_cidr" { type = string, default = "10.0.0.0/16" }
variable "subnet_cidr" { type = string, default = "10.0.1.0/24" }
variable "availability_domain" { type = string, default = "" }

variable "instance_shape" { type = string, default = "VM.Standard.E4.Flex" }
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
