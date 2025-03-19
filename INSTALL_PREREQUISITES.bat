@echo off
echo ====================================
echo Web Stryker R7 Prerequisites Installer
echo ====================================

echo Checking administrator privileges...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run this script as Administrator
    pause
    exit /b 1
)

REM Check for Chocolatey
where choco >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Chocolatey...
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
)

echo Installing prerequisites...

REM Install Python
echo Installing Python 3.11...
choco install -y python311

REM Install PostgreSQL
echo Installing PostgreSQL...
choco install -y postgresql13

REM Install Redis
echo Installing Redis...
choco install -y redis-64

REM Install Docker Desktop
echo Installing Docker Desktop...
choco install -y docker-desktop

REM Install Git
echo Installing Git...
choco install -y git

REM Install Visual Studio Build Tools
echo Installing Build Tools...
choco install -y visualstudio2019buildtools

REM Optional tools
echo Installing additional tools...
choco install -y vscode
choco install -y postman

REM Refresh environment variables
call refreshenv

REM Verify installations
echo Verifying installations...

python --version
pg_config --version
redis-cli --version
docker --version
git --version

echo ====================================
echo Creating default directories...

if not exist logs mkdir logs
if not exist data mkdir data
if not exist ssl mkdir ssl

echo ====================================
echo Setting up PostgreSQL...

REM Start PostgreSQL service
net start postgresql-x64-13

REM Create database user and database
echo Creating database and user...
createdb -U postgres web_stryker
psql -U postgres -c "CREATE USER web_stryker WITH PASSWORD 'web_stryker';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE web_stryker TO web_stryker;"

echo ====================================
echo Setting up Redis...

REM Start Redis service
net start redis

echo ====================================
echo Starting Docker services...

REM Start Docker service
net start com.docker.service

echo ====================================
echo Installation complete!

echo Next steps:
echo 1. Restart your computer
echo 2. Run SETUP_PRODUCTION.bat to configure the application
echo 3. Update .env with your settings
echo 4. Start the application with RUN_PRODUCTION.bat

pause
