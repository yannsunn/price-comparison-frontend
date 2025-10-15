
import json
import os
from price_comparison_system.costco_parser import parse_costco_markdown
from price_comparison_system.amazon_sp_api_client import search_amazon_products, get_amazon_competitive_price
from price_comparison_system.price_comparator import compare_prices

def run_price_comparison(costco_search_term):
    print(f"Searching Costco for: {costco_search_term}")
    # 1. Firecrawlでコストコをスクレイピング
    # ここでは、以前スクレイピングした結果のパスを直接使用します。
    # 実際には、ここでFirecrawlのscrapeツールを呼び出す必要があります。
    firecrawl_output_file = '/home/ubuntu/.mcp/tool-results/2025-10-14_14-05-39_firecrawl_firecrawl_scrape.json'
    
    if not os.path.exists(firecrawl_output_file):
        print(f"Error: Firecrawl output file not found at {firecrawl_output_file}")
        return []

    try:
        with open(firecrawl_output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        costco_markdown_content = data.get('markdown', '')
    except Exception as e:
        print(f"Error reading Firecrawl output: {e}")
        return []

    # 2. コストコのMarkdownコンテンツを解析
    costco_products = parse_costco_markdown(costco_markdown_content)
    print(f"Found {len(costco_products)} products on Costco.")

    # 3. Amazonの商品を検索（認証情報がないためダミーデータを使用）
    # 実際には、costco_productsの各商品名を使ってAmazon SP-APIを呼び出す
    amazon_products = []
    # ダミーのAmazon商品データ。実際にはSP-APIから取得する。
    # costco_productsの商品名と一致するものを想定して作成。
    dummy_amazon_products = [
        {"product_name": "カークランドシグネチャートイレットペーパー 30ロール", "price": 2500, "url": "amazon.co.jp/tp"},
        {"product_name": "パステルカラーペーパー 10冊", "price": 1500, "url": "amazon.co.jp/pp"},
        {"product_name": "ハホニコ タオルセット", "price": 4000, "url": "amazon.co.jp/hahonico"},
        {"product_name": "高価格商品X", "price": 9000, "url": "amazon.co.jp/highx"},
        {"product_name": "低価格商品Y", "price": 1000, "url": "amazon.co.jp/lowy"},
        {"product_name": "別の商品", "price": 1000, "url": "amazon.co.jp/other"},
    ]
    amazon_products = dummy_amazon_products # ダミーデータを直接使用
    print(f"Found {len(amazon_products)} dummy products on Amazon.")

    # 4. 価格比較
    comparison_results = compare_prices(costco_products, amazon_products)
    print(f"Found {len(comparison_results)} price differences of 20-25% or more.")

    return comparison_results

if __name__ == '__main__':
    search_term = "ティッシュペーパー"
    results = run_price_comparison(search_term)
    print("\n--- Comparison Results ---")
    print(json.dumps(results, ensure_ascii=False, indent=2))

