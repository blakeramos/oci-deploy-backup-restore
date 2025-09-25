output "vcn_id" {
  value = oci_core_virtual_network.vcn.id
}

output "subnet_id" {
  value = oci_core_subnet.subnet.id
}

output "backup_bucket_name" {
  value = oci_objectstorage_bucket.backup_bucket.name
}

output "instance_pool_id" {
  value = oci_core_instance_pool.pool.id
}

output "backup_repo_volume_id" {
  value = oci_core_volume.backup_repo.id
}
