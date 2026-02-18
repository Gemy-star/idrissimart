@echo off
REM Test Services in Production Mode
REM This uses environment.production file and docker settings

echo ================================================
echo   Testing Production Services (Production Mode)
echo ================================================
echo.
echo Loading environment from environment.production...
echo.

if "%1"=="" (
    echo Usage:
    echo   test_production_mode.bat all          - Test all services
    echo   test_production_mode.bat paymob       - Test Paymob only
    echo   test_production_mode.bat paypal       - Test PayPal only
    echo   test_production_mode.bat twilio       - Test Twilio only
    echo   test_production_mode.bat sms PHONE    - Test SMS to phone number
    echo.
    pause
    exit /b
)

REM Load environment.production file
set ENV_FILE=environment.production
if exist %ENV_FILE% (
    echo Loading environment variables from %ENV_FILE%...
    for /F "tokens=1,2 delims==" %%G in (%ENV_FILE%) do (
        if not "%%G"=="" (
            if not "%%G:~0,1%"=="#" (
                set %%G=%%H
            )
        )
    )
)

REM Set to use docker settings
set DJANGO_SETTINGS_MODULE=idrissimart.settings.docker

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
        echo Usage: test_production_mode.bat sms +201234567890
    ) else (
        poetry run python test_production_services.py --sms %2
    )
) else (
    echo Unknown command: %1
    echo Use: all, paymob, paypal, twilio, or sms
)

echo.
pause
