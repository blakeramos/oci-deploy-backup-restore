# Quick Guide: Create VM and Run Backup Tests

## Current Status
- ✅ Network infrastructure ready (VCN, subnet, internet gateway)
- ❌ IAM policies needed for CLI instance creation
- 🎯 Solution: Create VM via OCI Console (faster)

---

## Step 1: Create VM via OCI Console (5 minutes)

### Go to OCI Console
https://cloud.oracle.com → Sign in to **joetil7634** tenancy

### Create Instance
1. **Click:** Compute → Instances → **Create Instance**

2. **Name:** `backup-test-vm`

3. **Image:** Oracle Linux 8 (should be pre-selected)

4. **Shape:** 
   - Click "Change Shape"
   - Select "**VM.Standard.E2.1.Micro**" (Always Free tier - NO COST)
   - OR select "**VM.Standard.E4.Flex**" (1 OCPU, 8GB RAM)

5. **Networking:**
   - **Virtual cloud network:** Select `backup-test-vcn`
   - **Subnet:** Select `backup-test-subnet`
   - **Public IP:** ✅ Assign a public IPv4 address

6. **SSH Keys:** 
   - Select "No SSH keys" (not needed for backup testing)

7. **Boot Volume:**
   - Leave default (50 GB)

8. **Click "Create"**

9. **Wait 2-3 minutes** for instance to reach **RUNNING** state

10. **Copy Instance OCID** (looks like: `ocid1.instance.oc1.iad.aaaaaaaaxxx...`)

---

## Step 2: Create Configuration File

Once you have the Instance OCID, run these commands:

```bash
# Navigate to project directory
cd ~/oci-deploy-backup-restore

# Create configuration file
cat > test_config.sh << 'EOF'
#!/bin/bash
# OCI Backup Test Configuration - joetil7634 Tenancy

# Tenancy & Compartment
export TENANCY_ID="ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a"
export COMPARTMENT_ID="ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a"

# Network Resources
export VCN_ID="ocid1.vcn.oc1.iad.amaaaaaaumfbntyaq735wfzzcbxybur3ergz5zqonfptpdym6wa3rcyur2da"
export SUBNET_ID="ocid1.subnet.oc1.iad.aaaaaaaagpmvodqss4mbqpoq7vcmhkn7jysn52dy6tnsb2deoila2qgjzhrq"
export AVAILABILITY_DOMAIN="DeZH:US-ASHBURN-AD-1"

# **REPLACE THIS with your actual instance OCID from console:**
export TEST_INSTANCE_ID="ocid1.instance.oc1.iad.PASTE_YOUR_INSTANCE_OCID_HERE"

# Restore Settings
export RESTORE_SHAPE="VM.Standard.E2.1.Micro"

echo "✅ Configuration loaded!"
echo "Tenancy: joetil7634"
echo "Region: us-ashburn-1"  
echo "Instance: $TEST_INSTANCE_ID"
EOF

# Make it executable
chmod +x test_config.sh

# Edit to add your instance OCID
nano test_config.sh
# OR
code test_config.sh
```

**Important:** Replace `PASTE_YOUR_INSTANCE_OCID_HERE` with your actual instance OCID!

---

## Step 3: Run First Backup Test

```bash
# Load configuration
source test_config.sh

# Verify configuration loaded
echo "Testing instance: $TEST_INSTANCE_ID"

# Run backup
python3 python/backup.py \
  --compartment "$COMPARTMENT_ID" \
  --instance "$TEST_INSTANCE_ID"
```

### Expected Output:
```
INFO: Created boot volume backup ocid1.bootbackup.oc1.iad.aaaaaaaa...
INFO: Boot backup: ocid1.bootbackup.oc1.iad.aaaaaaaa...
```

---

## Step 4: Verify Backup in Console

1. **Go to:** Compute → Instances → Click `backup-test-vm`
2. **Under Resources**, click "**Boot Volume**"
3. **Click on the boot volume name**
4. **Click "Boot Volume Backups"** (left menu)
5. **Verify:** You should see a backup with timestamp name like:
   - `oci-backup-boot-20251006T183000Z`
   - State: AVAILABLE
   - Type: FULL

---

## Step 5: Validate the Backup

```bash
# Source config (if not already loaded)
source test_config.sh

# Get the backup ID from previous step output
# It looks like: ocid1.bootbackup.oc1.iad.aaaaaaaa...
export BOOT_BACKUP_ID="<paste-backup-id-here>"

# Run validation
python3 python/validator.py \
  --backup-type boot_volume \
  --backup-id "$BOOT_BACKUP_ID"
```

### Expected Output:
```
INFO: Validating boot volume backup...
INFO: ✓ Backup exists
INFO: ✓ Metadata valid
INFO: ✓ Encryption verified
INFO: Validation status: PASSED
INFO: Backup is ready for restore
```

---

## Step 6: Test Restore (Optional)

**Warning:** This creates a NEW instance and will cost money if not Always Free tier.

```bash
# Source config
source test_config.sh

# Run restore
python3 python/restore.py \
  --compartment "$COMPARTMENT_ID" \
  --availability-domain "$AVAILABILITY_DOMAIN" \
  --subnet "$SUBNET_ID" \
  --shape "$RESTORE_SHAPE" \
  --boot-backup "$BOOT_BACKUP_ID"
```

### Expected Output:
```
INFO: Creating instance from backup...
INFO: Instance created: ocid1.instance.oc1.iad.bbbbbbbb...
INFO: Restore complete!
```

### Cleanup Restored Instance
```bash
# Terminate the test restored instance (to avoid costs)
oci compute instance terminate \
  --instance-id <restored-instance-id> \
  --preserve-boot-volume false \
  --force
```

---

## Complete Test Suite

After basic tests work, run the complete test suite:

```bash
# Follow the comprehensive walkthrough
cat OCI_NATIVE_VM_BACKUP_WALKTHROUGH.md

# Or run all 6 test scenarios:
# 1. Basic boot volume backup ✅
# 2. Multi-volume backup
# 3. Full instance restore
# 4. Cross-AD disaster recovery
# 5. Backup validation
# 6. Policy-based automation
```

---

## Troubleshooting

### "Instance OCID not set"
```bash
# Make sure you edited test_config.sh with real OCID
source test_config.sh
echo $TEST_INSTANCE_ID  # Should show actual OCID
```

### "Backup not found"
```bash
# List backups to find OCID
oci bv boot-volume-backup list \
  --compartment-id "$COMPARTMENT_ID" \
  --output table
```

### "Authentication failed"
```bash
# Test OCI CLI authentication
oci iam region list --output table
# Should list regions without errors
```

---

## Quick Reference Commands

```bash
# Load configuration
source test_config.sh

# Run backup
python3 python/backup.py --compartment "$COMPARTMENT_ID" --instance "$TEST_INSTANCE_ID"

# Validate backup
python3 python/validator.py --backup-type boot_volume --backup-id "$BOOT_BACKUP_ID"

# List all backups
oci bv boot-volume-backup list --compartment-id "$COMPARTMENT_ID" --all --output table

# Check instance status
oci compute instance get --instance-id "$TEST_INSTANCE_ID" --query 'data."lifecycle-state"'

# Terminate instance (cleanup)
oci compute instance terminate --instance-id "$TEST_INSTANCE_ID" --force
```

---

## Success Criteria

✅ **Backup Test Passed if:**
- Backup created successfully
- Backup visible in OCI Console
- Backup validation passes
- Restore works (optional test)

✅ **You're Ready for Production if:**
- All 6 test scenarios pass
- Performance benchmarks met (see walkthrough)
- Documentation reviewed

---

## Need Help?

1. **Review full walkthrough:** `OCI_NATIVE_VM_BACKUP_WALKTHROUGH.md`
2. **Check setup log:** `OCI_SETUP_LOG.md`
3. **Feature planning:** `COHESITY_FEATURE_PARITY_PLAN.md`

---

**Next:** Once you create the VM and copy its OCID, let me know and I'll help run the tests! 🚀
