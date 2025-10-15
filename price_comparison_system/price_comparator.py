
import json

def compare_prices(costco_products, amazon_products):
    comparison_results = []

    for costco_product in costco_products:
        costco_name = costco_product.get("product_name")
        costco_price = costco_product.get("price")
        costco_url = costco_product.get("url")

        if not costco_name or costco_price is None:
            continue

        # Amazonの商品を検索（ここではモックデータを使用）
        # 実際にはamazon_sp_api_client.pyのsearch_amazon_productsを呼び出す
        # 商品名の部分一致でマッチングを試みる
        matching_amazon_products = [
            p for p in amazon_products 
            if costco_name.lower() in p.get("product_name", "").lower()
        ]

        for amazon_product in matching_amazon_products:
            amazon_name = amazon_product.get("product_name")
            amazon_price = amazon_product.get("price")
            amazon_url = amazon_product.get("url")

            if amazon_price is None or amazon_price == 0:
                continue

            # 価格差の計算
            # (コストコ価格 - Amazon価格) / Amazon価格 * 100
            price_difference = costco_price - amazon_price
            percentage_difference = (price_difference / amazon_price) * 100

            # 20%以上高いか、25%以上安い場合を抽出
            # percentage_difference >= 20: コストコがAmazonより20%以上高い
            # percentage_difference <= -25: コストコがAmazonより25%以上安い
            if percentage_difference >= 20 or percentage_difference <= -25:
                comparison_results.append({
                    "costco_product_name": costco_name,
                    "costco_price": costco_price,
                    "costco_url": costco_url,
                    "amazon_product_name": amazon_name,
                    "amazon_price": amazon_price,
                    "amazon_url": amazon_url,
                    "price_difference": price_difference,
                    "percentage_difference": round(percentage_difference, 2)
                })
    return comparison_results

if __name__ == '__main__':
    # テスト用のダミーデータ
    dummy_costco_products = [
        {"product_name": "カークランドシグネチャートイレットペーパー ２枚重ね 30ロール", "price": 3198, "url": "costco.jp/tp"},
        {"product_name": "パステルカラーペーパー 80枚 x 10冊", "price": 1298, "url": "costco.jp/pp"},
        {"product_name": "ハホニコ タオル1枚, ターバン1枚, カラミーブラシ セット", "price": 3180, "url": "costco.jp/hahonico"},
        {"product_name": "高価格商品X", "price": 12000, "url": "costco.jp/highx"}, # Amazonより20%以上高いケース
        {"product_name": "低価格商品Y", "price": 750, "url": "costco.jp/lowy"}, # Amazonより25%以上安いケース
    ]

    dummy_amazon_products = [
        {"product_name": "カークランドシグネチャートイレットペーパー 30ロール", "price": 2500, "url": "amazon.co.jp/tp"},
        {"product_name": "パステルカラーペーパー 10冊", "price": 1500, "url": "amazon.co.jp/pp"},
        {"product_name": "ハホニコ タオルセット", "price": 4000, "url": "amazon.co.jp/hahonico"},
        {"product_name": "高価格商品X", "price": 9000, "url": "amazon.co.jp/highx"}, # Costco: 12000, Amazon: 9000 -> (12000-9000)/9000 * 100 = 33.33% (>=20%)
        {"product_name": "低価格商品Y", "price": 1000, "url": "amazon.co.jp/lowy"}, # Costco: 750, Amazon: 1000 -> (750-1000)/1000 * 100 = -25% (<= -25%)
        {"product_name": "別の商品", "price": 1000, "url": "amazon.co.jp/other"},
    ]

    results = compare_prices(dummy_costco_products, dummy_amazon_products)
    print(json.dumps(results, ensure_ascii=False, indent=2))

