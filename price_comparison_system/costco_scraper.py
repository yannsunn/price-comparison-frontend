
import requests
import time
import json

def scrape_costco_products(query, pages=1, items_per_page=24, delay=1.5):
    all_items = []
    API_URL = "https://search.costco.com/api/apps/www_costco_com/query/www_costco_com_navigation"
    headers = {
        "Host": "search.costco.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.costco.com/",
        "Content-Type": "application/json",
        "Origin": "https://www.costco.com",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }

    for page in range(pages):
        start = page * items_per_page
        params = {
            "expoption": "def",
            "q": query,
            "locale": "en-US",
            "start": start,
            "expand": "false",
            "userLocation": "WA",
            "loc": "*",
            "whloc": "1-wh",
            "rows": items_per_page,
            "chdcategory": "true",
            "chdheader": "true"
        }

        print(f"[INFO] Scraping Costco page {page + 1} (start={start})...")

        try:
            response = requests.get(API_URL, headers=headers, params=params)
            if response.status_code != 200:
                print(f"[ERROR] Costco page {page + 1} failed with status {response.status_code}")
                break

            data = response.json()
            products = data.get("response", {}).get("docs", [])

            if not products:
                print(f"[WARNING] No products found on Costco page {page + 1}")
                break

            for product in products:
                all_items.append({
                    "source": "Costco Online",
                    "product_name": product.get("item_product_name"),
                    "price": product.get("item_location_pricing_salePrice") or product.get("item_location_pricing_listPrice"),
                    "item_number": product.get("item_number"),
                    "member_only": product.get("item_member_only"),
                    "stock_status": product.get("item_location_stockStatus"),
                    "url": f"https://www.costco.com/product/{product.get('item_number')}" # Construct URL if not directly available
                })
            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            break

    return all_items

if __name__ == "__main__":
    # Example usage
    search_query = "Apple AirPods Pro"
    costco_products = scrape_costco_products(search_query, pages=1)
    print(json.dumps(costco_products, indent=2, ensure_ascii=False))

    with open("costco_products.json", "w", encoding="utf-8") as f:
        json.dump(costco_products, f, indent=2, ensure_ascii=False)
    print(f"Costco products saved to costco_products.json")

