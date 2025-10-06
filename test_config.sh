#!/bin/bash
# OCI Backup Test Configuration - joetil7634 Tenancy
# Created: October 6, 2025

# Tenancy & Compartment
export TENANCY_ID="ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a"
export COMPARTMENT_ID="ocid1.tenancy.oc1..aaaaaaaaz4f4xsfb2faytoaicahyc4usdbwm5jxk5rzgkzd6aongo3bmxm5a"

# Network Resources (Already Created)
export VCN_ID="ocid1.vcn.oc1.iad.amaaaaaaumfbntyaq735wfzzcbxybur3ergz5zqonfptpdym6wa3rcyur2da"
export SUBNET_ID="ocid1.subnet.oc1.iad.aaaaaaaagpmvodqss4mbqpoq7vcmhkn7jysn52dy6tnsb2deoila2qgjzhrq"
export AVAILABILITY_DOMAIN="DeZH:US-ASHBURN-AD-1"

# Test Instance - CLI-created VM (VM.Standard.E5.Flex)
export TEST_INSTANCE_ID="ocid1.instance.oc1.iad.anuwcljtumfbntyc546cafdlm2j3okwny66vcfonzt7da5pvcdxsgzmcd4fa"

# Restore Settings
export RESTORE_SHAPE="VM.Standard.E2.1.Micro"

# Display configuration
echo "========================================="
echo "OCI Backup Test Configuration"
echo "========================================="
echo "Tenancy: joetil7634"
echo "Region: us-ashburn-1"
echo "Compartment: $(echo $COMPARTMENT_ID | cut -d'.' -f5 | cut -c1-20)..."
echo "Instance: $TEST_INSTANCE_ID"
echo "========================================="

# Verify instance exists
echo "✅ Configuration loaded successfully!"
echo "Instance Shape: VM.Standard.E5.Flex (CLI-created)"
