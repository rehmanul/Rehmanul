@echo off
setlocal enabledelayedexpansion
echo Starting Web Stryker R7 UAT Tests
echo ================================

REM Setup test environment
call setup_test_env.bat
if errorlevel 1 (
    echo Test environment setup failed!
    call cleanup_test_env.bat
    exit /b 1
)

REM Start UAT environment
echo Starting UAT environment...
docker-compose -f docker-compose.uat.yml up -d
if errorlevel 1 (
    echo Failed to start UAT environment!
    call cleanup_test_env.bat
    exit /b 1
)

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 10 /nobreak

set TEST_STATUS=0

REM Run Web Interface Tests with HTML report
echo Running Web Interface Tests...
python -m pytest tests/web_interface/test_dashboard.py tests/web_interface/test_extraction.py --html=reports/test-report.html --self-contained-html
if errorlevel 1 set TEST_STATUS=1

REM Run Backend Tests
echo Running Backend Performance Tests...
docker-compose exec -T web python -c "from extraction_service import run_performance_test; TEST_URLS = ['https://www.example.com', 'https://www.wikipedia.org', 'https://www.python.org']; run_performance_test(urls=TEST_URLS, concurrent=5)"
if errorlevel 1 set TEST_STATUS=1

REM Run Load Tests
echo Running Load Tests...
python load_test.py
if errorlevel 1 set TEST_STATUS=1

REM Run Integration Tests
echo Testing API Integrations...
curl -X POST http://localhost/api/test/azure-openai
if errorlevel 1 set TEST_STATUS=1
curl -X POST http://localhost/api/test/knowledge-graph
if errorlevel 1 set TEST_STATUS=1

REM Check Database Operations
echo Verifying Data Persistence...
docker-compose exec -T web python -c "from data_repository import verify_persistence; verify_persistence()"
if errorlevel 1 set TEST_STATUS=1

REM Generate Performance Report
echo Generating Performance Report...
docker-compose exec -T web python -c "from monitoring import generate_report; generate_report('reports/uat_performance_report.html')"

REM Check service health
echo Checking Service Health...
curl -f http://localhost/health || (
    echo Health check failed!
    set TEST_STATUS=1
)

REM Display resource usage
echo Resource Usage:
docker stats --no-stream web-stryker-web-1

echo UAT Tests Completed
echo ===================
echo Test Report: reports/test-report.html
echo Performance Report: reports/uat_performance_report.html

REM Clean up environment
call cleanup_test_env.bat

if !TEST_STATUS! neq 0 (
    echo Some tests failed! Check the test report for details.
    endlocal
    exit /b 1
)

echo All tests passed successfully!
endlocal
pause
