import json
import os
from dotenv import load_dotenv
import requests
import datetime
import hashlib
import hmac
import urllib.parse

# .envファイルから環境変数を読み込む
# このスクリプトが存在するディレクトリ内の.envファイルを指定
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# --- SP-API認証情報 --- #
LWA_CLIENT_ID = os.getenv("SP_API_CLIENT_ID")
LWA_CLIENT_SECRET = os.getenv("SP_API_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SP_API_REFRESH_TOKEN")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_ROLE_ARN = os.getenv("AWS_ROLE_ARN")

# --- SP-APIエンドポイント・マーケットプレイス設定 --- #
MARKETPLACE_ID = os.getenv("SP_API_MARKETPLACE_ID", "A1VC38T7YXB528")
REGION = os.getenv("AWS_REGION", "us-west-2")
HOST = os.getenv("SP_API_ENDPOINT", "sellingpartnerapi-na.amazon.com").replace("https://", "")

# --- グローバル変数 (LWAトークンキャッシュ用) --- #
_lwa_access_token = None
_lwa_token_expiry = None

def _get_lwa_access_token():
    """LWAアクセストークンを取得または更新する。"""
    global _lwa_access_token, _lwa_token_expiry

    if _lwa_access_token and _lwa_token_expiry and _lwa_token_expiry > datetime.datetime.now():
        return _lwa_access_token

    print("[INFO] LWAアクセストークンを更新しています...")
    token_url = "https://api.amazon.com/auth/o2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": LWA_CLIENT_ID,
        "client_secret": LWA_CLIENT_SECRET
    }

    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        _lwa_access_token = token_data["access_token"]
        expires_in = token_data["expires_in"]
        _lwa_token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=expires_in - 60)
        print("[INFO] LWAアクセストークンの更新に成功しました。")
        return _lwa_access_token
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] LWAアクセストークンの取得に失敗しました: {e}")
        return None

def _sign_request(method, path, query_params, body):
    """AWS SigV4署名を生成してリクエストヘッダーを返す。"""
    service = "execute-api"
    t = datetime.datetime.utcnow()
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    # 1. Canonical Requestの作成
    canonical_uri = urllib.parse.quote(path)
    
    sorted_query = sorted(query_params.items())
    canonical_querystring = "&".join([urllib.parse.quote(k, safe="~") + "=" + urllib.parse.quote(str(v), safe="~") for k, v in sorted_query])

    canonical_headers = f"host:{HOST}\nuser-agent:PriceComparisonSystem/1.0 (Language=Python)\nx-amz-date:{amz_date}\n"
    signed_headers = "host;user-agent;x-amz-date"

    payload_hash = hashlib.sha256(body.encode("utf-8")).hexdigest() if body else hashlib.sha256(b"").hexdigest()

    canonical_request = f'{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}'

    # 2. String to Signの作成
    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f'{date_stamp}/{REGION}/{service}/aws4_request'
    string_to_sign = f'{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'

    # 3. 署名の計算
    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    signing_key = sign(f"AWS4{AWS_SECRET_ACCESS_KEY}".encode("utf-8"), date_stamp)
    signing_key = sign(signing_key, REGION)
    signing_key = sign(signing_key, service)
    signing_key = sign(signing_key, "aws4_request")

    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    # 4. ヘッダーの構築
    authorization_header = f'{algorithm} Credential={AWS_ACCESS_KEY_ID}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'
    
    headers = {
        "host": HOST,
        "user-agent": "PriceComparisonSystem/1.0 (Language=Python)",
        "x-amz-date": amz_date,
        "Authorization": authorization_header
    }
    # ロールARNが設定されている場合のみx-amz-security-tokenヘッダーを追加
    if AWS_ROLE_ARN and AWS_ROLE_ARN != "YOUR_AWS_ROLE_ARN":
        headers["x-amz-security-token"] = AWS_ROLE_ARN

    return headers

def get_amazon_competitive_price(asin):
    """ASINに基づいてAmazonの競合価格情報を取得する。"""
    if any(val is None or "dummy" in str(val) for val in [LWA_CLIENT_ID, LWA_CLIENT_SECRET, REFRESH_TOKEN, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
        print("[ERROR] Amazon SP-APIの認証情報が不足しています。環境変数を設定してください。")
        return None

    access_token = _get_lwa_access_token()
    if not access_token:
        return None

    path = "/pricing/v0/competitivePrice"
    query_params = {
        "MarketplaceId": MARKETPLACE_ID,
        "Asins": asin
    }

    # SigV4署名付きヘッダーを取得
    signed_headers = _sign_request("GET", path, query_params, "")
    # LWAトークンをヘッダーに追加
    signed_headers["x-amz-access-token"] = access_token
    signed_headers["Content-Type"] = "application/json"

    api_url = f"https://{HOST}{path}"

    try:
        response = requests.get(api_url, headers=signed_headers, params=query_params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("payload") and len(data["payload"]) > 0:
            item_data = data["payload"][0]
            if item_data.get("Product", {}).get("CompetitivePricing", {}).get("CompetitivePrices"):
                competitive_price = item_data["Product"]["CompetitivePricing"]["CompetitivePrices"][0]["Price"]["LandedPrice"]["Amount"]
                product_title = f"Amazon Product (ASIN: {asin})"
                product_url = f"https://www.amazon.co.jp/dp/{asin}"

                return {
                    "source": "Amazon",
                    "product_name": product_title,
                    "price": competitive_price,
                    "asin": asin,
                    "url": product_url
                }
            else:
                print(f"[WARNING] Amazonで商品ASIN: {asin} の価格情報が見つかりませんでした。")
                return None
        else:
            print(f"[WARNING] Amazonで商品ASIN: {asin} が見つかりませんでした。")
            return None

    except requests.exceptions.HTTPError as e:
        print(f'[ERROR] Amazon SP-APIからの商品情報取得中にHTTPエラーが発生しました: {e.response.status_code} - {e.response.text}')
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Amazon SP-APIからの商品情報取得中にリクエストエラーが発生しました: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 予期せぬエラーが発生しました: {e}")
        return None

def search_amazon_products(keywords, page_size=10):
    """Catalog Items APIを使用してキーワードで商品を検索する。"""
    if any(val is None or "dummy" in str(val) for val in [LWA_CLIENT_ID, LWA_CLIENT_SECRET, REFRESH_TOKEN, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
        print("[ERROR] Amazon SP-APIの認証情報が不足しています。環境変数を設定してください。")
        return None

    access_token = _get_lwa_access_token()
    if not access_token:
        return None

    path = "/catalog/2020-12-01/items"
    query_params = {
        "keywords": keywords,
        "marketplaceIds": MARKETPLACE_ID,
        "includedData": "summaries,attributes",
        "pageSize": page_size
    }

    # SigV4署名付きヘッダーを取得
    signed_headers = _sign_request("GET", path, query_params, "")
    # LWAトークンをヘッダーに追加
    signed_headers["x-amz-access-token"] = access_token
    signed_headers["Content-Type"] = "application/json"

    api_url = f"https://{HOST}{path}"

    try:
        response = requests.get(api_url, headers=signed_headers, params=query_params)
        response.raise_for_status()
        data = response.json()

        products = []
        if "items" in data:
            for item in data["items"]:
                asin = item.get("asin")
                summary = item.get("summaries", [{}])[0]
                product_info = {
                    "source": "Amazon",
                    "asin": asin,
                    "product_name": summary.get("itemName"),
                    "url": f"https://www.amazon.co.jp/dp/{asin}",
                    "price": None  # Catalog Items APIは価格を返さない
                }
                products.append(product_info)
        return products

    except requests.exceptions.HTTPError as e:
        print(f'[ERROR] Amazon SP-API商品検索中にHTTPエラー: {e.response.status_code} - {e.response.text}')
        return None
    except Exception as e:
        print(f"[ERROR] 予期せぬエラー: {e}")
        return None

if __name__ == "__main__":
    print("--- Amazon SP-API Clientテスト ---")
    
    # 競合価格取得のテスト
    example_asin = "B07XQ5G18G" # 例: Apple AirPods Pro (ダミー)
    print(f"\nASIN \'{example_asin}\' の競合価格情報を取得します...")
    amazon_product = get_amazon_competitive_price(example_asin)
    if amazon_product:
        print("\n--- 競合価格情報 ---")
        print(json.dumps(amazon_product, indent=2, ensure_ascii=False))
    else:
        print("\n競合価格情報の取得に失敗しました。認証情報やリクエスト内容を確認してください。")

    # キーワード検索のテスト
    example_keywords = "ティッシュペーパー"
    print(f"\nキーワード \'{example_keywords}\' で商品を検索します...")
    search_results = search_amazon_products(example_keywords)
    
    if search_results is not None:
        if search_results:
            print("\n--- 商品検索結果 ---")
            for product in search_results:
                print(json.dumps(product, indent=2, ensure_ascii=False))
        else:
            print("検索結果がありませんでした。")
    else:
        print("\n商品検索に失敗しました。認証情報やリクエスト内容を確認してください。")

