@echo off
REM Quick Services Check - Windows Batch Script
REM Usage: check_services.bat

echo ================================================
echo   Production Services - Quick Check
echo ================================================
echo.

poetry run python check_services.py

echo.
pause
