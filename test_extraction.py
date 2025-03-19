import asyncio
import json
from datetime import datetime
from extraction_service import extraction_service

async def test_extraction():
    # Test URLs - using different types of websites
    test_urls = [
        "https://www.apple.com/iphone-15-pro/",  # Product page
        "https://www.microsoft.com/en-us/microsoft-365",  # Service page
        "https://www.samsung.com/us/smartphones/galaxy-s23-ultra/"  # Product page
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for url_index, url in enumerate(test_urls, 1):
        print(f"\nTesting URL ({url_index}/{len(test_urls)}): {url}")
        print("-" * 80)
        
        result = await extraction_service.process_url(url, f"test-{url.replace('https://', '').replace('/', '-')}")
        
        if result["success"]:
            print("✓ Extraction successful")
            data = result["data"]
            
            # Company Info
            print("\n1. Company Information:")
            print(f"   Name: {data.get('company_name', 'N/A')}")
            print(f"   Type: {data.get('company_type', 'N/A')}")
            if desc := data.get('company_description'):
                print(f"   Description: {desc[:150]}...")
            
            # Contact Info
            print("\n2. Contact Information:")
            if emails := data.get('emails', []):
                print(f"   Emails ({len(emails)}):")
                for email in emails[:5]:
                    print(f"   - {email}")
                if len(emails) > 5:
                    print(f"   ... and {len(emails) - 5} more")
            
            if phones := data.get('phones', []):
                print(f"   Phones ({len(phones)}):")
                for phone in phones[:5]:
                    print(f"   - {phone}")
                if len(phones) > 5:
                    print(f"   ... and {len(phones) - 5} more")
            
            if addrs := data.get('addresses', []):
                print(f"   Addresses ({len(addrs)}):")
                for addr in addrs:
                    print(f"   - {addr}")
            
            # Products Info
            if products := data.get('products', []):
                print(f"\n3. Products Found ({len(products)}):")
                for i, product in enumerate(products, 1):
                    print(f"\n   Product {i}:")
                    print(f"   - Name: {product.get('name', 'N/A')}")
                    if desc := product.get('description'):
                        print(f"   - Description: {desc[:150]}...")
                    if cat := product.get('category'):
                        print(f"   - Category: {cat}")
                    if price := product.get('price'):
                        print(f"   - Price: {price}")
                    if features := product.get('features'):
                        print(f"   - Features ({len(features)}):")
                        for feature in features[:3]:
                            print(f"     * {feature}")
                        if len(features) > 3:
                            print(f"     ... and {len(features) - 3} more")
                    if specs := product.get('specifications'):
                        print(f"   - Specifications:")
                        for key, value in list(specs.items())[:3]:
                            print(f"     * {key}: {value}")
                        if len(specs) > 3:
                            print(f"     ... and {len(specs) - 3} more")
                    if images := product.get('images', []):
                        print(f"   - Images: {len(images)} found")
            
            print(f"\nExtraction Duration: {result['duration_ms']}ms")
            
            # Save detailed results to file
            filename = f'extraction_result_{url_index}_{timestamp}.json'
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Detailed results saved to: {filename}")
            
        else:
            print(f"✗ Extraction failed: {result['error']}")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_extraction())