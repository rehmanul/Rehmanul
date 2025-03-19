import time
import uuid
import traceback
import re
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from datetime import datetime

# Import domain models and extractors
from domain_models import CompanyEntity, ProductEntity, ExtractionState, global_stats
from config import config
from logging_system import log_repository, log_execution_time
from extractors_base import CompanyExtractor, ContactExtractor, ProductExtractor
from google_sheets_integration import GoogleSheetsIntegration

class ExtractionService:
    """Main service for extracting data"""
    
    def __init__(self):
        """Initialize extraction service"""
        self.config_data = config
        self.sheets_integration = GoogleSheetsIntegration('credentials.json', 'Web Stryker Pro+')
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    async def fetch_content(self, url: str, extraction_id: str) -> Optional[str]:
        """Fetch content from URL with retry logic"""
        headers = {
            "User-Agent": self.config_data.get("USER_AGENT", "Mozilla/5.0 (compatible; WebStrykerPython/1.0)"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        max_retries = self.config_data.get("MAX_RETRIES", 3)
        timeout_seconds = self.config_data.get("TIMEOUT_SECONDS", 30)
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=timeout_seconds)
                if response.status_code == 200:
                    return response.text
                
                log_repository.log_error(
                    url, extraction_id, "FetchError", 
                    f"Failed to fetch content: HTTP {response.status_code}"
                )
                
            except requests.RequestException as e:
                log_repository.log_error(
                    url, extraction_id, "FetchError", 
                    f"Fetch attempt {attempt + 1} failed: {str(e)}"
                )
            
            # Add exponential backoff with jitter
            import random
            sleep_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)
        
        return None
    
    def format_for_sheets(self, company: CompanyEntity) -> List[str]:
        """Format company data for Google Sheets."""
        # Get primary product
        primary_product = company.products[0] if company.products else None
        
        # Format additional products
        additional_products = []
        if len(company.products) > 1:
            for product in company.products[1:]:
                product_info = {
                    'name': product.product_name,
                    'category': product.main_category,
                    'price': f"{product.price} {product.currency}" if product.price > 0 else "N/A"
                }
                additional_products.append(str(product_info))
        
        # Prepare row data
        row_data = [
            company.url,
            company.company_name,
            company.company_type,
            company.company_description[:500] if company.company_description else "",
            "; ".join(company.emails),
            "; ".join(company.phones),
            "; ".join(company.addresses),
            primary_product.product_name if primary_product else "",
            primary_product.main_category if primary_product else "",
            f"{primary_product.price} {primary_product.currency}" if primary_product and primary_product.price > 0 else "N/A",
            primary_product.product_description[:500] if primary_product and primary_product.product_description else "",
            "; ".join(primary_product.features[:5]) if primary_product and primary_product.features else "",
            "; ".join(f"{k}: {v}" for k, v in list(primary_product.specifications.items())[:3]) if primary_product and primary_product.specifications else "",
            " | ".join(additional_products),
            datetime.now().isoformat()
        ]
        
        return row_data
    
    @log_execution_time()
    async def extract_data(self, url: str, extraction_id: str, extraction_state: ExtractionState) -> Optional[CompanyEntity]:
        """Extract company and product data"""
        # Fetch the URL content
        extraction_state.update_progress(15, "Fetching website content")
        content = await self.fetch_content(url, extraction_id)
        if not content:
            return None
        
        # Create company entity
        company = CompanyEntity()
        company.url = url
        
        # Extract company information
        extraction_state.update_progress(25, "Extracting company information")
        company_extractor = CompanyExtractor(self.config_data)
        company_extractor.extract(content, url, company)
        
        # Extract contact information
        extraction_state.update_progress(40, "Extracting contact information")
        contact_extractor = ContactExtractor(self.config_data)
        contact_extractor.extract(content, url, company)
        
        # Extract product information
        extraction_state.update_progress(60, "Discovering product information")
        product_extractor = ProductExtractor(self.config_data)
        product_extractor.extract(content, url, company, extraction_id)
        
        # Format and send data to Google Sheets
        row_data = self.format_for_sheets(company)
        self.sheets_integration.add_row(row_data)
        
        return company
    
    async def process_url(self, url: str, extraction_id: str) -> Dict[str, Any]:
        """Process a URL for extraction"""
        try:
            # Start timing the overall extraction
            start_time = time.time()
            
            # Create extraction state
            extraction_state = ExtractionState(extraction_id, url)
            
            # Validate URL
            extraction_state.update_progress(5, "Validating URL")
            if not self.validate_url(url):
                log_repository.log_error(url, extraction_id, "ValidationError", "Invalid URL format")
                return {"success": False, "error": "Invalid URL format"}
            
            # Extract data
            extraction_state.update_progress(10, "Starting extraction")
            extracted_company = await self.extract_data(url, extraction_id, extraction_state)
            
            if not extracted_company:
                log_repository.log_operation(
                    url, extraction_id, "Extraction", "Failed", 
                    "Failed to extract data from URL"
                )
                return {"success": False, "error": "Failed to extract data from URL"}
            
            # Finalize
            extraction_state.update_progress(100, "Completed")
            
            # Calculate total duration
            end_time = time.time()
            total_duration = int((end_time - start_time) * 1000)  # in milliseconds
            
            # Log completion
            log_repository.log_operation(
                url, extraction_id, "Extraction", "Completed", 
                "Extraction completed successfully", total_duration
            )
            
            # Increment global stats
            global_stats.processed += 1
            global_stats.success += 1
            
            # Return results
            return {
                "success": True,
                "data": extracted_company.to_dict(),
                "duration_ms": total_duration
            }
            
        except Exception as e:
            stack_trace = traceback.format_exc()
            error_message = f"Error processing URL: {str(e)}"
            
            log_repository.log_error(
                url, extraction_id, "ProcessingError", 
                error_message, stack_trace
            )
            
            global_stats.fail += 1
            
            return {
                "success": False,
                "error": error_message
            }

# Create singleton instance
extraction_service = ExtractionService()
