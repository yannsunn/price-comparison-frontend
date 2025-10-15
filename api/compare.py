from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'price_comparison_system'))

# Import backend modules
try:
    from amazon_sp_api_client import search_amazon_products
    from costco_parser import parse_costco_markdown
    from price_comparator import compare_prices
except ImportError as e:
    print(f"Import error: {e}")
    search_amazon_products = None
    parse_costco_markdown = None
    compare_prices = None


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
            
            # TODO: Implement actual scraping and comparison logic
            # For now, return dummy data
            
            response_data = {
                'keyword': keyword,
                'results': [
                    {
                        'costco_name': 'コストコ商品A',
                        'costco_price': 1000,
                        'costco_url': 'https://www.costco.co.jp/product/A',
                        'amazon_name': 'Amazon商品A',
                        'amazon_price': 1500,
                        'amazon_url': 'https://www.amazon.co.jp/dp/A',
                        'price_difference_percent': 50.0
                    },
                    {
                        'costco_name': 'コストコ商品B',
                        'costco_price': 2000,
                        'costco_url': 'https://www.costco.co.jp/product/B',
                        'amazon_name': 'Amazon商品B',
                        'amazon_price': 2600,
                        'amazon_url': 'https://www.amazon.co.jp/dp/B',
                        'price_difference_percent': 30.0
                    }
                ]
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

