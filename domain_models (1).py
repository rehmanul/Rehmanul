from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class ProductEntity:
    """Product information"""
    product_name: str = ""
    product_description: str = ""
    main_category: str = ""
    sub_category: str = ""
    price: float = 0.0
    currency: str = "USD"
    features: List[str] = field(default_factory=list)
    specifications: Dict[str, str] = field(default_factory=dict)
    images: List[str] = field(default_factory=list)
    url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.product_name,
            "description": self.product_description,
            "category": self.main_category,
            "sub_category": self.sub_category,
            "price": f"{self.price} {self.currency}" if self.price > 0 else "N/A",
            "features": ", ".join(self.features),
            "specifications": ", ".join(f"{k}: {v}" for k, v in self.specifications.items()),
            "url": self.url
        }

@dataclass
class CompanyEntity:
    """Company information"""
    url: str = ""
    company_name: str = ""
    company_type: str = ""
    company_description: str = ""
    products: List[ProductEntity] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    extraction_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "url": self.url,
            "company_name": self.company_name,
            "company_type": self.company_type,
            "company_description": self.company_description,
            "extraction_date": self.extraction_date,
            "emails": self.emails,
            "phones": self.phones,
            "addresses": self.addresses,
            "products": [p.to_dict() for p in self.products]
        }

    def to_sheet_row(self) -> List[str]:
        """Convert to a row for Google Sheets"""
        # Get the primary product if available
        primary_product = self.products[0] if self.products else None
        
        return [
            self.url,
            self.company_name,
            self.company_type,
            self.company_description[:500] if self.company_description else "",
            ", ".join(self.emails),
            ", ".join(self.phones),
            "; ".join(self.addresses),
            primary_product.product_name if primary_product else "",
            primary_product.main_category if primary_product else "",
            str(primary_product.price) + " " + primary_product.currency if primary_product and primary_product.price > 0 else "",
            primary_product.product_description[:500] if primary_product and primary_product.product_description else "",
            ", ".join(p.product_name for p in self.products[1:])[:500] if len(self.products) > 1 else ""
        ]

class ExtractionState:
    """Tracks extraction progress"""
    def __init__(self, extraction_id: str, url: str):
        self.extraction_id = extraction_id
        self.url = url
        self.progress = 0
        self.status = "Starting"
        self.start_time = datetime.now()
    
    def update_progress(self, progress: int, status: str):
        self.progress = progress
        self.status = status
    
    @staticmethod
    def is_stopped(extraction_id: str) -> bool:
        return False
    
    @staticmethod
    def is_paused(extraction_id: str) -> bool:
        return False

class GlobalStats:
    """Global statistics tracker"""
    def __init__(self):
        self.processed = 0
        self.success = 0
        self.fail = 0
        self.remaining = 0
        self.api_calls = {
            "azure": {"success": 0, "fail": 0},
            "knowledge_graph": {"success": 0, "fail": 0}
        }

# Create global stats instance
global_stats = GlobalStats()
