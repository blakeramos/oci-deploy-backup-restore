#!/bin/bash
# OCI Environment Diagnostic Script
# Checks authentication, permissions, service limits, and network configuration
# Created: October 6, 2025

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load configuration if available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/test_config.sh" ]; then
    source "$SCRIPT_DIR/test_config.sh" 2>/dev/null
fi

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}OCI Environment Diagnostic Tool${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Test 1: OCI CLI Installation
echo -e "${YELLOW}Test 1: OCI CLI Installation${NC}"
if command -v oci &> /dev/null; then
    OCI_VERSION=$(oci --version 2>&1 | head -1)
    echo -e "${GREEN}✓ OCI CLI installed: $OCI_VERSION${NC}"
else
    echo -e "${RED}✗ OCI CLI not found${NC}"
    echo "  Install: brew install oci-cli"
    exit 1
fi
echo ""

# Test 2: Authentication
echo -e "${YELLOW}Test 2: Authentication${NC}"
AUTH_TEST=$(oci iam region list --output table 2>&1)
if echo "$AUTH_TEST" | grep -q "us-ashburn-1\|us-phoenix-1"; then
    echo -e "${GREEN}✓ Authentication successful${NC}"
    CURRENT_USER=$(oci iam user get --user-id $(oci iam user list --query 'data[0].id' --raw-output 2>/dev/null) --query 'data.name' --raw-output 2>/dev/null || echo "Unknown")
    echo "  User: $CURRENT_USER"
else
    echo -e "${RED}✗ Authentication failed${NC}"
    echo "  Run: oci setup config"
    exit 1
fi
echo ""

# Test 3: Configuration Variables
echo -e "${YELLOW}Test 3: Configuration Variables${NC}"
if [ -n "$COMPARTMENT_ID" ]; then
    echo -e "${GREEN}✓ COMPARTMENT_ID set${NC}"
    echo "  Value: $(echo $COMPARTMENT_ID | cut -d'.' -f5 | cut -c1-20)..."
else
    echo -e "${RED}✗ COMPARTMENT_ID not set${NC}"
fi

if [ -n "$AVAILABILITY_DOMAIN" ]; then
    echo -e "${GREEN}✓ AVAILABILITY_DOMAIN set${NC}"
    echo "  Value: $AVAILABILITY_DOMAIN"
else
    echo -e "${RED}✗ AVAILABILITY_DOMAIN not set${NC}"
fi

if [ -n "$SUBNET_ID" ]; then
    echo -e "${GREEN}✓ SUBNET_ID set${NC}"
    echo "  Value: $(echo $SUBNET_ID | cut -d'.' -f5 | cut -c1-20)..."
else
    echo -e "${RED}✗ SUBNET_ID not set${NC}"
fi
echo ""

# Test 4: Network Resources
echo -e "${YELLOW}Test 4: Network Resources${NC}"
if [ -n "$VCN_ID" ]; then
    VCN_STATE=$(oci network vcn get --vcn-id "$VCN_ID" --query 'data."lifecycle-state"' --raw-output 2>/dev/null)
    if [ "$VCN_STATE" = "AVAILABLE" ]; then
        echo -e "${GREEN}✓ VCN is AVAILABLE${NC}"
    else
        echo -e "${RED}✗ VCN state: $VCN_STATE${NC}"
    fi
else
    echo -e "${YELLOW}⊘ VCN not configured${NC}"
fi

if [ -n "$SUBNET_ID" ]; then
    SUBNET_STATE=$(oci network subnet get --subnet-id "$SUBNET_ID" --query 'data."lifecycle-state"' --raw-output 2>/dev/null)
    if [ "$SUBNET_STATE" = "AVAILABLE" ]; then
        echo -e "${GREEN}✓ Subnet is AVAILABLE${NC}"
    else
        echo -e "${RED}✗ Subnet state: $SUBNET_STATE${NC}"
    fi
else
    echo -e "${YELLOW}⊘ Subnet not configured${NC}"
fi
echo ""

# Test 5: Service Limits - Compute Shapes
echo -e "${YELLOW}Test 5: Service Limits (Compute Shapes)${NC}"

if [ -n "$COMPARTMENT_ID" ] && [ -n "$AVAILABILITY_DOMAIN" ]; then
    # Check VM.Standard.E2.1.Micro (Always Free)
    echo "Checking VM.Standard.E2.1.Micro (Always Free)..."
    MICRO_LIMITS=$(oci limits resource-availability get \
        --compartment-id "$COMPARTMENT_ID" \
        --service-name compute \
        --limit-name vm-standard-e2-1-micro-count \
        --availability-domain "$AVAILABILITY_DOMAIN" 2>&1)
    
    if echo "$MICRO_LIMITS" | grep -q '"available"'; then
        MICRO_AVAIL=$(echo "$MICRO_LIMITS" | grep '"available"' | grep -oE '[0-9]+' | head -1)
        MICRO_USED=$(echo "$MICRO_LIMITS" | grep '"used"' | grep -oE '[0-9]+' | head -1)
        if [ "$MICRO_AVAIL" -gt 0 ]; then
            echo -e "${GREEN}✓ Available: $MICRO_AVAIL, Used: $MICRO_USED${NC}"
        else
            echo -e "${RED}✗ No capacity available (Used: $MICRO_USED)${NC}"
        fi
    else
        echo -e "${YELLOW}⊘ Cannot check limits${NC}"
    fi
    
    # Check VM.Standard.E4.Flex
    echo "Checking VM.Standard.E4.Flex..."
    E4_LIMITS=$(oci limits resource-availability get \
        --compartment-id "$COMPARTMENT_ID" \
        --service-name compute \
        --limit-name vm-standard-e4-flex-count \
        --availability-domain "$AVAILABILITY_DOMAIN" 2>&1)
    
    if echo "$E4_LIMITS" | grep -q '"available"'; then
        E4_AVAIL=$(echo "$E4_LIMITS" | grep '"available"' | grep -oE '[0-9]+' | head -1)
        E4_USED=$(echo "$E4_LIMITS" | grep '"used"' | grep -oE '[0-9]+' | head -1)
        if [ "$E4_AVAIL" -gt 0 ]; then
            echo -e "${GREEN}✓ Available: $E4_AVAIL, Used: $E4_USED${NC}"
        else
            echo -e "${RED}✗ No capacity available (Used: $E4_USED)${NC}"
        fi
    else
        echo -e "${YELLOW}⊘ Cannot check limits${NC}"
    fi
    
    # Check VM.Standard.A1.Flex (ARM Always Free)
    echo "Checking VM.Standard.A1.Flex (ARM Always Free)..."
    A1_LIMITS=$(oci limits resource-availability get \
        --compartment-id "$COMPARTMENT_ID" \
        --service-name compute \
        --limit-name vm-standard-a1-flex-count \
        --availability-domain "$AVAILABILITY_DOMAIN" 2>&1)
    
    if echo "$A1_LIMITS" | grep -q '"available"'; then
        A1_AVAIL=$(echo "$A1_LIMITS" | grep '"available"' | grep -oE '[0-9]+' | head -1)
        A1_USED=$(echo "$A1_LIMITS" | grep '"used"' | grep -oE '[0-9]+' | head -1)
        if [ "$A1_AVAIL" -gt 0 ]; then
            echo -e "${GREEN}✓ Available: $A1_AVAIL, Used: $A1_USED${NC}"
        else
            echo -e "${RED}✗ No capacity available (Used: $A1_USED)${NC}"
        fi
    else
        echo -e "${YELLOW}⊘ Cannot check limits${NC}"
    fi
else
    echo -e "${YELLOW}⊘ Compartment or AD not configured - skipping${NC}"
fi
echo ""

# Test 6: IAM Permissions
echo -e "${YELLOW}Test 6: IAM Permissions${NC}"
if [ -n "$COMPARTMENT_ID" ]; then
    # Try to list instances (requires read permission)
    INSTANCE_TEST=$(oci compute instance list --compartment-id "$COMPARTMENT_ID" --limit 1 2>&1)
    if echo "$INSTANCE_TEST" | grep -q "data\|NotAuthorized"; then
        if echo "$INSTANCE_TEST" | grep -q "NotAuthorized"; then
            echo -e "${RED}✗ Not authorized to list instances${NC}"
            echo "  Solution: Add user to Administrators group"
        else
            echo -e "${GREEN}✓ Can list instances${NC}"
        fi
    fi
    
    # Try to list volumes
    VOLUME_TEST=$(oci bv volume list --compartment-id "$COMPARTMENT_ID" --limit 1 2>&1)
    if echo "$VOLUME_TEST" | grep -q "data\|NotAuthorized"; then
        if echo "$VOLUME_TEST" | grep -q "NotAuthorized"; then
            echo -e "${RED}✗ Not authorized to list volumes${NC}"
        else
            echo -e "${GREEN}✓ Can list volumes${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⊘ Compartment not configured - skipping${NC}"
fi
echo ""

# Test 7: Python Environment
echo -e "${YELLOW}Test 7: Python Environment${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓ Python installed: $PYTHON_VERSION${NC}"
    
    # Check for OCI SDK
    if python3 -c "import oci" 2>/dev/null; then
        OCI_SDK_VERSION=$(python3 -c "import oci; print(oci.__version__)" 2>/dev/null)
        echo -e "${GREEN}✓ OCI Python SDK installed: $OCI_SDK_VERSION${NC}"
    else
        echo -e "${RED}✗ OCI Python SDK not installed${NC}"
        echo "  Install: pip3 install -r python/requirements.txt"
    fi
else
    echo -e "${RED}✗ Python 3 not found${NC}"
fi
echo ""

# Test 8: Existing Instances
echo -e "${YELLOW}Test 8: Existing Instances${NC}"
if [ -n "$COMPARTMENT_ID" ]; then
    INSTANCE_COUNT=$(oci compute instance list --compartment-id "$COMPARTMENT_ID" --query 'length(data)' --raw-output 2>/dev/null || echo "0")
    if [ "$INSTANCE_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ Found $INSTANCE_COUNT instance(s) in compartment${NC}"
        echo ""
        echo "Recent instances:"
        oci compute instance list \
            --compartment-id "$COMPARTMENT_ID" \
            --sort-by TIMECREATED \
            --sort-order DESC \
            --limit 3 \
            --query 'data[*].{"Name":"display-name","State":"lifecycle-state","Shape":"shape","Created":"time-created"}' \
            --output table 2>/dev/null || echo "  (Cannot list instances)"
    else
        echo -e "${YELLOW}⊘ No instances found in compartment${NC}"
    fi
else
    echo -e "${YELLOW}⊘ Compartment not configured - skipping${NC}"
fi
echo ""

# Summary and Recommendations
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Summary and Recommendations${NC}"
echo -e "${BLUE}=========================================${NC}"

if [ -z "$COMPARTMENT_ID" ] || [ -z "$AVAILABILITY_DOMAIN" ] || [ -z "$SUBNET_ID" ]; then
    echo -e "${YELLOW}⚠ Configuration incomplete${NC}"
    echo "  Run: source test_config.sh"
    echo ""
fi

echo "Next steps to create a VM via CLI:"
echo ""
echo "1. ${BLUE}Ensure configuration is loaded:${NC}"
echo "   source test_config.sh"
echo ""
echo "2. ${BLUE}Run the intelligent VM creation script:${NC}"
echo "   bash create_vm_cli.sh"
echo ""
echo "3. ${BLUE}Or manually specify a shape:${NC}"
echo "   bash create_vm_cli.sh my-custom-vm-name"
echo ""
echo "4. ${BLUE}If all shapes fail, try:${NC}"
echo "   - Different availability domain"
echo "   - Different region (us-phoenix-1)"
echo "   - Request service limit increase"
echo "   - Use OCI Console temporarily"
echo ""

exit 0
