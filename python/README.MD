# OCI VM Backup & Restore (Python SDK)

This directory contains **Python scripts** that implement Cohesity-style **backup** and **restore workflows** for Oracle Cloud Infrastructure (OCI) Compute instances.  
They leverage the **OCI Python SDK** to automate VM protection in a way similar to Cohesity DataProtect on AWS.

---

##  Features

### Backup (`backup.py`)
- Creates a **boot volume backup** of the specified OCI VM.  
- Creates backups for **all attached block volumes**.  
- Tags backups with timestamped names for easy identification.  
- Logs all backup operations and OCIDs.

### Restore (`restore.py`)
- Restores a **boot volume** from a selected backup.  
- Restores any number of **block volumes** from backups.  
- Launches a **new instance** using the restored boot volume.  
- Attaches restored block volumes to the new instance.  
- Logs the new instance OCID and attached volume OCIDs.

---

##  Requirements

- Python 3.7+  
- [OCI CLI/SDK setup](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm)  
- Installed packages (from `requirements.txt`):
  ```bash
  pip install -r python/requirements.txt
  ```

### Authentication
The scripts support both:
- **Config file authentication** (`~/.oci/config`) with profiles.
- **Instance principals** (recommended for running inside OCI instances).

---

##  Usage

### Backup a VM
```bash
python backup.py   --compartment ocid1.compartment.oc1..aaaaaaaaxxx   --instance ocid1.instance.oc1..bbbbbbbbbyyy
```

**Output:**
- Boot volume backup OCID.
- List of block volume backup OCIDs.

---

### Restore a VM
```bash
python restore.py   --compartment ocid1.compartment.oc1..aaaaaaaaxxx   --availability-domain Uocm:PHX-AD-1   --subnet ocid1.subnet.oc1..cccccccc   --shape VM.Standard.E4.Flex   --image-id ocid1.image.oc1..dddddddd   --boot-backup ocid1.bootvolumebackup.oc1..eeeeeeee   --block-backups ocid1.volumebackup.oc1..ffffffff ocid1.volumebackup.oc1..gggggggg
```

**Output:**
- Restored boot volume OCID.
- Restored block volume OCIDs.
- New instance OCID with attached volumes.

---

##  Parameters

### `backup.py`
- `--compartment` : Compartment OCID of the instance.  
- `--instance` : Instance OCID to back up.  
- `--profile` : (Optional) Profile from `~/.oci/config`.

### `restore.py`
- `--compartment` : Compartment OCID for restore resources.  
- `--availability-domain` : AD where resources will be created.  
- `--subnet` : Subnet OCID for the new instance.  
- `--shape` : Compute shape (e.g., `VM.Standard.E4.Flex`).  
- `--image-id` : Image OCID (for metadata; doesn’t affect boot volume restore).  
- `--boot-backup` : Boot volume backup OCID.  
- `--block-backups` : (Optional) One or more block volume backup OCIDs.  
- `--profile` : (Optional) Profile from `~/.oci/config`.

---

##  Example Workflow

1. **Back up a VM**:
   - Run `backup.py` with compartment + instance IDs.
   - Note down the boot and block volume backup OCIDs.

2. **Restore the VM**:
   - Run `restore.py` with the backup OCIDs.
   - A new instance is launched with restored volumes attached.

3. **Post-Restore**:
   - Connect to the instance with SSH.
   - Validate applications and data.

---

##  Security Considerations
- Use **Instance Principals** + IAM Dynamic Groups instead of embedding API keys.  
- Restrict IAM policies to least privilege:
  - `manage volume-family` in target compartment.
  - `manage instance-family` in target compartment.
  - `use buckets` for object storage if needed.

---

##  References
- [OCI Python SDK Docs](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm)  
- [Block Volume Backups](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/overview.htm)  
- [Boot Volume Backups](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/bootvolumes.htm)  
- [Resizing Instances](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/resizinginstances.htm)  
