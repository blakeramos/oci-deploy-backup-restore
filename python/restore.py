#!/usr/bin/env python3
"""
restore.py - Restore OCI VM from backups (boot + block volumes)
"""
import argparse
import logging
from datetime import datetime
import oci

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def load_clients(profile=None):
    try:
        config = oci.config.from_file(profile_name=profile) if profile else oci.config.from_file()
        signer = None
    except Exception:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        config = {}
    compute = oci.core.ComputeClient(config, signer=signer)
    block = oci.core.BlockstorageClient(config, signer=signer)
    return compute, block

def restore_boot(block, compartment_id, ad, boot_backup_id):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    details = oci.core.models.CreateBootVolumeDetails(
        compartment_id=compartment_id,
        availability_domain=ad,
        source_details=oci.core.models.BootVolumeSourceFromBootVolumeBackupDetails(id=boot_backup_id),
        display_name=f"oci-restore-boot-{ts}"
    )
    resp = block.create_boot_volume(details)
    logging.info("Restored boot volume %s", resp.data.id)
    return resp.data

def restore_volume(block, compartment_id, ad, vol_backup_id):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    details = oci.core.models.CreateVolumeDetails(
        compartment_id=compartment_id,
        availability_domain=ad,
        source_details=oci.core.models.VolumeSourceFromVolumeBackupDetails(id=vol_backup_id),
        display_name=f"oci-restore-vol-{ts}"
    )
    resp = block.create_volume(details)
    logging.info("Restored block volume %s", resp.data.id)
    return resp.data

def launch_instance(compute, compartment_id, ad, subnet_id, shape, image_id, boot_vol_id):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    launch = oci.core.models.LaunchInstanceDetails(
        compartment_id=compartment_id,
        availability_domain=ad,
        shape=shape,
        source_details=oci.core.models.InstanceSourceViaBootVolumeDetails(boot_volume_id=boot_vol_id),
        create_vnic_details=oci.core.models.CreateVnicDetails(subnet_id=subnet_id, assign_public_ip=True),
        display_name=f"oci-restore-instance-{ts}"
    )
    resp = compute.launch_instance(launch)
    logging.info("Launched instance %s", resp.data.id)
    return resp.data

def attach_volume(compute, compartment_id, instance_id, vol_id):
    details = oci.core.models.AttachVolumeDetails(
        compartment_id=compartment_id, instance_id=instance_id, volume_id=vol_id
    )
    resp = compute.attach_volume(details)
    logging.info("Attached volume %s to instance %s", vol_id, instance_id)
    return resp.data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compartment", "-c", required=True)
    parser.add_argument("--availability-domain", "-a", required=True)
    parser.add_argument("--subnet", "-s", required=True)
    parser.add_argument("--shape", required=True)
    parser.add_argument("--image-id", required=True)
    parser.add_argument("--boot-backup", required=True)
    parser.add_argument("--block-backups", nargs="*", default=[])
    parser.add_argument("--profile", "-p")
    args = parser.parse_args()

    compute, block = load_clients(args.profile)
    boot = restore_boot(block, args.compartment, args.availability_domain, args.boot_backup)
    vols = [restore_volume(block, args.compartment, args.availability_domain, vb) for vb in args.block_backups]
    instance = launch_instance(compute, args.compartment, args.availability_domain, args.subnet, args.shape, args.image_id, boot.id)
    for vol in vols:
        attach_volume(compute, args.compartment, instance.id, vol.id)

    logging.info("Restore complete. Instance OCID: %s", instance.id)

if __name__ == "__main__":
    main()
