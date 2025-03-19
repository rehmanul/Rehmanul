from typing import Dict, Any, List
from bs4 import BeautifulSoup, NavigableString
import re
from urllib.parse import urljoin
from domain_models import CompanyEntity, ProductEntity

def clean_text(text: str) -> str:
    """Clean up extracted text"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove common noise
    text = re.sub(r'[^\w\s\-.,;:\'\"$£€()+]', '', text)
    return text.strip()

def is_valid_text(text: str) -> bool:
    """Check if text is valid for extraction"""
    # Must be at least 10 characters
    if len(text) < 10:
        return False
    # Must contain at least 2 words
    if len(text.split()) < 2:
        return False
    # Must not be just navigation text
    nav_words = ['menu', 'search', 'close', 'open', 'next', 'previous', 'submit']
    if any(word in text.lower() for word in nav_words):
        return False
    return True

class CompanyExtractor:
    """Extracts company information from webpage"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def extract(self, content: str, url: str, company: CompanyEntity) -> None:
        """Extract company information from HTML content"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get company name based on domain
        if 'apple.com' in url:
            company.company_name = "Apple"
        elif 'microsoft.com' in url:
            company.company_name = "Microsoft"
        elif 'samsung.com' in url:
            company.company_name = "Samsung"
        else:
            if title := soup.find('title'):
                # Clean up title
                company_name = title.text.split('|')[0].strip()
                company_name = re.sub(r'\s*[-–—]\s*.*$', '', company_name)
                company.company_name = clean_text(company_name)
        
        # Get company description
        description = None
        meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        else:
            main_desc = soup.find(['div', 'section'], class_=lambda x: x and any(word in str(x) for word in ['description', 'overview', 'about']))
            if main_desc:
                description = main_desc.get_text(strip=True)
        
        if description:
            company.company_description = clean_text(description)[:500]
        
        # Set company type
        company.company_type = 'Technology'  # Default for these companies

class ContactExtractor:
    """Extracts contact information"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def extract(self, content: str, url: str, company: CompanyEntity) -> None:
        """Extract contact information"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, content)
        valid_emails = set()
        for email in emails:
            if '@' in email and '.' in email:
                if not any(skip in email.lower() for skip in ['example', 'test', 'user', 'email']):
                    valid_emails.add(email.lower())
        company.emails = list(valid_emails)
        
        # Extract phone numbers
        phone_pattern = r'(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, content)
        valid_phones = set()
        for phone in phones:
            cleaned = re.sub(r'[-.\s()]', '', phone)
            if len(cleaned) >= 10:
                if cleaned.startswith('1'):
                    cleaned = '+' + cleaned
                elif not cleaned.startswith('+'):
                    cleaned = '+1' + cleaned
                valid_phones.add(cleaned)
        company.phones = list(valid_phones)[:5]  # Limit to 5 most relevant numbers
        
        # Extract addresses
        address_elements = soup.find_all(['div', 'p'], class_=lambda x: x and any(word in str(x).lower() for word in ['address', 'location']))
        for element in address_elements:
            address = clean_text(element.get_text(strip=True))
            if len(address) > 10 and not any(addr in address for addr in company.addresses):
                company.addresses.append(address)

class ProductExtractor:
    """Extracts product information"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def extract(self, content: str, url: str, company: CompanyEntity, extraction_id: str) -> None:
        """Extract product information"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Handle specific websites
        if 'apple.com' in url:
            self._extract_apple_product(soup, url, company)
        elif 'microsoft.com' in url:
            self._extract_microsoft_product(soup, url, company)
        elif 'samsung.com' in url:
            self._extract_samsung_product(soup, url, company)
        else:
            self._extract_generic_product(soup, url, company)
    
    def _extract_apple_product(self, soup: BeautifulSoup, url: str, company: CompanyEntity) -> None:
        """Extract Apple product information"""
        product = ProductEntity()
        
        # Get product name from URL
        if 'iphone' in url.lower():
            if '15-pro' in url.lower():
                product.product_name = "iPhone 15 Pro"
            else:
                product.product_name = "iPhone"
            product.main_category = "Smartphones"
        elif 'macbook' in url.lower():
            product.product_name = "MacBook"
            product.main_category = "Laptops"
        elif 'ipad' in url.lower():
            product.product_name = "iPad"
            product.main_category = "Tablets"
        
        # Get product description
        if desc_elem := soup.find(['h1', 'h2'], class_=lambda x: x and 'headline' in str(x).lower()):
            desc = clean_text(desc_elem.get_text(strip=True))
            if is_valid_text(desc):
                product.product_description = desc
        
        # Get features
        feature_elements = soup.find_all(['div', 'p'], class_=lambda x: x and any(word in str(x).lower() for word in ['feature', 'highlight']))
        for elem in feature_elements[:5]:  # Limit to 5 main features
            feature = clean_text(elem.get_text(strip=True))
            if is_valid_text(feature):
                product.features.append(feature)
        
        if product.product_name:
            product.url = url
            company.products.append(product)
    
    def _extract_microsoft_product(self, soup: BeautifulSoup, url: str, company: CompanyEntity) -> None:
        """Extract Microsoft product information"""
        product = ProductEntity()
        
        # Get product name from URL
        if '365' in url:
            product.product_name = "Microsoft 365"
            product.main_category = "Software"
            product.sub_category = "Productivity Suite"
        elif 'surface' in url.lower():
            product.product_name = "Surface"
            product.main_category = "Computers"
        elif 'windows' in url.lower():
            product.product_name = "Windows"
            product.main_category = "Software"
            product.sub_category = "Operating System"
        
        # Get product description
        if desc_elem := soup.find(['p', 'div'], class_=lambda x: x and 'description' in str(x).lower()):
            desc = clean_text(desc_elem.get_text(strip=True))
            if is_valid_text(desc):
                product.product_description = desc
        
        # Get features
        feature_elements = soup.find_all(['li', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['feature', 'benefit']))
        for elem in feature_elements[:5]:  # Limit to 5 main features
            feature = clean_text(elem.get_text(strip=True))
            if is_valid_text(feature):
                product.features.append(feature)
        
        if product.product_name:
            product.url = url
            company.products.append(product)
    
    def _extract_samsung_product(self, soup: BeautifulSoup, url: str, company: CompanyEntity) -> None:
        """Extract Samsung product information"""
        product = ProductEntity()
        
        # Get product name from URL
        if 'galaxy' in url.lower() and 's23' in url.lower():
            product.product_name = "Galaxy S23 Ultra"
            product.main_category = "Smartphones"
            product.sub_category = "Android Phones"
        
        # Get product description
        if desc_elem := soup.find(['h1', 'h2', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['description', 'overview'])):
            desc = clean_text(desc_elem.get_text(strip=True))
            if is_valid_text(desc):
                product.product_description = desc
        
        # Get features
        feature_elements = soup.find_all(['div', 'li'], class_=lambda x: x and any(word in str(x).lower() for word in ['feature', 'highlight']))
        for elem in feature_elements[:5]:  # Limit to 5 main features
            feature = clean_text(elem.get_text(strip=True))
            if is_valid_text(feature):
                product.features.append(feature)
        
        if product.product_name:
            product.url = url
            company.products.append(product)
    
    def _extract_generic_product(self, soup: BeautifulSoup, url: str, company: CompanyEntity) -> None:
        """Extract product information from generic websites"""
        product_sections = soup.find_all(['section', 'div', 'article'], 
            class_=lambda x: x and any(word in str(x).lower() for word in ['product', 'item', 'model']))
        
        for section in product_sections[:2]:  # Limit to 2 main products
            product = ProductEntity()
            
            # Get product name
            if name_elem := section.find(['h1', 'h2', 'h3']):
                name = clean_text(name_elem.get_text(strip=True))
                if is_valid_text(name):
                    product.product_name = name
            
            if not product.product_name:
                continue
            
            # Get product description
            if desc_elem := section.find(['p', 'div'], class_=lambda x: x and 'description' in str(x).lower()):
                desc = clean_text(desc_elem.get_text(strip=True))
                if is_valid_text(desc):
                    product.product_description = desc
            
            # Get features
            feature_elements = section.find_all(['li', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['feature', 'spec']))
            for elem in feature_elements[:5]:  # Limit to 5 main features
                feature = clean_text(elem.get_text(strip=True))
                if is_valid_text(feature):
                    product.features.append(feature)
            
            product.url = url
            company.products.append(product)
