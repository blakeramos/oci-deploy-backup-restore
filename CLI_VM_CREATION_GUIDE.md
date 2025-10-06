# CLI VM Creation Guide

Complete guide for creating OCI VM instances via CLI with intelligent fallback and troubleshooting.

---

## Quick Start

```bash
# 1. Load configuration
source test_config.sh

# 2. Run diagnostic to check environment
bash diagnose_oci.sh

# 3. Create VM with intelligent fallback
bash create_vm_cli.sh

# 4. Verify VM was created
source test_config.sh
echo "Instance ID: $TEST_INSTANCE_ID"
```

---

## Problem Statement

**Issue**: Cannot create VMs via OCI CLI despite being in Administrators group.

**Root Cause**: Service limits and capacity constraints, NOT IAM permissions.

**Solution**: Intelligent script that tries multiple VM shapes with automatic fallback.

---

## What's Included

### 1. `diagnose_oci.sh` - Environment Diagnostic Tool

Comprehensive diagnostic script that checks:
- ✅ OCI CLI installation and authentication
- ✅ Configuration variables (compartment, AD, subnet)
- ✅ Network resources (VCN, subnet status)
- ✅ Service limits for multiple compute shapes
- ✅ IAM permissions
- ✅ Python environment and OCI SDK
- ✅ Existing instances

**Usage:**
```bash
bash diagnose_oci.sh
```

**Example Output:**
```
=========================================
OCI Environment Diagnostic Tool
=========================================

Test 1: OCI CLI Installation
✓ OCI CLI installed: 3.39.0

Test 2: Authentication
✓ Authentication successful
  User: joseph.tilley@oracle.com

Test 3: Configuration Variables
✓ COMPARTMENT_ID set
✓ AVAILABILITY_DOMAIN set
✓ SUBNET_ID set

Test 5: Service Limits (Compute Shapes)
Checking VM.Standard.E2.1.Micro (Always Free)...
✗ No capacity available (Used: 0)

Checking VM.Standard.E4.Flex...
✓ Available: 10, Used: 0
```

### 2. `create_vm_cli.sh` - Intelligent VM Creation Script

Smart VM creation with automatic fallback across multiple shapes:

**Shape Priority (in order):**
1. **VM.Standard.E2.1.Micro** - Always Free (first choice)
2. **VM.Standard.A1.Flex** - ARM Always Free (second choice)
3. **VM.Standard.E4.Flex** - Low cost ~$0.05/hour (fallback)
4. **VM.Standard.E5.Flex** - Latest generation (last resort)

**Features:**
- ✅ Checks service limits before attempting creation
- ✅ Automatically finds latest Oracle Linux 8 image
- ✅ Waits for instance to reach RUNNING state
- ✅ Auto-updates `test_config.sh` with new instance ID
- ✅ Color-coded output for easy monitoring
- ✅ Comprehensive error handling

**Usage:**
```bash
# Default name: backup-test-vm-cli
bash create_vm_cli.sh

# Custom name
bash create_vm_cli.sh my-custom-vm-name
```

**Example Output:**
```
=========================================
OCI VM Creation Script
=========================================
VM Name: backup-test-vm-cli
Compartment: aaaaaaaaz4f4xsfb...
Availability Domain: DeZH:US-ASHBURN-AD-1

Step 1: Getting Oracle Linux 8 image...
✓ Found image: aaaaaaaasx2ayj3i...

Step 2: Checking shape availability...

Checking availability for VM.Standard.E2.1.Micro...
  Available: 0, Used: 0
✗ No capacity available

Checking availability for VM.Standard.E4.Flex...
  Available: 10, Used: 0
✓ Shape available!

=========================================
Creating VM Instance
=========================================
Shape: VM.Standard.E4.Flex
OCPUs: 1, Memory: 8GB
Image: aaaaaaaasx2ayj3i...

Launching instance (this may take 2-3 minutes)...

=========================================
✓ VM Created Successfully!
=========================================
Instance ID: ocid1.instance.oc1.iad.anyhqljt...

Updating test_config.sh with new instance ID...
✓ Configuration updated

Next Steps:
1. Reload configuration: source test_config.sh
2. Run backup test: python3 python/backup.py --compartment "$COMPARTMENT_ID" --instance "$TEST_INSTANCE_ID"
```

---

## Workflow

### Step 1: Verify Environment

```bash
# Run diagnostics
bash diagnose_oci.sh
```

Check for:
- ✅ OCI CLI authenticated
- ✅ Configuration loaded
- ✅ Network resources available
- ✅ At least one shape has capacity

### Step 2: Create VM

```bash
# Load configuration
source test_config.sh

# Create VM with intelligent fallback
bash create_vm_cli.sh
```

The script will:
1. Check service limits for each shape
2. Try to create VM with first available shape
3. Automatically configure for flexible shapes (OCPUs/memory)
4. Wait for instance to reach RUNNING state
5. Update test_config.sh with new instance ID

### Step 3: Verify VM Creation

```bash
# Reload configuration to get new instance ID
source test_config.sh

# Check instance status
oci compute instance get --instance-id "$TEST_INSTANCE_ID" --query 'data."lifecycle-state"'

# Should output: "RUNNING"
```

### Step 4: Run Backup Tests

```bash
# Run backup
python3 python/backup.py \
  --compartment "$COMPARTMENT_ID" \
  --instance "$TEST_INSTANCE_ID"

# Validate backup (use backup ID from previous output)
python3 python/validator.py \
  --backup-type boot_volume \
  --backup-id "ocid1.bootbackup.oc1.iad.xxxxx"
```

---

## Troubleshooting

### All Shapes Exhausted

If all shapes fail with "No capacity available":

**Solution 1: Try Different Availability Domain**
```bash
# List all ADs in region
oci iam availability-domain list --compartment-id "$TENANCY_ID"

# Update test_config.sh with different AD
# Then retry: bash create_vm_cli.sh
```

**Solution 2: Try Different Region**
```bash
# Configure for us-phoenix-1
export REGION="us-phoenix-1"

# Update OCI CLI config or use --region flag
oci compute instance launch ... --region us-phoenix-1
```

**Solution 3: Request Service Limit Increase**
1. Go to: https://cloud.oracle.com/limits
2. Select "Compute" service
3. Find the shape limit (e.g., "vm-standard-e4-flex-count")
4. Click "Request Limit Increase"
5. Wait 1-2 business days for approval

**Solution 4: Use OCI Console (Temporary)**
Follow: `CREATE_VM_AND_TEST.md` for console-based creation

### Authentication Errors

```bash
# Re-configure OCI CLI
oci setup config

# Test authentication
oci iam region list

# Should list regions without errors
```

### Permission Errors

Despite being in Administrators group, if you see "NotAuthorizedOrNotFound":

1. **Wait 2-3 minutes** - Permissions take time to propagate
2. **Verify group membership**:
   - Console → Identity & Security → Domains → Default → Groups → Administrators
   - Check your user is listed
3. **Check policy exists**:
   ```bash
   oci iam policy list --compartment-id "$TENANCY_ID" --all
   ```

### Network Errors

```bash
# Verify VCN exists and is available
oci network vcn get --vcn-id "$VCN_ID"

# Verify subnet exists and is available
oci network subnet get --subnet-id "$SUBNET_ID"

# If network resources don't exist, create them:
# Follow: terraform/README.md or use Console to create VCN + subnet
```

---

## Understanding Service Limits

### Always Free Tier Limits
- **VM.Standard.E2.1.Micro**: 2 instances per tenancy (across all regions)
- **VM.Standard.A1.Flex**: 4 OCPUs total, 24 GB RAM total

### Why "Available: 0, Used: 0"?

This means:
- ❌ The limit is 0 (not enabled for your tenancy/region)
- ❌ OR capacity is exhausted in this availability domain

**Not:**
- ✅ You're already using instances (Used would be > 0)
- ✅ Permission issues (you can query the limits)

### Checking All Regions

```bash
# Check micro instance availability in all regions
for region in us-ashburn-1 us-phoenix-1 us-sanjose-1; do
  echo "Region: $region"
  oci limits resource-availability get \
    --compartment-id "$COMPARTMENT_ID" \
    --service-name compute \
    --limit-name vm-standard-e2-1-micro-count \
    --availability-domain "$(oci iam availability-domain list --region $region --query 'data[0].name' --raw-output)" \
    --region $region \
    2>&1 | grep -E "(available|used)"
done
```

---

## Cost Considerations

### Always Free Options (NO COST)
- **VM.Standard.E2.1.Micro**: 1/8 OCPU, 1 GB RAM
  - Up to 2 instances
  - Best for testing/development
  
- **VM.Standard.A1.Flex** (ARM): Up to 4 OCPUs, 24 GB RAM total
  - Newer ARM architecture
  - May have better availability

### Paid Options (Minimal Cost)
- **VM.Standard.E4.Flex**: ~$0.015/OCPU/hour
  - 1 OCPU, 8 GB RAM = ~$0.05/hour (~$36/month)
  - Can be scaled down after testing
  
- **VM.Standard.E5.Flex**: ~$0.017/OCPU/hour
  - Latest generation
  - Better performance

**Cost Mitigation:**
1. Stop instances when not in use (no compute charges)
2. Use smallest configuration (1 OCPU)
3. Clean up after testing
4. Set up budget alerts in Console

---

## Integration with Backup Testing

Once VM is created, follow the complete backup testing workflow:

```bash
# 1. Verify instance is running
source test_config.sh
oci compute instance get --instance-id "$TEST_INSTANCE_ID"

# 2. Run backup
python3 python/backup.py \
  --compartment "$COMPARTMENT_ID" \
  --instance "$TEST_INSTANCE_ID"

# 3. Get backup OCID from output, then validate
export BOOT_BACKUP_ID="ocid1.bootbackup.oc1.iad.xxxxx"
python3 python/validator.py \
  --backup-type boot_volume \
  --backup-id "$BOOT_BACKUP_ID"

# 4. Test restore (creates new instance)
python3 python/restore.py \
  --compartment "$COMPARTMENT_ID" \
  --availability-domain "$AVAILABILITY_DOMAIN" \
  --subnet "$SUBNET_ID" \
  --shape "VM.Standard.E2.1.Micro" \
  --boot-backup "$BOOT_BACKUP_ID"

# 5. Cleanup test resources
oci compute instance terminate --instance-id "$TEST_INSTANCE_ID" --force
```

For comprehensive testing, see:
- `OCI_NATIVE_VM_BACKUP_WALKTHROUGH.md` - Complete 6-scenario test suite
- `CREATE_VM_AND_TEST.md` - Step-by-step testing guide

---

## Advanced Usage

### Creating Multiple VMs

```bash
# Create 3 VMs for testing
for i in {1..3}; do
  bash create_vm_cli.sh backup-test-vm-$i
  sleep 30  # Wait between creations
done
```

### Using Specific Shape

```bash
# Force specific shape (bypass availability check)
oci compute instance launch \
  --compartment-id "$COMPARTMENT_ID" \
  --availability-domain "$AVAILABILITY_DOMAIN" \
  --shape "VM.Standard.E4.Flex" \
  --shape-config '{"ocpus": 1, "memoryInGBs": 8}' \
  --subnet-id "$SUBNET_ID" \
  --image-id "$IMAGE_ID" \
  --display-name "my-vm" \
  --assign-public-ip true \
  --wait-for-state RUNNING
```

### Cross-Region Deployment

```bash
# Set different region
export REGION="us-phoenix-1"

# Get AD for that region
export AVAILABILITY_DOMAIN=$(oci iam availability-domain list \
  --region $REGION \
  --query 'data[0].name' \
  --raw-output)

# Create VM in new region
oci compute instance launch \
  --region $REGION \
  --compartment-id "$COMPARTMENT_ID" \
  --availability-domain "$AVAILABILITY_DOMAIN" \
  ...
```

---

## Scripts Reference

### Make Scripts Executable

```bash
chmod +x diagnose_oci.sh create_vm_cli.sh test_config.sh
```

### Configuration Management

```bash
# View current configuration
cat test_config.sh

# Reload after changes
source test_config.sh

# Backup configuration
cp test_config.sh test_config.sh.backup
```

### Cleanup

```bash
# Terminate VM
oci compute instance terminate --instance-id "$TEST_INSTANCE_ID" --force

# Delete backups
oci bv boot-volume-backup delete --boot-volume-backup-id "$BOOT_BACKUP_ID" --force

# Delete network resources (if using Terraform)
cd terraform && terraform destroy
```

---

## Summary

This solution provides:

✅ **Comprehensive diagnostics** to identify issues before VM creation  
✅ **Intelligent fallback** across 4 different VM shapes  
✅ **Automatic configuration** updates for seamless integration  
✅ **Cost optimization** by prioritizing Always Free options  
✅ **Full automation** from environment check to VM creation  
✅ **Clear error messages** and troubleshooting guidance

**Next Steps:**
1. Run `bash diagnose_oci.sh` to check your environment
2. Run `bash create_vm_cli.sh` to create your VM
3. Follow `OCI_NATIVE_VM_BACKUP_WALKTHROUGH.md` for backup testing

---

## Support

For issues or questions:
- Review diagnostic output from `diagnose_oci.sh`
- Check OCI Console → Compute → Instances
- Verify service limits at: https://cloud.oracle.com/limits
- Consult OCI documentation: https://docs.oracle.com/iaas

**Common Issues Resolved:**
- ✅ IAM permissions (user in Administrators group)
- ✅ Service limit checking (automatic before creation)
- ✅ Shape availability (tries 4 different options)
- ✅ Network configuration (validates before proceeding)
- ✅ Configuration management (auto-updates after creation)
