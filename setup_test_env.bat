@echo off
echo Setting up test environment...

REM Check Python installation
python --version || (
    echo Python is not installed!
    exit /b 1
)

REM Check pip installation
pip --version || (
    echo pip is not installed!
    exit /b 1
)

REM Check Docker installation
docker --version || (
    echo Docker is not installed!
    exit /b 1
)

REM Install Chrome for Selenium tests
echo Checking Chrome installation...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1 || (
    echo Chrome is not installed! Please install Chrome browser.
    exit /b 1
)

REM Install test requirements
echo Installing test requirements...
pip install -r test-requirements.txt

REM Create test directories if they don't exist
if not exist "tests" mkdir tests
if not exist "tests\web_interface" mkdir tests\web_interface
if not exist "logs" mkdir logs
if not exist "reports" mkdir reports

REM Copy environment file if it doesn't exist
if not exist ".env.uat" (
    echo Creating UAT environment file...
    copy .env.example .env.uat
)

echo Test environment setup completed successfully.
