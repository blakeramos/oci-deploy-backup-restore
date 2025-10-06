# OCI IAM Policy Setup Guide

## Problem
Your user needs permissions to create and manage compute instances, but the current policy grants permissions to the "Administrators" group, and your user may not be in that group.

---

## Solution: Add User to Administrators Group

This is the **fastest and simplest** approach.

### Step-by-Step Instructions

#### 1. Navigate to Groups
- Go to OCI Console: https://cloud.oracle.com
- Click **☰** menu → **Identity & Security** → **Domains**
- Click on **Default** domain
- Click **Groups** (left menu)

#### 2. Open Administrators Group
- Find and click on **"Administrators"** group

#### 3. Add Your User
- Click **"Add user to group"** button
- Search for your user (the one with OCID: `ocid1.user.oc1..aaaaaaaagphtuef36rlytvcxg6tcnb4455rpgu2e2fb7brisri3qmdlgzpjq`)
- Select your user
- Click **"Add"**

#### 4. Verify
- Your user should now appear in the Members list
- **Wait 2-3 minutes** for changes to propagate

#### 5. Test
- Try creating VM via CLI again
- Should work now!

---

## Alternative: Verify Existing Policy

If you don't want to add user to Administrators group, verify the existing policy is correct:

### Check Current Policy

#### 1. Navigate to Policies
- **☰** → **Identity & Security** → **Policies**

#### 2. View Policy Details
- Click on **"user-compute-policy"**
- Verify statements are:
  ```
  Allow group Administrators to manage instances in tenancy
  Allow group Administrators to manage volume-family in tenancy
  Allow group Administrators to use virtual-network-family in tenancy
  ```

#### 3. Check Your Group Membership
- **☰** → **Identity & Security** → **Domains** → **Default**
- Click **Users**
- Find and click your user
- Check **"Groups"** section
- If "Administrators" is NOT listed, you need to add it (see above)

---

## Alternative: Create User-Specific Policy (Advanced)

If you want to grant permissions to your user directly without adding to Administrators group:

### Option A: Via Console

#### 1. Navigate to Policies
- **☰** → **Identity & Security** → **Policies**

#### 2. Create New Policy
- Click **"Create Policy"**
- **Name:** `user-direct-compute-policy`
- **Description:** `Direct compute permissions for specific user`
- **Compartment:** joetil7634 (root)

#### 3. Policy Builder
- Click **"Show manual editor"**
- Paste these statements (one per line):

```
Allow any-user to manage instances in tenancy where request.user.id = 'ocid1.user.oc1..aaaaaaaagphtuef36rlytvcxg6tcnb4455rpgu2e2fb7brisri3qmdlgzpjq'
Allow any-user to manage volume-family in tenancy where request.user.id = 'ocid1.user.oc1..aaaaaaaagphtuef36rlytvcxg6tcnb4455rpgu2e2fb7brisri3qmdlgzpjq'
Allow any-user to use virtual-network-family in tenancy where request.user.id = 'ocid1.user.oc1..aaaaaaaagphtuef36rlytvcxg6tcnb4455rpgu2e2fb7brisri3qmdlgzpjq'
```

#### 4. Create
- Click **"Create"**
- **Wait 2-3 minutes** for propagation

---

## Recommended Approach

### ✅ Best Option: Add User to Administrators Group

**Why?**
- ✅ Simplest and fastest
- ✅ Works immediately
- ✅ Standard OCI practice
- ✅ Policy already exists and is correct
- ✅ No complex syntax needed

**Steps:**
1. Go to Identity → Domains → Default → Groups
2. Click "Administrators"
3. Click "Add user to group"
4. Select your user
5. Add
6. Wait 2-3 minutes
7. Retry VM creation

---

## After Policy Setup

### Test Authentication
```bash
# Test if you can list instances (should work)
oci compute instance list --compartment-id ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a --all

# Try creating VM again
oci compute instance launch \
  --compartment-id ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a \
  --availability-domain "DeZH:US-ASHBURN-AD-1" \
  --shape "VM.Standard.E2.1.Micro" \
  --image-id ocid1.image.oc1.iad.aaaaaaaasx2ayj3iaqze2ja2tr5glsltl3pdvxb37xyal7nscthikosglu5a \
  --subnet-id ocid1.subnet.oc1.iad.aaaaaaaagpmvodqss4mbqpoq7vcmhkn7jysn52dy6tnsb2deoila2qgjzhrq \
  --display-name "backup-test-vm" \
  --assign-public-ip true \
  --wait-for-state RUNNING
```

---

## Troubleshooting

### "Still getting NotAuthorizedOrNotFound"

**Possible causes:**
1. ⏳ Policy needs time to propagate (wait 2-3 more minutes)
2. ❌ User not in Administrators group
3. ❌ Policy in wrong compartment
4. ❌ Typo in policy statement

**Solutions:**
1. Wait and retry
2. Verify group membership
3. Ensure policy is in root compartment
4. Review policy statements

### "Can't add user to Administrators group"

**Cause:** You may not have permissions to modify groups

**Solution:** 
- You might be a limited user
- Contact your tenancy administrator
- OR use Console to create VM (doesn't require group membership for console access)

---

## Quick Reference

### Your Key Details
```bash
# User OCID
ocid1.user.oc1..aaaaaaaagphtuef36rlytvcxg6tcnb4455rpgu2e2fb7brisri3qmdlgzpjq

# Tenancy OCID  
ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a

# Existing Policy
user-compute-policy (grants to Administrators group)
```

### Commands to Test
```bash
# List groups your user belongs to
oci iam user list-groups \
  --user-id ocid1.user.oc1..aaaaaaaagphtuef36rlytvcxg6tcnb4455rpgu2e2fb7brisri3qmdlgzpjq

# List all policies
oci iam policy list \
  --compartment-id ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a
```

---

## Next Steps

1. ✅ **Add user to Administrators group** (recommended)
2. ⏳ **Wait 2-3 minutes** for propagation
3. 🧪 **Test VM creation** via CLI
4. 🎉 **Run backup tests** once VM is created

---

**Need help? Let me know which approach you chose and if you need assistance with any steps!**
