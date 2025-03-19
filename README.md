# Web Stryker R7 Python Edition

An advanced web data extraction tool with AI-powered enrichment capabilities.

## Features

- **Robust Web Extraction**: Extract company information, contact details, and product data
- **AI Enhancement**: Improve data quality with Azure OpenAI and Google Knowledge Graph
- **Real-time Dashboard**: Monitor extractions with live updates
- **Data Analytics**: Analyze extracted data with category-based insights
- **Multiple Interfaces**: Web UI, CLI, and Python API support
- **Dark/Light Theme**: Customizable UI theme support

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start the web interface:
```bash
python main.py --web
```

4. Open http://localhost:8080 in your browser

## Detailed Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/web-stryker-r7-python.git
cd web-stryker-r7-python
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Initialize the database:
```bash
python main.py --setup
```

## Usage

### Web Interface

The web interface provides:
- Real-time dashboard with extraction statistics
- Data center for managing extractions
- System logs and analytics
- Dark/light theme support

Start the web server:
```bash
python main.py --web
```

### Command Line Interface

Extract from a single URL:
```bash
python main.py extract https://example.com
```

Process multiple URLs:
```bash
python main.py batch urls.txt --concurrent 5
```

Export data:
```bash
python main.py export data.csv
```

### Python API

```python
import asyncio
from extraction_service import extraction_service

async def extract_url(url):
    result = await extraction_service.process_url(url, "api-example")
    print(f"Extraction successful: {result['data']}")

asyncio.run(extract_url("https://example.com"))
```

## Configuration

### Environment Variables

Required API keys:
- `AZURE_OPENAI_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint
- `KNOWLEDGE_GRAPH_KEY`: Google Knowledge Graph API key

Optional settings:
- `MAX_CONCURRENT`: Maximum concurrent extractions (default: 5)
- `TIMEOUT_SECONDS`: Request timeout in seconds (default: 30)
- `LOG_LEVEL`: Logging level (default: INFO)

### Configuration File

The application also reads from `~/.web_stryker/config.json`:

```json
{
  "api": {
    "azure": {
      "openai": {
        "key": "your-key",
        "endpoint": "your-endpoint",
        "deployment": "your-deployment"
      }
    },
    "knowledge_graph": {
      "key": "your-key"
    }
  },
  "extraction": {
    "max_concurrent": 5,
    "timeout_seconds": 30
  }
}
```

## Project Structure

```
web-stryker-python/
├── domain_models.py        # Core domain entities
├── config.py              # Configuration system
├── logging_system.py      # Logging utilities
├── extractors/            # Extraction modules
│   ├── base.py           # Base extractor class
│   ├── company.py        # Company information extractor
│   ├── contact.py        # Contact details extractor
│   └── product.py        # Product data extractor
├── services/             # Core services
│   ├── extraction.py     # Main extraction service
│   ├── ai_enricher.py    # AI enhancement service
│   └── knowledge_graph.py # Knowledge graph service
├── web/                  # Web interface
│   ├── templates/        # Jinja2 templates
│   ├── static/          # Static assets
│   └── web_application.py # Flask application
├── cli/                  # Command line interface
└── tests/               # Test suite
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_extraction.py

# Run with coverage
pytest --cov=.
```

### Code Style

The project uses:
- Black for code formatting
- Flake8 for linting
- MyPy for type checking

Run all checks:
```bash
black .
flake8 .
mypy .
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and style checks
5. Submit a pull request

## Troubleshooting

### Common Issues

1. WebSocket Connection Failed
```
Check if the port 8080 is available:
netstat -ano | findstr 8080  # Windows
lsof -i :8080               # Linux/Mac
```

2. API Key Issues
```
Ensure your API keys are properly set in .env or config.json
Check API key permissions and quotas
```

3. Extraction Failures
```
Check network connectivity
Verify URL format
Review logs for specific error messages
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT models
- Google for Knowledge Graph API
- Contributors and maintainers
