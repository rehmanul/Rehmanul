@echo off
echo Cleaning up UAT test environment...

REM Stop and remove Docker containers
echo Stopping Docker containers...
docker-compose -f docker-compose.uat.yml down

REM Remove test reports older than 7 days
echo Cleaning old test reports...
forfiles /p reports /m *.html /d -7 /c "cmd /c del @file" 2>nul

REM Clean up temporary files
echo Cleaning temporary files...
del /f /q *.pyc 2>nul
del /f /q tests\*.pyc 2>nul
del /f /q tests\web_interface\*.pyc 2>nul

REM Clean up __pycache__ directories
rmdir /s /q tests\__pycache__ 2>nul
rmdir /s /q tests\web_interface\__pycache__ 2>nul

REM Archive logs older than 7 days
echo Archiving old logs...
if not exist "logs\archive" mkdir logs\archive
forfiles /p logs /m *.log /d -7 /c "cmd /c move @file logs\archive" 2>nul

echo Cleanup completed successfully.
