
import json
import pandas as pd
from costco_scraper import scrape_costco_products
from amazon_api_client import get_amazon_product_info

def match_products(costco_products, amazon_products_data):
    matched_products = []
    # 簡易的な商品名マッチング
    # 実際にはより高度なマッチングロジック（JANコード、部分一致、類似度計算など）が必要
    for c_prod in costco_products:
        c_name = c_prod['product_name'].lower() if c_prod['product_name'] else ''
        for a_prod in amazon_products_data:
            a_name = a_prod['product_name'].lower() if a_prod['product_name'] else ''
            # ここでは単純にキーワードが含まれているかでマッチング
            # 例: Costcoの商品名がAmazonの商品名に含まれている、またはその逆
            if c_name and a_name and (c_name in a_name or a_name in c_name):
                matched_products.append({
                    'costco_name': c_prod['product_name'],
                    'costco_price': c_prod['price'],
                    'costco_url': c_prod['url'],
                    'amazon_name': a_prod['product_name'],
                    'amazon_price': a_prod['price'],
                    'amazon_url': a_prod['url'],
                    'asin': a_prod['asin']
                })
                break # Amazon側で見つかったら次のCostco商品へ
    return matched_products

def calculate_price_difference(matched_products, min_diff_percent=20, max_diff_percent=25):
    results = []
    for item in matched_products:
        if item['costco_price'] is None or item['amazon_price'] is None:
            continue

        costco_price = float(item['costco_price'])
        amazon_price = float(item['amazon_price'])

        if costco_price == 0:
            continue

        price_diff_percent = ((amazon_price - costco_price) / costco_price) * 100

        if min_diff_percent <= price_diff_percent <= max_diff_percent:
            results.append({
                'costco_name': item['costco_name'],
                'costco_price': costco_price,
                'costco_url': item['costco_url'],
                'amazon_name': item['amazon_name'],
                'amazon_price': amazon_price,
                'amazon_url': item['amazon_url'],
                'price_difference_percent': round(price_diff_percent, 2)
            })
    return results

def main():
    search_query = "Apple AirPods Pro" # 検索したい商品クエリ

    print(f"[INFO] コストコオンラインから商品情報を取得中: {search_query}...")
    costco_products = scrape_costco_products(search_query, pages=1)
    print(f"[INFO] コストコオンラインから {len(costco_products)} 件の商品を取得しました。")

    # Amazon PA-APIの認証情報が設定されているか確認
    
    print(f"[INFO] Amazonから商品情報を取得中: {search_query}...")
    # 実際には、コストコの商品名などからAmazonでASINを検索し、そのASINを使って情報を取得する必要があります。
    # ここではデモンストレーションのため、ダミーのASINで取得を試みます。
    # 適切なASINを特定するロジックは別途実装が必要です。
    # 例: コストコの商品名からAmazonで検索し、最も関連性の高いASINを取得する
    # 現状は、Costcoの商品名からAmazonのASINを特定するロジックがないため、
    # ここではAmazonの商品取得はコメントアウトし、手動でASINリストを作成するなどの対応が必要です。
    # または、Amazonの検索APIを利用して商品名からASINを検索する機能を追加する必要があります。
    
    # デモンストレーション用に、Costcoの商品から適当なASINを仮定して取得を試みる
    amazon_products_data = []
    # 例: コストコの商品名からAmazonのASINを検索するロジックをここに実装
    # 例えば、Costcoで取得した商品名を使ってAmazonのSearchItems APIを呼び出し、
    # 関連性の高いASINを取得する。
    # 現状、このスクリプトではその機能は実装されていないため、
    # amazon_api_client.pyのget_amazon_product_info関数を直接呼び出すことはできません。
    # ユーザーが手動でASINリストを提供するか、Amazonの検索機能を実装する必要があります。
    
    # 暫定的に、Amazonの商品データは空として処理を進めます。
    amazon_products = [] # ここにAmazonから取得した商品データが入る想定
    print(f"[INFO] Amazonから {len(amazon_products)} 件の商品を取得しました。(認証情報が設定されている場合のみ)")

    # 商品マッチング
    # 実際には、コストコの商品名からAmazonのASINを検索し、そのASINを使って情報を取得する必要があります。
    # そのため、現状ではマッチングは機能しません。
    # デモンストレーションのため、amazon_productsが空の場合でも処理を進めます。
    matched = match_products(costco_products, amazon_products)
    print(f"[INFO] マッチングされた商品: {len(matched)} 件")

    # 価格差計算とフィルタリング
    filtered_results = calculate_price_difference(matched, min_diff_percent=20, max_diff_percent=25)
    print(f"[INFO] 価格差20-25%の範囲でフィルタリングされた商品: {len(filtered_results)} 件")

    # 結果の出力
    if filtered_results:
        df = pd.DataFrame(filtered_results)
        output_file = "price_difference_results.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"[INFO] 結果を {output_file} に保存しました。")
    else:
        print("[INFO] 指定された価格差の範囲に該当する商品はありませんでした。")

if __name__ == "__main__":
    main()

