@echo off
echo =====================================
echo Web Stryker R7 - Python Setup
echo =====================================
echo.

REM Check Python installation
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please download and install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Clean up existing virtual environment if exists
if exist .venv (
    echo Removing existing virtual environment...
    rmdir /s /q .venv
)

echo Creating virtual environment...
python -m venv .venv

REM Check if venv creation was successful
if not exist .venv\Scripts\activate.bat (
    echo [ERROR] Failed to create virtual environment!
    echo Please run this script as administrator
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Python environment setup complete!
echo.
echo Next steps:
echo 1. Run RUN_WEB_STRYKER.bat to start the application
echo.
pause
