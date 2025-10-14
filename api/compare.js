// Vercel Serverless Function for Price Comparison
// This function handles the price comparison logic securely on the backend

export default async function handler(req, res) {
  // CORS設定
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { searchTerm } = req.body;

    if (!searchTerm) {
      return res.status(400).json({ error: 'Search term is required' });
    }

    // 環境変数から認証情報を取得
    const SP_API_CLIENT_ID = process.env.SP_API_CLIENT_ID;
    const SP_API_CLIENT_SECRET = process.env.SP_API_CLIENT_SECRET;
    const SP_API_REFRESH_TOKEN = process.env.SP_API_REFRESH_TOKEN;
    const AWS_ACCESS_KEY_ID = process.env.AWS_ACCESS_KEY_ID;
    const AWS_SECRET_ACCESS_KEY = process.env.AWS_SECRET_ACCESS_KEY;
    const AWS_REGION = process.env.AWS_REGION || 'us-west-2';
    const SP_API_MARKETPLACE_ID = process.env.SP_API_MARKETPLACE_ID || 'A1VC38T7YXB528';
    const SP_API_ENDPOINT = process.env.SP_API_ENDPOINT || 'https://sellingpartnerapi-fe.amazon.com';

    // 認証情報の検証
    if (!SP_API_CLIENT_ID || !SP_API_CLIENT_SECRET || !SP_API_REFRESH_TOKEN || !AWS_ACCESS_KEY_ID || !AWS_SECRET_ACCESS_KEY) {
      console.error('Missing required environment variables');
      return res.status(500).json({ 
        error: 'Server configuration error. Please contact the administrator.',
        results: []
      });
    }

    // TODO: ここで実際のコストコスクレイピングとAmazon SP-API呼び出しを実装
    // 現在はダミーデータを返す
    const dummyResults = [
      {
        costco_product_name: 'カークランドシグネチャートイレットペーパー ２枚重ね 30ロール',
        costco_price: 3198,
        costco_url: 'https://www.costco.co.jp/Subscription/Kirkland-Signature-Bath-Tissue-30-Rolls/p/1713045',
        amazon_product_name: 'カークランドシグネチャートイレットペーパー 30ロール',
        amazon_price: 2500,
        amazon_url: 'https://amazon.co.jp/tp',
        price_difference: 698,
        percentage_difference: 27.92
      },
      {
        costco_product_name: 'ハホニコ タオル1枚, ターバン1枚, カラミーブラシ セット',
        costco_price: 3180,
        costco_url: 'https://www.costco.co.jp/c/HAHONICO-Towel-x-1-Turban-x-1-Brush-Set/p/61476',
        amazon_product_name: 'ハホニコ タオルセット',
        amazon_price: 4000,
        amazon_url: 'https://amazon.co.jp/hahonico',
        price_difference: -820,
        percentage_difference: -20.5
      }
    ];

    return res.status(200).json({ 
      results: dummyResults,
      message: 'This is a demo response. Actual implementation requires valid API credentials.'
    });

  } catch (error) {
    console.error('Error in price comparison:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      results: []
    });
  }
}

