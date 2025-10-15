from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import requests
from bs4 import BeautifulSoup

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'price_comparison_system'))

# Import backend modules
try:
    from amazon_sp_api_client import search_amazon_products
    from price_comparator import compare_prices
except ImportError as e:
    print(f"Import error: {e}")
    search_amazon_products = None
    compare_prices = None

# --- Costco Scraper (requests + BeautifulSoup) --- #
def scrape_costco_products(keyword):
    base_url = "https://www.costco.co.jp/search/" # This might need to be adjusted based on actual search URL structure
    search_url = f"{base_url}{keyword}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # Adjust these selectors based on actual Costco website structure
        # This is a generic example and will likely need fine-tuning
        product_cards = soup.select('div.product-card') # Example selector
        
        for card in product_cards:
            name_element = card.select_one('a.product-card-name')
            price_element = card.select_one('span.price')
            link_element = card.select_one('a.product-card-link')
            
            name = name_element.text.strip() if name_element else 'N/A'
            price_text = price_element.text.strip() if price_element else 'N/A'
            url = link_element['href'] if link_element and 'href' in link_element.attrs else 'N/A'
            
            # Clean and convert price to float
            price = None
            if price_text != 'N/A':
                try:
                    price = float(price_text.replace('¥', '').replace(',', '').strip())
                except ValueError:
                    pass
            
            if name != 'N/A' and price is not None and url != 'N/A':
                products.append({
                    'name': name,
                    'price': price,
                    'url': url
                })
        return products
        
    except requests.exceptions.RequestException as e:
        print(f"Costco scraping error: {e}")
        return []


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            keyword = request_data.get('keyword', '')
            
            if not keyword:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Keyword is required'
                }).encode('utf-8'))
                return
            
            # 1. Scrape Costco products
            costco_products = scrape_costco_products(keyword)
            
            # 2. Search Amazon products and compare
            final_results = []
            for c_product in costco_products:
                if search_amazon_products:
                    amazon_results = search_amazon_products(keyword=c_product['name'])
                    
                    if amazon_results and compare_prices:
                        # Assuming amazon_results is a list of dicts with 'name', 'price', 'url'
                        # For simplicity, we'll take the first Amazon result for comparison
                        # In a real scenario, more sophisticated matching would be needed
                        a_product = amazon_results[0]
                        
                        comparison = compare_prices(
                            costco_name=c_product['name'],
                            costco_price=c_product['price'],
                            costco_url=c_product['url'],
                            amazon_name=a_product['name'],
                            amazon_price=a_product['price'],
                            amazon_url=a_product['url']
                        )
                        if comparison:
                            final_results.append(comparison)
            
            response_data = {
                'keyword': keyword,
                'results': final_results
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e)
            }).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

