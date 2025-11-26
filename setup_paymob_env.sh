#!/bin/bash

################################################################################
# Paymob Environment Variables Setup Script for Ubuntu
#
# This script helps configure Paymob payment gateway credentials securely
# on Ubuntu production servers.
#
# Usage:
#   ./setup_paymob_env.sh --interactive
#   ./setup_paymob_env.sh --api-key "KEY" --secret-key "KEY" --public-key "KEY"
#   ./setup_paymob_env.sh --env-file
#   ./setup_paymob_env.sh --systemd
#
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENV_FILE=".env"
SYSTEMD_ENV_FILE="/etc/idrissimart/environment"
EXPORT_TO_PROFILE=false
SETUP_SYSTEMD=false
INTERACTIVE=false

# Paymob credentials
PAYMOB_API_KEY=""
PAYMOB_SECRET_KEY=""
PAYMOB_PUBLIC_KEY=""
PAYMOB_IFRAME_ID=""
PAYMOB_INTEGRATION_ID=""
PAYMOB_HMAC_SECRET=""

################################################################################
# Helper Functions
################################################################################

print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

################################################################################
# Validation Functions
################################################################################

validate_credentials() {
    local has_errors=false

    if [[ -z "$PAYMOB_API_KEY" ]]; then
        print_error "API Key is required"
        has_errors=true
    elif [[ ${#PAYMOB_API_KEY} -lt 10 ]]; then
        print_warning "API Key appears to be too short"
    fi

    if [[ -z "$PAYMOB_SECRET_KEY" ]]; then
        print_error "Secret Key is required"
        has_errors=true
    elif [[ ! "$PAYMOB_SECRET_KEY" =~ ^egy_sk_ ]]; then
        print_warning "Secret Key should start with 'egy_sk_'"
    fi

    if [[ -z "$PAYMOB_PUBLIC_KEY" ]]; then
        print_error "Public Key is required"
        has_errors=true
    elif [[ ! "$PAYMOB_PUBLIC_KEY" =~ ^egy_pk_ ]]; then
        print_warning "Public Key should start with 'egy_pk_'"
    fi

    if [[ "$has_errors" == true ]]; then
        return 1
    fi

    return 0
}

################################################################################
# Interactive Setup
################################################################################

interactive_setup() {
    print_header "Paymob Configuration - Interactive Setup"

    echo "Please enter your Paymob credentials:"
    echo "(You can find these in your Paymob dashboard)"
    echo ""

    read -p "API Key: " PAYMOB_API_KEY
    read -p "Secret Key: " PAYMOB_SECRET_KEY
    read -p "Public Key: " PAYMOB_PUBLIC_KEY

    echo ""
    echo "Optional fields (press Enter to skip):"
    read -p "iFrame ID: " PAYMOB_IFRAME_ID
    read -p "Integration ID: " PAYMOB_INTEGRATION_ID
    read -p "HMAC Secret: " PAYMOB_HMAC_SECRET

    echo ""
    print_info "Configuration method:"
    echo "1) Update .env file (Django/dotenv)"
    echo "2) Export to current shell session"
    echo "3) Add to ~/.bashrc or ~/.profile"
    echo "4) Create systemd environment file"
    echo ""
    read -p "Choose method [1-4]: " method

    case $method in
        1)
            setup_env_file
            ;;
        2)
            export_to_current_shell
            ;;
        3)
            export_to_profile
            ;;
        4)
            setup_systemd_env
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

################################################################################
# Setup Methods
################################################################################

setup_env_file() {
    print_header "Updating .env File"

    if [[ ! -f "$ENV_FILE" ]]; then
        print_info "Creating new .env file..."
        touch "$ENV_FILE"
    fi

    # Backup existing file
    if [[ -s "$ENV_FILE" ]]; then
        backup_file="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$ENV_FILE" "$backup_file"
        print_info "Backed up existing .env to: $backup_file"
    fi

    # Update or add variables
    update_env_var "PAYMOB_API_KEY" "$PAYMOB_API_KEY"
    update_env_var "PAYMOB_SECRET_KEY" "$PAYMOB_SECRET_KEY"
    update_env_var "PAYMOB_PUBLIC_KEY" "$PAYMOB_PUBLIC_KEY"

    if [[ -n "$PAYMOB_IFRAME_ID" ]]; then
        update_env_var "PAYMOB_IFRAME_ID" "$PAYMOB_IFRAME_ID"
    fi

    if [[ -n "$PAYMOB_INTEGRATION_ID" ]]; then
        update_env_var "PAYMOB_INTEGRATION_ID" "$PAYMOB_INTEGRATION_ID"
    fi

    if [[ -n "$PAYMOB_HMAC_SECRET" ]]; then
        update_env_var "PAYMOB_HMAC_SECRET" "$PAYMOB_HMAC_SECRET"
    fi

    # Set restrictive permissions
    chmod 600 "$ENV_FILE"

    print_success "Environment file updated: $ENV_FILE"
    print_info "File permissions set to 600 (read/write for owner only)"

    display_configured_vars
    display_security_warnings
}

update_env_var() {
    local key="$1"
    local value="$2"

    # Escape special characters in value
    local escaped_value=$(printf '%s\n' "$value" | sed -e 's/[\/&]/\\&/g')

    if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
        # Update existing variable
        sed -i "s|^${key}=.*|${key}=${escaped_value}|" "$ENV_FILE"
    else
        # Add new variable
        echo "${key}=${escaped_value}" >> "$ENV_FILE"
    fi
}

export_to_current_shell() {
    print_header "Exporting to Current Shell Session"

    export PAYMOB_API_KEY="$PAYMOB_API_KEY"
    export PAYMOB_SECRET_KEY="$PAYMOB_SECRET_KEY"
    export PAYMOB_PUBLIC_KEY="$PAYMOB_PUBLIC_KEY"

    if [[ -n "$PAYMOB_IFRAME_ID" ]]; then
        export PAYMOB_IFRAME_ID="$PAYMOB_IFRAME_ID"
    fi

    if [[ -n "$PAYMOB_INTEGRATION_ID" ]]; then
        export PAYMOB_INTEGRATION_ID="$PAYMOB_INTEGRATION_ID"
    fi

    if [[ -n "$PAYMOB_HMAC_SECRET" ]]; then
        export PAYMOB_HMAC_SECRET="$PAYMOB_HMAC_SECRET"
    fi

    print_success "Variables exported to current shell session"
    print_warning "These variables will only persist in the current session"

    echo ""
    print_info "To export in future sessions, add these lines to your script:"
    echo ""
    generate_export_commands
}

export_to_profile() {
    print_header "Adding to Shell Profile"

    # Determine which profile file to use
    if [[ -f "$HOME/.bashrc" ]]; then
        PROFILE_FILE="$HOME/.bashrc"
    elif [[ -f "$HOME/.profile" ]]; then
        PROFILE_FILE="$HOME/.profile"
    else
        PROFILE_FILE="$HOME/.bashrc"
        touch "$PROFILE_FILE"
    fi

    print_info "Using profile file: $PROFILE_FILE"

    # Backup profile
    backup_file="${PROFILE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$PROFILE_FILE" "$backup_file"
    print_info "Backed up profile to: $backup_file"

    # Add Paymob section
    echo "" >> "$PROFILE_FILE"
    echo "# Paymob Payment Gateway Configuration" >> "$PROFILE_FILE"
    echo "# Added on $(date)" >> "$PROFILE_FILE"

    generate_export_commands >> "$PROFILE_FILE"

    print_success "Paymob variables added to $PROFILE_FILE"
    print_warning "Run 'source $PROFILE_FILE' to load in current session"
    print_warning "Or start a new terminal session"
}

setup_systemd_env() {
    print_header "Setting up Systemd Environment File"

    # Check if running as root or with sudo
    if [[ $EUID -ne 0 ]]; then
        print_error "This option requires root privileges"
        print_info "Please run with sudo: sudo ./setup_paymob_env.sh --systemd"
        exit 1
    fi

    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$SYSTEMD_ENV_FILE")"

    # Backup existing file
    if [[ -f "$SYSTEMD_ENV_FILE" ]]; then
        backup_file="${SYSTEMD_ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$SYSTEMD_ENV_FILE" "$backup_file"
        print_info "Backed up existing file to: $backup_file"
    fi

    # Create/update systemd environment file
    cat > "$SYSTEMD_ENV_FILE" <<EOF
# Paymob Payment Gateway Configuration
# Generated on $(date)

PAYMOB_API_KEY=${PAYMOB_API_KEY}
PAYMOB_SECRET_KEY=${PAYMOB_SECRET_KEY}
PAYMOB_PUBLIC_KEY=${PAYMOB_PUBLIC_KEY}
EOF

    if [[ -n "$PAYMOB_IFRAME_ID" ]]; then
        echo "PAYMOB_IFRAME_ID=${PAYMOB_IFRAME_ID}" >> "$SYSTEMD_ENV_FILE"
    fi

    if [[ -n "$PAYMOB_INTEGRATION_ID" ]]; then
        echo "PAYMOB_INTEGRATION_ID=${PAYMOB_INTEGRATION_ID}" >> "$SYSTEMD_ENV_FILE"
    fi

    if [[ -n "$PAYMOB_HMAC_SECRET" ]]; then
        echo "PAYMOB_HMAC_SECRET=${PAYMOB_HMAC_SECRET}" >> "$SYSTEMD_ENV_FILE"
    fi

    # Set restrictive permissions
    chmod 600 "$SYSTEMD_ENV_FILE"
    chown root:root "$SYSTEMD_ENV_FILE"

    print_success "Systemd environment file created: $SYSTEMD_ENV_FILE"
    print_info "File permissions set to 600 (read/write for root only)"

    echo ""
    print_info "Add this to your systemd service file:"
    echo ""
    echo "  [Service]"
    echo "  EnvironmentFile=$SYSTEMD_ENV_FILE"
    echo ""

    display_security_warnings
}

generate_export_commands() {
    echo "export PAYMOB_API_KEY=\"$PAYMOB_API_KEY\""
    echo "export PAYMOB_SECRET_KEY=\"$PAYMOB_SECRET_KEY\""
    echo "export PAYMOB_PUBLIC_KEY=\"$PAYMOB_PUBLIC_KEY\""

    if [[ -n "$PAYMOB_IFRAME_ID" ]]; then
        echo "export PAYMOB_IFRAME_ID=\"$PAYMOB_IFRAME_ID\""
    fi

    if [[ -n "$PAYMOB_INTEGRATION_ID" ]]; then
        echo "export PAYMOB_INTEGRATION_ID=\"$PAYMOB_INTEGRATION_ID\""
    fi

    if [[ -n "$PAYMOB_HMAC_SECRET" ]]; then
        echo "export PAYMOB_HMAC_SECRET=\"$PAYMOB_HMAC_SECRET\""
    fi
}

display_configured_vars() {
    echo ""
    print_info "Configured variables:"
    echo "  - PAYMOB_API_KEY: ${PAYMOB_API_KEY:0:20}..."
    echo "  - PAYMOB_SECRET_KEY: ${PAYMOB_SECRET_KEY:0:20}..."
    echo "  - PAYMOB_PUBLIC_KEY: ${PAYMOB_PUBLIC_KEY:0:20}..."

    if [[ -n "$PAYMOB_IFRAME_ID" ]]; then
        echo "  - PAYMOB_IFRAME_ID: $PAYMOB_IFRAME_ID"
    fi

    if [[ -n "$PAYMOB_INTEGRATION_ID" ]]; then
        echo "  - PAYMOB_INTEGRATION_ID: $PAYMOB_INTEGRATION_ID"
    fi

    if [[ -n "$PAYMOB_HMAC_SECRET" ]]; then
        echo "  - PAYMOB_HMAC_SECRET: ${PAYMOB_HMAC_SECRET:0:20}..."
    fi
}

display_security_warnings() {
    echo ""
    print_warning "Security Reminders:"
    echo "  1. Never commit credentials to version control"
    echo "  2. Ensure .env is in your .gitignore file"
    echo "  3. Keep credentials secure and rotate periodically"
    echo "  4. Use environment-specific credentials (test vs production)"
    echo "  5. Limit file permissions (600 for sensitive files)"
}

################################################################################
# Argument Parsing
################################################################################

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Setup Paymob environment variables on Ubuntu

OPTIONS:
    -i, --interactive           Interactive setup wizard
    -e, --env-file              Update .env file (default)
    -s, --systemd               Create systemd environment file (requires sudo)
    -p, --profile               Add to ~/.bashrc or ~/.profile

    --api-key KEY               Paymob API Key
    --secret-key KEY            Paymob Secret Key
    --public-key KEY            Paymob Public Key
    --iframe-id ID              Paymob iFrame ID (optional)
    --integration-id ID         Paymob Integration ID (optional)
    --hmac-secret SECRET        Paymob HMAC Secret (optional)

    -h, --help                  Show this help message

EXAMPLES:
    # Interactive setup
    $0 --interactive

    # Update .env file with credentials
    $0 --api-key "KEY" --secret-key "KEY" --public-key "KEY"

    # Create systemd environment file (requires sudo)
    sudo $0 --systemd --api-key "KEY" --secret-key "KEY" --public-key "KEY"

    # Add to shell profile
    $0 --profile --api-key "KEY" --secret-key "KEY" --public-key "KEY"

EOF
}

################################################################################
# Main Script
################################################################################

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--interactive)
                INTERACTIVE=true
                shift
                ;;
            -e|--env-file)
                # Default behavior
                shift
                ;;
            -s|--systemd)
                SETUP_SYSTEMD=true
                shift
                ;;
            -p|--profile)
                EXPORT_TO_PROFILE=true
                shift
                ;;
            --api-key)
                PAYMOB_API_KEY="$2"
                shift 2
                ;;
            --secret-key)
                PAYMOB_SECRET_KEY="$2"
                shift 2
                ;;
            --public-key)
                PAYMOB_PUBLIC_KEY="$2"
                shift 2
                ;;
            --iframe-id)
                PAYMOB_IFRAME_ID="$2"
                shift 2
                ;;
            --integration-id)
                PAYMOB_INTEGRATION_ID="$2"
                shift 2
                ;;
            --hmac-secret)
                PAYMOB_HMAC_SECRET="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Interactive mode
    if [[ "$INTERACTIVE" == true ]]; then
        interactive_setup
        exit 0
    fi

    # Validate credentials if provided
    if [[ -n "$PAYMOB_API_KEY" || -n "$PAYMOB_SECRET_KEY" || -n "$PAYMOB_PUBLIC_KEY" ]]; then
        if ! validate_credentials; then
            print_error "Credential validation failed"
            exit 1
        fi

        # Choose setup method
        if [[ "$SETUP_SYSTEMD" == true ]]; then
            setup_systemd_env
        elif [[ "$EXPORT_TO_PROFILE" == true ]]; then
            export_to_profile
        else
            setup_env_file
        fi
    else
        print_error "No credentials provided and not in interactive mode"
        echo ""
        show_usage
        exit 1
    fi

    print_success "Paymob configuration completed successfully!"
}

# Run main function
main "$@"
