# コストコ vs Amazon 価格比較システム

このプロジェクトは、コストコオンラインとAmazon.co.jpの商品価格を比較し、20-25%以上の価格差がある商品を抽出するシステムです。

## 機能

- コストコオンラインの商品検索
- Amazon SP-APIを使用したAmazon商品価格の取得
- 価格差の計算と表示
- レスポンシブなUIデザイン

## 技術スタック

- **フロントエンド**: React, Vite, Tailwind CSS, shadcn/ui
- **バックエンド**: Vercel Serverless Functions
- **API**: Amazon SP-API, Firecrawl (コストコスクレイピング)

## セットアップ

### 1. 依存関係のインストール

```bash
cd price-comparison-frontend
pnpm install
```

### 2. 環境変数の設定

Vercelの環境変数設定で以下の値を設定してください:

- `SP_API_CLIENT_ID`: Amazon SP-APIのクライアントID
- `SP_API_CLIENT_SECRET`: Amazon SP-APIのクライアントシークレット
- `SP_API_REFRESH_TOKEN`: Amazon SP-APIのリフレッシュトークン
- `AWS_ACCESS_KEY_ID`: AWS IAMユーザーのアクセスキーID
- `AWS_SECRET_ACCESS_KEY`: AWS IAMユーザーのシークレットアクセスキー
- `AWS_REGION`: AWSリージョン (例: `us-west-2`)
- `SP_API_MARKETPLACE_ID`: マーケットプレイスID (例: `A1VC38T7YXB528` for Amazon.co.jp)
- `SP_API_ENDPOINT`: SP-APIエンドポイント (例: `https://sellingpartnerapi-fe.amazon.com`)

### 3. ローカル開発サーバーの起動

```bash
pnpm run dev
```

ブラウザで `http://localhost:5173` を開いてアプリケーションにアクセスできます。

## Vercelへのデプロイ

### 方法1: GitHub統合

1. GitHubリポジトリをVercelに接続します
2. Vercelのダッシュボードで環境変数を設定します
3. 自動デプロイが開始されます

### 方法2: Vercel CLIを使用

```bash
vercel deploy
```

## セキュリティ

- Amazon SP-APIの認証情報はすべてサーバーサイド（Vercelのサーバーレス関数）で処理されます
- フロントエンドには認証情報が含まれません
- 環境変数を使用して機密情報を安全に管理します

## ライセンス

MIT

## 作成者

Manus AI

