#!/bin/bash
# OCI VM Creation Script with Intelligent Fallback
# Handles service limits, capacity constraints, and multiple shape options
# Created: October 6, 2025

set -e  # Exit on error

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/test_config.sh" ]; then
    source "$SCRIPT_DIR/test_config.sh"
else
    echo "❌ Error: test_config.sh not found"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VM_NAME="${1:-backup-test-vm-cli}"
IMAGE_NAME="Oracle-Linux-8"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}OCI VM Creation Script${NC}"
echo -e "${BLUE}=========================================${NC}"
echo "VM Name: $VM_NAME"
echo "Compartment: $(echo $COMPARTMENT_ID | cut -d'.' -f5 | cut -c1-20)..."
echo "Availability Domain: $AVAILABILITY_DOMAIN"
echo ""

# Function to check shape availability
check_shape_availability() {
    local shape=$1
    local limit_name=$2
    
    echo -e "${YELLOW}Checking availability for $shape...${NC}"
    
    local result=$(oci limits resource-availability get \
        --compartment-id "$COMPARTMENT_ID" \
        --service-name compute \
        --limit-name "$limit_name" \
        --availability-domain "$AVAILABILITY_DOMAIN" \
        2>&1 || echo "error")
    
    if echo "$result" | grep -q "error\|Error\|NotAuthorized"; then
        echo -e "${RED}  ✗ Cannot check limits (may not have access)${NC}"
        return 2  # Unknown status
    fi
    
    local available=$(echo "$result" | grep '"available"' | grep -oE '[0-9]+' | head -1)
    local used=$(echo "$result" | grep '"used"' | grep -oE '[0-9]+' | head -1)
    
    if [ -z "$available" ]; then
        echo -e "${RED}  ✗ Could not determine availability${NC}"
        return 2
    fi
    
    echo "  Available: $available, Used: $used"
    
    if [ "$available" -gt 0 ]; then
        echo -e "${GREEN}  ✓ Shape available!${NC}"
        return 0
    else
        echo -e "${RED}  ✗ No capacity available${NC}"
        return 1
    fi
}

# Function to get latest Oracle Linux 9 image
get_oracle_linux_image() {
    echo -e "${YELLOW}Finding latest Oracle Linux 9 image...${NC}"
    
    local image_id=$(oci compute image list \
        --compartment-id "$COMPARTMENT_ID" \
        --operating-system "Oracle Linux" \
        --operating-system-version "9" \
        --sort-by TIMECREATED \
        --sort-order DESC \
        --limit 1 \
        --query 'data[0].id' \
        --raw-output 2>/dev/null)
    
    if [ -z "$image_id" ] || [ "$image_id" = "null" ]; then
        # Fallback to known Oracle Linux 9 image ID for us-ashburn-1
        image_id="ocid1.image.oc1.iad.aaaaaaaa4l64brs5udx52nedrhlex4cpaorcd2jwvpoududksmw4lgmameqq"
        echo -e "${YELLOW}  Using known Oracle Linux 9 image ID${NC}"
    else
        echo -e "${GREEN}  ✓ Found image: $(echo $image_id | cut -d'.' -f5 | cut -c1-20)...${NC}"
    fi
    
    echo "$image_id"
}

# Function to create VM with specific shape
create_vm() {
    local shape=$1
    local image_id=$2
    local ocpus=${3:-1}
    local memory=${4:-8}
    
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}Creating VM Instance${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo "Shape: $shape"
    [ "$shape" == *"Flex"* ] && echo "OCPUs: $ocpus, Memory: ${memory}GB"
    echo "Image: $(echo $image_id | cut -d'.' -f5 | cut -c1-20)..."
    echo ""
    
    # Build instance creation command
    local create_cmd="oci compute instance launch \
        --compartment-id '$COMPARTMENT_ID' \
        --availability-domain '$AVAILABILITY_DOMAIN' \
        --shape '$shape' \
        --subnet-id '$SUBNET_ID' \
        --image-id '$image_id' \
        --display-name '$VM_NAME' \
        --assign-public-ip true"
    
    # Add shape config for flexible shapes
    if [[ "$shape" == *"Flex"* ]]; then
        create_cmd="$create_cmd --shape-config '{\"ocpus\": $ocpus, \"memoryInGBs\": $memory}'"
    fi
    
    # Add wait for running state
    create_cmd="$create_cmd --wait-for-state RUNNING --max-wait-seconds 300"
    
    echo -e "${YELLOW}Launching instance (this may take 2-3 minutes)...${NC}"
    echo ""
    
    # Execute command
    local result=$(eval $create_cmd 2>&1)
    
    if echo "$result" | grep -q "\"lifecycle-state\": \"RUNNING\""; then
        local instance_id=$(echo "$result" | grep '"id":' | head -1 | grep -oE 'ocid1\.instance\.[^"]+')
        echo -e "${GREEN}=========================================${NC}"
        echo -e "${GREEN}✓ VM Created Successfully!${NC}"
        echo -e "${GREEN}=========================================${NC}"
        echo "Instance ID: $instance_id"
        echo ""
        echo -e "${YELLOW}Updating test_config.sh with new instance ID...${NC}"
        
        # Update test_config.sh with new instance ID
        if [ -f "$SCRIPT_DIR/test_config.sh" ]; then
            sed -i.bak "s|export TEST_INSTANCE_ID=.*|export TEST_INSTANCE_ID=\"$instance_id\"|g" "$SCRIPT_DIR/test_config.sh"
            echo -e "${GREEN}✓ Configuration updated${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}Next Steps:${NC}"
        echo "1. Reload configuration: ${BLUE}source test_config.sh${NC}"
        echo "2. Run backup test: ${BLUE}python3 python/backup.py --compartment \"\$COMPARTMENT_ID\" --instance \"\$TEST_INSTANCE_ID\"${NC}"
        echo ""
        
        return 0
    else
        echo -e "${RED}=========================================${NC}"
        echo -e "${RED}✗ VM Creation Failed${NC}"
        echo -e "${RED}=========================================${NC}"
        echo "$result"
        echo ""
        return 1
    fi
}

# Main execution flow
main() {
    echo -e "${YELLOW}Step 1: Getting Oracle Linux 8 image...${NC}"
    IMAGE_ID=$(get_oracle_linux_image)
    echo ""
    
    echo -e "${YELLOW}Step 2: Checking shape availability...${NC}"
    echo ""
    
    # Try shapes in priority order
    # Priority 1: VM.Standard.E2.1.Micro (Always Free)
    if check_shape_availability "VM.Standard.E2.1.Micro" "vm-standard-e2-1-micro-count"; then
        echo ""
        create_vm "VM.Standard.E2.1.Micro" "$IMAGE_ID"
        exit $?
    fi
    
    echo ""
    
    # Priority 2: VM.Standard.A1.Flex (ARM Always Free)
    if check_shape_availability "VM.Standard.A1.Flex" "vm-standard-a1-flex-count"; then
        echo ""
        echo -e "${YELLOW}Attempting ARM-based Always Free instance...${NC}"
        create_vm "VM.Standard.A1.Flex" "$IMAGE_ID" 1 6
        exit $?
    fi
    
    echo ""
    
    # Priority 3: VM.Standard.E4.Flex (Low cost, widely available)
    if check_shape_availability "VM.Standard.E4.Flex" "vm-standard-e4-flex-count"; then
        echo ""
        echo -e "${YELLOW}Attempting flexible instance (minimal cost ~\$0.05/hour)...${NC}"
        create_vm "VM.Standard.E4.Flex" "$IMAGE_ID" 1 16
        exit $?
    fi
    
    echo ""
    
    # Priority 4: VM.Standard.E5.Flex (Latest generation)
    echo -e "${YELLOW}Checking VM.Standard.E5.Flex...${NC}"
    echo -e "${YELLOW}Attempting latest generation flexible instance...${NC}"
    create_vm "VM.Standard.E5.Flex" "$IMAGE_ID" 1 12
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        exit 0
    fi
    
    echo ""
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}All Shape Options Exhausted${NC}"
    echo -e "${RED}=========================================${NC}"
    echo ""
    echo "Possible solutions:"
    echo "1. Try a different availability domain"
    echo "2. Try a different region (us-phoenix-1)"
    echo "3. Request service limit increase: https://cloud.oracle.com/limits"
    echo "4. Use OCI Console to create VM manually"
    echo "5. Wait and retry later (capacity may free up)"
    echo ""
    exit 1
}

# Run main function
main
