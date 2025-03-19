@echo off
echo ================================
echo Web Stryker R7 Production Setup
echo ================================

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or later.
    exit /b 1
)

REM Check if PostgreSQL is installed
pg_config --version > nul 2>&1
if errorlevel 1 (
    echo PostgreSQL is not installed! Please install PostgreSQL 12 or later.
    exit /b 1
)

REM Check if Redis is installed
redis-cli --version > nul 2>&1
if errorlevel 1 (
    echo Redis is not installed! Please install Redis.
    exit /b 1
)

REM Create virtual environment if not exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Install production dependencies
echo Installing production dependencies...
pip install -r requirements.txt

REM Create necessary directories
if not exist logs mkdir logs
if not exist data mkdir data

REM Check if .env exists, if not copy from example
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please update the .env file with your production settings!
)

REM Initialize database
echo Initializing database...
set PGPASSWORD=%DB_PASSWORD%
createdb -U %DB_USER% web_stryker 2> nul

REM Apply database schema
psql -U %DB_USER% -d web_stryker -f schema.sql

REM Set up logging
echo Setting up logging configuration...
python -c "import logging; logging.basicConfig(filename='logs/web_stryker.log', level=logging.INFO)"

REM Initialize Redis
echo Initializing Redis...
redis-cli FLUSHDB

REM Check SSL certificates
if not exist ssl (
    echo Creating SSL certificates directory...
    mkdir ssl
    echo Please place your SSL certificates in the ssl directory!
)

REM Set up monitoring
echo Setting up monitoring...
if not exist monitoring\data mkdir monitoring\data

REM Set up Prometheus
copy monitoring\prometheus.yml monitoring\data\prometheus.yml

REM Set up Grafana dashboards
if not exist monitoring\grafana\data mkdir monitoring\grafana\data
xcopy /E /I monitoring\grafana\dashboards monitoring\grafana\data\dashboards

REM Production environment checks
echo Running production environment checks...
python -c "from web.database import init_schema; init_schema()"

echo ================================
echo Production setup complete!
echo.
echo Next steps:
echo 1. Review and update .env file with production settings
echo 2. Install SSL certificates in ssl directory
echo 3. Set up reverse proxy (nginx/apache)
echo 4. Configure monitoring tools
echo 5. Set up backup scripts
echo.
echo Run 'RUN_PRODUCTION.bat' to start the application
echo ================================

pause
