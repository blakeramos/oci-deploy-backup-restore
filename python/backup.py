#!/usr/bin/env python3
"""
backup.py - Backup for OCI VMs using OCI Python SDK
"""
import argparse
import logging
from datetime import datetime
import oci

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def load_clients(profile=None):
    try:
        config = oci.config.from_file(profile_name=profile) if profile else oci.config.from_file()
        oci.config.validate_config(config)
        compute = oci.core.ComputeClient(config)
        block = oci.core.BlockstorageClient(config)
        logging.info("Using OCI config file authentication")
        return compute, block
    except Exception as e:
        logging.error(f"Failed to load OCI config: {e}")
        logging.info("Attempting instance principals authentication...")
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        compute = oci.core.ComputeClient(config={}, signer=signer)
        block = oci.core.BlockstorageClient(config={}, signer=signer)
        return compute, block

def backup_boot_volume(block, compute, compartment_id, instance_id, prefix="oci-backup"):
    # Get boot volume attachments to find boot volume ID
    boot_vol_atts = compute.list_boot_volume_attachments(
        availability_domain=compute.get_instance(instance_id).data.availability_domain,
        compartment_id=compartment_id,
        instance_id=instance_id
    ).data
    
    if not boot_vol_atts:
        raise Exception("No boot volume attachments found")
    
    boot_vol_id = boot_vol_atts[0].boot_volume_id
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    details = oci.core.models.CreateBootVolumeBackupDetails(
        boot_volume_id=boot_vol_id,
        display_name=f"{prefix}-boot-{ts}"
    )
    resp = block.create_boot_volume_backup(details)
    logging.info("Created boot volume backup %s", resp.data.id)
    return resp.data

def backup_block_volumes(block, compute, compartment_id, instance_id, prefix="oci-backup"):
    atts = compute.list_volume_attachments(
        compartment_id=compartment_id,
        instance_id=instance_id
    ).data
    backups = []
    for att in atts:
        if att.volume_id:
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            details = oci.core.models.CreateVolumeBackupDetails(
                volume_id=att.volume_id,
                display_name=f"{prefix}-vol-{ts}"
            )
            resp = block.create_volume_backup(details)
            backups.append(resp.data)
            logging.info("Created block volume backup %s", resp.data.id)
    return backups

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compartment", "-c", required=True)
    parser.add_argument("--instance", "-i", required=True)
    parser.add_argument("--profile", "-p")
    args = parser.parse_args()

    compute, block = load_clients(args.profile)
    instance = compute.get_instance(args.instance).data
    boot_backup = backup_boot_volume(block, compute, args.compartment, args.instance)
    vol_backups = backup_block_volumes(block, compute, args.compartment, args.instance)

    logging.info("Boot backup: %s", boot_backup.id)
    for vb in vol_backups:
        logging.info("Volume backup: %s", vb.id)

if __name__ == "__main__":
    main()
