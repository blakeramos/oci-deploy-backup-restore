# OCI Native VM Backup - Complete Setup Log

## Session Date
October 6, 2025 - 10:49 AM to 11:00 AM PST

---

## Objective
Set up OCI SDK/CLI and prepare environment for testing OCI Native VM backup functionality.

---

## Environment Information

### System Details
- **Operating System:** macOS
- **Shell:** /bin/zsh
- **Current Working Directory:** `/Users/jtilley/oci-deploy-backup-restore`
- **User:** jtilley

### Software Installed
- **OCI CLI:** Version 3.52.0 (pre-installed via Homebrew)
- **OCI Python SDK:** Version 2.160.3 (pre-installed)
- **Python:** Version 3.x
- **Git:** Installed

---

## Steps Completed

### 1. Verified Existing Installations

**Command:**
```bash
oci --version
python3 -c "import oci; print(f'OCI SDK version: {oci.__version__}')"
```

**Result:**
- ✅ OCI CLI: v3.52.0 (installed at `/opt/homebrew/Cellar/oci-cli/3.52.0/`)
- ✅ OCI Python SDK: v2.160.3

### 2. Checked Existing OCI Configuration

**Command:**
```bash
ls -la ~/.oci/config
cat ~/.oci/config
```

**Found:**
- Config file existed from July 1, 2023
- Old API key was no longer valid
- Authentication was failing with "NotAuthenticated" error

### 3. Generated New API Key Pair

**Commands:**
```bash
# Generate new private key
openssl genrsa -out ~/.oci/oci_api_key_new.pem 2048

# Extract public key
openssl rsa -pubout -in ~/.oci/oci_api_key_new.pem -out ~/.oci/oci_api_key_public_new.pem

# Calculate fingerprint
openssl rsa -pubout -outform DER -in ~/.oci/oci_api_key_new.pem | openssl md5 -c
```

**Generated:**
- Private Key: `~/.oci/oci_api_key_new.pem`
- Public Key: `~/.oci/oci_api_key_public_new.pem`
- **Fingerprint:** `0a:77:17:5e:0d:bc:88:90:52:9f:2e:39:07:61:84:b9`

**Public Key Content:**
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1X0RRYb//tDq4Gf2BxXx
mELXxzQ5JvQkZDBlI69nW01vTxjqG9SP5t6CnuPJDk8KoGJcfDC7+auQ3ONMhMjc
mpzqFCKzHuj2Fg/aSyU0LVS6fq3Ms9F/2J/L2JUa2B/9Z4zZ6GKDuLTS9mueik9h
/w6ArLp5iMwox+W4qKJrrTjokYzmKJ25FT2KIqy83flCBUXzu+S7cJIiNxzEbEJ2
A62BE3N+ZQFzUfCzjHCPeJQ35LZc5leOZnuraRLFIrlF/Qk5Jc27ToYi1/itUgCn
ocAhIHYnr9zGumy3MnPqYESaK7qfC4+qMxdf+AQ+S7/OlMackWgrae7g3XhE8LUg
ZQIDAQAB
-----END PUBLIC KEY-----
```

### 4. Identified Target Tenancy

**Tenancy Details Provided by User:**
- **Tenancy Name:** joetil7634
- **Tenancy OCID:** `ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a`
- **Home Region:** IAD (us-ashburn-1)
- **Object Storage Namespace:** `idsmsfppnvvx`
- **CSI Number:** 21942898

### 5. User Uploaded Public Key to OCI Console

**Steps User Performed:**
1. Logged into OCI Console (https://cloud.oracle.com)
2. Clicked profile icon → "My Profile"
3. Navigated to "API Keys" section
4. Clicked "Add API Key"
5. Selected "Paste Public Keys"
6. Pasted the public key (from step 3)
7. Verified fingerprint: `0a:77:17:5e:0d:bc:88:90:52:9f:2e:39:07:61:84:b9`

### 6. Retrieved Correct User OCID

**Initial Attempt:**
- Used old User OCID: `ocid1.user.oc1..aaaaaaaa6acylldrah3toiojdmy2oc5byby7qcnwwp44ctx3hszjhu3th7rq`
- Authentication failed

**Correction:**
- User provided correct User OCID from OCI Console
- **Correct User OCID:** `ocid1.user.oc1..aaaaaaaagphtuef36rlytvcxg6tcnb4455rpgu2e2fb7brisri3qmdlgzpjq`

### 7. Updated OCI Configuration File

**Final Config File:** `~/.oci/config`
```ini
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaagphtuef36rlytvcxg6tcnb4455rpgu2e2fb7brisri3qmdlgzpjq
fingerprint=0a:77:17:5e:0d:bc:88:90:52:9f:2e:39:07:61:84:b9
key_file=/Users/jtilley/.oci/oci_api_key_new.pem
tenancy=ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a
region=us-ashburn-1
```

### 8. Tested Authentication

**Command:**
```bash
oci iam region list --output table
```

**Result:** ✅ **SUCCESS!**
- Listed all 40 OCI regions
- Authentication working correctly
- No errors (except minor warning about API key label)

### 9. Checked for Existing Resources

**Compartments Check:**
```bash
oci iam compartment list --compartment-id-in-subtree true --all
```
**Result:** No sub-compartments found (using root tenancy compartment)

**Compute Instances Check:**
```bash
oci compute instance list --compartment-id ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a --all
```
**Result:** No compute instances found (tenancy is empty)

---

## Current Status

### ✅ Completed
1. OCI CLI and SDK verified as installed
2. New API key pair generated
3. Public key uploaded to OCI Console
4. Configuration file updated with correct OCIDs
5. Authentication tested and working
6. Tenancy details documented
7. Existing resources checked (none found)

### 🔄 In Progress
- Deploying test infrastructure

### ⏳ Pending
- Creating test compute instance
- Configuring test_config.sh with instance OCIDs
- Running first backup test
- Validating backup functionality
- Performance testing

---

## Configuration Summary

### Files Created/Modified
- `~/.oci/oci_api_key_new.pem` - New private key
- `~/.oci/oci_api_key_public_new.pem` - New public key
- `~/.oci/config` - Updated configuration file

### Important OCIDs
```bash
# Tenancy
TENANCY_OCID="ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a"

# User
USER_OCID="ocid1.user.oc1..aaaaaaaagphtuef36rlytvcxg6tcnb4455rpgu2e2fb7brisri3qmdlgzpjq"

# Compartment (using root tenancy)
COMPARTMENT_OCID="ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a"

# Region
REGION="us-ashburn-1"

# Object Storage Namespace
OBJ_STORAGE_NAMESPACE="idsmsfppnvvx"
```

### API Key Fingerprint
```
0a:77:17:5e:0d:bc:88:90:52:9f:2e:39:07:61:84:b9
```

---

## Documentation Created

During this setup session, the following documentation files were created/exist:

1. **OCI_NATIVE_VM_BACKUP_WALKTHROUGH.md** (800+ lines)
   - Step-by-step testing guide
   - 6 comprehensive test scenarios
   - Performance benchmarking procedures
   - Failure testing scenarios

2. **BACKUP_TESTING_IMPLEMENTATION_PLAN.md** (1000+ lines)
   - Complete testing strategy for 3 backup types
   - VMware Cloud backup implementation plan (6-9 months)
   - Oracle Database backup implementation plan (6-9 months)
   - Timeline, resources, and budget estimates

3. **COHESITY_FEATURE_PARITY_PLAN.md** (3000+ lines)
   - Detailed feature comparison vs Cohesity DataProtect
   - Gap analysis
   - Enhancement roadmap
   - OCI native capabilities assessment

4. **OCI_SETUP_LOG.md** (this file)
   - Complete setup documentation
   - Step-by-step commands executed
   - Troubleshooting steps
   - Current status

---

## Troubleshooting Notes

### Issue 1: Authentication Failed with Old API Key
**Problem:** Initial `oci iam region list` command returned "NotAuthenticated" error

**Root Cause:** API key from 2023 was no longer active in OCI Console

**Solution:** Generated new API key pair and uploaded public key to OCI Console

### Issue 2: Authentication Failed with Correct Key
**Problem:** After uploading new key, still got "NotAuthenticated" error

**Root Cause:** User OCID in config file was incorrect/outdated

**Solution:** User retrieved correct User OCID from OCI Console ("My Profile" page)

### Issue 3: No Resources Found
**Problem:** No compartments or compute instances found

**Root Cause:** Tenancy is new/empty with no resources created yet

**Solution:** Need to deploy test infrastructure (next step)

---

## Next Steps

### Immediate Actions (Current Session)
1. ✅ Document setup process (this file)
2. ⏳ Deploy test infrastructure using OCI CLI
   - Create VCN and subnet
   - Create compute instance for testing
   - Configure security lists
3. ⏳ Create `test_config.sh` with instance OCIDs
4. ⏳ Run first backup test
5. ⏳ Validate backup in OCI Console

### Future Actions
1. Run complete test suite (6 scenarios from walkthrough)
2. Performance benchmarking
3. Failure scenario testing
4. Generate test report
5. Plan VMware and Oracle DB implementations

---

## Useful Commands Reference

### Authentication & Configuration
```bash
# Test authentication
oci iam region list --output table

# View current config
cat ~/.oci/config

# List API keys for user
oci iam user api-key list --user-id <USER_OCID>
```

### Resource Discovery
```bash
# List compartments
oci iam compartment list --compartment-id-in-subtree true --all

# List compute instances
oci compute instance list --compartment-id <COMPARTMENT_OCID> --all

# List VCNs
oci network vcn list --compartment-id <COMPARTMENT_OCID> --all

# List subnets
oci network subnet list --compartment-id <COMPARTMENT_OCID> --all --vcn-id <VCN_OCID>

# List availability domains
oci iam availability-domain list --compartment-id <COMPARTMENT_OCID>
```

### Backup Operations
```bash
# Run backup
python3 python/backup.py --compartment <COMP_ID> --instance <INST_ID>

# Run restore
python3 python/restore.py --compartment <COMP_ID> --availability-domain <AD> --subnet <SUBNET_ID> --shape <SHAPE> --boot-backup <BACKUP_ID>

# Validate backup
python3 python/validator.py --backup-type boot_volume --backup-id <BACKUP_ID>
```

---

## Security Notes

### API Key Security
- Private key stored at: `~/.oci/oci_api_key_new.pem`
- Permissions: `600` (owner read/write only)
- Public key uploaded to OCI Console and associated with user account
- Fingerprint used for verification

### Best Practices Followed
✅ Used strong 2048-bit RSA key  
✅ Private key never shared or transmitted  
✅ Proper file permissions on private key  
✅ Fingerprint verification after upload  
✅ Old/unused keys not removed yet (for safety)

### Recommendations
- Consider rotating API keys every 90 days
- Remove old API key from OCI Console once new key is confirmed working
- Consider using Instance Principals when running from OCI compute instances

---

## Session Summary

**Duration:** ~11 minutes  
**Status:** ✅ Setup complete, ready for infrastructure deployment  
**Blockers:** None  
**Next Session:** Deploy test resources and run first backup

---

**Last Updated:** October 6, 2025 - 11:00 AM PST  
**Document Version:** 1.0  
**Author:** Cline AI Assistant + jtilley
