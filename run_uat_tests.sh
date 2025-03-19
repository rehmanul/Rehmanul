#!/bin/bash
echo "Starting Web Stryker R7 UAT Tests"
echo "================================"

# Create UAT environment
cp .env.example .env.uat

# Start UAT environment
echo "Starting UAT environment..."
docker-compose -f docker-compose.uat.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run Web Interface Tests
echo "Running Web Interface Tests..."
python -m pytest tests/web_interface/test_dashboard.py
python -m pytest tests/web_interface/test_extraction.py

# Run Backend Tests
echo "Running Backend Performance Tests..."
docker-compose exec -T web python -c "
from extraction_service import run_performance_test
TEST_URLS = [
    'https://www.example.com',
    'https://www.wikipedia.org',
    'https://www.python.org'
]
run_performance_test(urls=TEST_URLS, concurrent=5)
"

# Run Load Tests
echo "Running Load Tests..."
ab -n 100 -c 10 http://localhost/

# Run Integration Tests
echo "Testing API Integrations..."
curl -X POST http://localhost/api/test/azure-openai
curl -X POST http://localhost/api/test/knowledge-graph

# Check Database Operations
echo "Verifying Data Persistence..."
docker-compose exec -T web python -c "
from data_repository import verify_persistence
verify_persistence()
"

# Generate Performance Report
echo "Generating Performance Report..."
docker-compose exec -T web python -c "
from monitoring import generate_report
generate_report('uat_test_report.html')
"

# Check service health
echo "Checking Service Health..."
curl -f http://localhost/health || echo "Health check failed!"

# Display resource usage
echo "Resource Usage:"
docker stats --no-stream web-stryker-web-1

echo "UAT Tests Completed"
echo "==================="
echo "Check uat_test_report.html for detailed results"
