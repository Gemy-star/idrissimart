@echo off
REM Test Production Services - Windows Batch Script
REM Usage:
REM   test_services.bat          - Show help
REM   test_services.bat all      - Test all services
REM   test_services.bat paymob   - Test Paymob only
REM   test_services.bat paypal   - Test PayPal only
REM   test_services.bat twilio   - Test Twilio only
REM   test_services.bat sms +201234567890 - Test SMS

echo ================================================
echo   Production Services Test
echo ================================================
echo.

if "%1"=="" (
    echo Usage:
    echo   test_services.bat all          - Test all services
    echo   test_services.bat paymob       - Test Paymob only
    echo   test_services.bat paypal       - Test PayPal only
    echo   test_services.bat twilio       - Test Twilio only
    echo   test_services.bat sms PHONE    - Test SMS to phone number
    echo.
    pause
    exit /b
)

if "%1"=="all" (
    poetry run python test_production_services.py --all
) else if "%1"=="paymob" (
    poetry run python test_production_services.py --paymob
) else if "%1"=="paypal" (
    poetry run python test_production_services.py --paypal
) else if "%1"=="twilio" (
    poetry run python test_production_services.py --twilio
) else if "%1"=="sms" (
    if "%2"=="" (
        echo Error: Phone number required for SMS test
        echo Usage: test_services.bat sms +201234567890
    ) else (
        poetry run python test_production_services.py --sms %2
    )
) else (
    echo Unknown command: %1
    echo Use: all, paymob, paypal, twilio, or sms
)

echo.
pause
