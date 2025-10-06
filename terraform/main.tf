terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 4.0.0"
    }
  }
}

provider "oci" {
  region = var.region
}

# --- Networking ---
resource "oci_core_virtual_network" "vcn" {
  compartment_id = var.compartment_ocid
  cidr_block     = var.vcn_cidr
  display_name   = "${var.display_name_prefix}-vcn"
  freeform_tags  = var.freeform_tags
}

resource "oci_core_subnet" "subnet" {
  compartment_id      = var.compartment_ocid
  vcn_id              = oci_core_virtual_network.vcn.id
  cidr_block          = var.subnet_cidr
  display_name        = "${var.display_name_prefix}-subnet"
  availability_domain = var.availability_domain != "" ? var.availability_domain : null
  freeform_tags       = var.freeform_tags
}

resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_virtual_network.vcn.id
  display_name   = "${var.display_name_prefix}-igw"
}

resource "oci_core_route_table" "rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_virtual_network.vcn.id
  display_name   = "${var.display_name_prefix}-rt"

  route_rules {
    cidr_block = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.igw.id
  }
}

resource "oci_core_security_list" "sec" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_virtual_network.vcn.id
  display_name   = "${var.display_name_prefix}-sec"

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  egress_security_rules {
    protocol = "all"
    destination = "0.0.0.0/0"
  }
}

# --- Object Storage Namespace ---
# Required for all object storage operations
data "oci_objectstorage_namespace" "ns" {}

# --- Instance Configuration ---
resource "oci_core_instance_configuration" "instance_config" {
  compartment_id = var.compartment_ocid
  display_name   = "${var.display_name_prefix}-cfg"

  instance_details {
    shape = var.instance_shape

    create_vnic_details {
      subnet_id       = oci_core_subnet.subnet.id
      assign_public_ip = true
    }

    source_details {
      source_type = "image"
      image_id    = var.image_id
    }

    metadata = {
      ssh_authorized_keys = var.ssh_public_key
      user_data           = base64encode(var.bootstrap_script != "" ? var.bootstrap_script : "#!/bin/bash\nyum -y install python3 git || apt-get update -y && apt-get install -y python3 git")
    }

    shape_config {
      ocpus         = var.instance_ocpus
      memory_in_gbs = var.instance_memory_in_gbs
    }
  }
}

# --- Instance Pool ---
resource "oci_core_instance_pool" "pool" {
  compartment_id            = var.compartment_ocid
  display_name              = "${var.display_name_prefix}-pool"
  instance_configuration_id = oci_core_instance_configuration.instance_config.id

  placement_configurations {
    availability_domain = var.availability_domain != "" ? var.availability_domain : null
    subnet_id           = oci_core_subnet.subnet.id
  }

  size          = var.instance_pool_initial_size
  freeform_tags = var.freeform_tags
}

# --- Autoscaling ---
resource "oci_autoscaling_auto_scaling_configuration" "pool_autoscale" {
  compartment_id = var.compartment_ocid
  display_name   = "${var.display_name_prefix}-autoscale"

  resource {
    id   = oci_core_instance_pool.pool.id
    type = "instancePool"
  }

  policy {
    policy_type = "threshold"
    capacity {
      initial = var.instance_pool_initial_size
      min     = var.instance_pool_min
      max     = var.instance_pool_max
    }

    rules {
      metric_type      = "CPU_UTILIZATION"
      threshold        = 70
      operator         = "GT"
      action {
        type   = "CHANGE_COUNT_BY"
        value  = 1
      }
    }

    rules {
      metric_type      = "CPU_UTILIZATION"
      threshold        = 25
      operator         = "LT"
      action {
        type   = "CHANGE_COUNT_BY"
        value  = -1
      }
    }
  }
}
