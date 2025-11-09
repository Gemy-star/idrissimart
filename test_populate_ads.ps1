# Quick Test Script for Populate Ads Command
# PowerShell Script

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "POPULATE ADS - QUICK TEST" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Yellow
& C:/WORK/idrissimart/.venv/Scripts/Activate.ps1

# Create a small batch of test ads
Write-Host ""
Write-Host "[2/4] Creating 5 test ads with images..." -ForegroundColor Yellow
python manage.py populate_ads 5 --country_code=EG

# Show command help
Write-Host ""
Write-Host "[3/4] Command help:" -ForegroundColor Yellow
python manage.py populate_ads --help

# Instructions for updating existing ads
Write-Host ""
Write-Host "[4/4] To update existing ads without images, run:" -ForegroundColor Yellow
Write-Host "  python manage.py populate_ads 0 --update_existing" -ForegroundColor Green

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "✅ TEST COMPLETE!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Check admin dashboard to see the created ads" -ForegroundColor White
Write-Host "2. Verify images are attached to ads" -ForegroundColor White
Write-Host "3. Add more images to static/images/ads/ for variety" -ForegroundColor White
Write-Host "4. Run with larger numbers when ready (e.g., 50, 100)" -ForegroundColor White
