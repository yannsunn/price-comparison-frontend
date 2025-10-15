import os
import requests
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv(dotenv_path='./price_comparison_system/.env')

def get_lwa_access_token():
    """LWA（Login with Amazon）アクセストークンを取得"""
    url = "https://api.amazon.com/auth/o2/token"
    
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("SP_API_REFRESH_TOKEN"),
        "client_id": os.getenv("SP_API_CLIENT_ID"),
        "client_secret": os.getenv("SP_API_CLIENT_SECRET")
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"[ERROR] LWAトークン取得失敗: {e}")
        return None

if __name__ == "__main__":
    token = get_lwa_access_token()
    if token:
        print(f"[SUCCESS] Access token取得成功: {token[:20]}...")
    else:
        print("[FAILED] トークン取得に失敗しました")

