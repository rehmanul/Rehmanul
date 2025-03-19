@echo off
echo =====================================
echo Web Stryker R7 - Prerequisites Setup
echo =====================================
echo.

echo Checking Python installation...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please download and install Python from:
    echo https://www.python.org/downloads/
    start https://www.python.org/downloads/
    pause
    exit
)

echo.
echo All prerequisites checked!
echo.
echo Next steps:
echo 1. Run SETUP_PYTHON_ENV.bat to set up the Python environment
echo 2. Run RUN_WEB_STRYKER.bat to start the application
echo.
pause
