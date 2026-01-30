#!/bin/bash

# Fix Arabic Slugs Script
# Quick script to run the fix_arabic_slugs management command

echo "=========================================="
echo "   Fix Arabic Slugs for Categories & Ads"
echo "=========================================="
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first."
    exit 1
fi

# Function to show menu
show_menu() {
    echo "Select an option:"
    echo "1) Dry run - Preview all changes (Categories & Ads)"
    echo "2) Dry run - Preview Categories only"
    echo "3) Dry run - Preview Ads only"
    echo "4) Fix all (Categories & Ads) - LIVE"
    echo "5) Fix Categories only - LIVE"
    echo "6) Fix Ads only - LIVE"
    echo "7) Exit"
    echo ""
    read -p "Enter your choice [1-7]: " choice
}

# Function to run command
run_command() {
    local cmd="$1"
    echo ""
    echo "Running: poetry run python manage.py $cmd"
    echo "----------------------------------------"
    poetry run python manage.py $cmd
    echo ""
    echo "✅ Command completed!"
    echo ""
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1)
            run_command "fix_arabic_slugs --dry-run"
            ;;
        2)
            run_command "fix_arabic_slugs --dry-run --categories-only"
            ;;
        3)
            run_command "fix_arabic_slugs --dry-run --ads-only"
            ;;
        4)
            read -p "⚠️  This will modify the database. Continue? (y/N): " confirm
            if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
                run_command "fix_arabic_slugs"
            else
                echo "Cancelled."
            fi
            ;;
        5)
            read -p "⚠️  This will modify the database. Continue? (y/N): " confirm
            if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
                run_command "fix_arabic_slugs --categories-only"
            else
                echo "Cancelled."
            fi
            ;;
        6)
            read -p "⚠️  This will modify the database. Continue? (y/N): " confirm
            if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
                run_command "fix_arabic_slugs --ads-only"
            else
                echo "Cancelled."
            fi
            ;;
        7)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please try again."
            echo ""
            ;;
    esac
    
    read -p "Press Enter to continue..."
    clear
done
