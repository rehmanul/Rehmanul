@echo off
echo ===================================
echo Web Stryker R7 Production Launcher
echo ===================================

REM Check environment
if not exist .env (
    echo ERROR: .env file not found! Please run SETUP_PRODUCTION.bat first.
    exit /b 1
)

REM Load environment variables
for /f "tokens=*" %%a in (.env) do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" set %%a
)

REM Check for required services
echo Checking required services...

REM Check PostgreSQL
pg_isready -h %DB_HOST% -p %DB_PORT% -U %DB_USER% > nul 2>&1
if errorlevel 1 (
    echo ERROR: PostgreSQL is not running!
    exit /b 1
)

REM Check Redis
redis-cli ping > nul 2>&1
if errorlevel 1 (
    echo ERROR: Redis is not running!
    exit /b 1
)

REM Create and activate virtual environment
if not exist .venv (
    echo Virtual environment not found! Please run SETUP_PRODUCTION.bat first.
    exit /b 1
)
call .venv\Scripts\activate

REM Check SSL certificates
if not exist "%SSL_CERT_PATH%" (
    echo ERROR: SSL certificate not found at %SSL_CERT_PATH%
    exit /b 1
)

REM Start Prometheus if enabled
if "%ENABLE_PROMETHEUS%"=="true" (
    echo Starting Prometheus...
    start /B prometheus\prometheus.exe --config.file=monitoring\prometheus.yml
)

REM Start Grafana
echo Starting Grafana...
start /B grafana-server.exe --config=monitoring\grafana\grafana.ini

REM Start Gunicorn with production settings
echo Starting Web Stryker R7...
gunicorn web_application:app ^
    --workers=%NUMBER_OF_PROCESSORS% ^
    --worker-class=gevent ^
    --bind=0.0.0.0:%PORT% ^
    --keyfile=%SSL_KEY_PATH% ^
    --certfile=%SSL_CERT_PATH% ^
    --access-logfile=logs/access.log ^
    --error-logfile=logs/error.log ^
    --log-level=%LOG_LEVEL% ^
    --capture-output ^
    --enable-stdio-inheritance ^
    --daemon

REM Start log monitoring
echo Starting log monitor...
start /B powershell -Command "Get-Content -Path logs/web_stryker.log -Wait"

echo ===================================
echo Web Stryker R7 is running!
echo.
echo Management URLs:
echo - Application: https://localhost:%PORT%
echo - Prometheus: http://localhost:%PROMETHEUS_PORT%
echo - Grafana: http://localhost:%GRAFANA_PORT%
echo.
echo Log files:
echo - Application: logs/web_stryker.log
echo - Access: logs/access.log
echo - Error: logs/error.log
echo ===================================

REM Monitor the application
:MONITOR
timeout /t 60 /nobreak > nul

REM Check if Gunicorn is running
tasklist /FI "IMAGENAME eq gunicorn.exe" 2>NUL | find /I /N "gunicorn.exe">NUL
if errorlevel 1 (
    echo WARNING: Gunicorn process not found! Attempting restart...
    goto START_APP
)

REM Check PostgreSQL connection
pg_isready -h %DB_HOST% -p %DB_PORT% -U %DB_USER% > nul 2>&1
if errorlevel 1 (
    echo WARNING: Database connection lost!
)

REM Check Redis connection
redis-cli ping > nul 2>&1
if errorlevel 1 (
    echo WARNING: Redis connection lost!
)

goto MONITOR

:START_APP
echo Restarting Web Stryker R7...
gunicorn web_application:app ^
    --workers=%NUMBER_OF_PROCESSORS% ^
    --worker-class=gevent ^
    --bind=0.0.0.0:%PORT% ^
    --keyfile=%SSL_KEY_PATH% ^
    --certfile=%SSL_CERT_PATH% ^
    --access-logfile=logs/access.log ^
    --error-logfile=logs/error.log ^
    --log-level=%LOG_LEVEL% ^
    --capture-output ^
    --enable-stdio-inheritance ^
    --daemon

goto MONITOR
