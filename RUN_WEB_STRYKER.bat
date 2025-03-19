@echo off
echo ===============================
echo Web Stryker R7 Quick Launcher
echo ===============================
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist .venv (
    echo [ERROR] Python virtual environment not found!
    echo Please run SETUP_PYTHON_ENV.bat first
    pause
    exit /b 1
)

REM Environment setup
if not exist .env (
    echo Setting up environment configuration...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit the .env file with your API keys.
    echo Opening .env file for editing...
    timeout /t 3
    notepad .env
    echo.
    echo After saving the .env file, press any key to continue...
    pause > nul
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo.
echo Starting Web Stryker...
echo.
echo ================================
echo Web Stryker R7 is now running!
echo ================================
echo.
echo Access the application at: http://localhost:5000
echo Health check at: http://localhost:5000/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the application with Flask development server
set FLASK_APP=web_application.py
set FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000
