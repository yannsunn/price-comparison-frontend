import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Search, TrendingDown, TrendingUp, ExternalLink } from 'lucide-react'
import './App.css'

function App() {
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])
  const [error, setError] = useState(null)

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setError('検索キーワードを入力してください')
      return
    }

    setLoading(true)
    setError(null)
    setResults([])

    try {
      // APIエンドポイントを呼び出す（Vercelのサーバーレス関数）
      const response = await fetch('/api/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ searchTerm }),
      })

      if (!response.ok) {
        throw new Error('価格比較の取得に失敗しました')
      }

      const data = await response.json()
      setResults(data.results || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-6xl mx-auto">
        {/* ヘッダー */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 dark:text-white mb-2">
            コストコ vs Amazon 価格比較
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            20-25%以上の価格差がある商品を見つけましょう
          </p>
        </div>

        {/* 検索バー */}
        <Card className="mb-8 shadow-lg">
          <CardHeader>
            <CardTitle>商品を検索</CardTitle>
            <CardDescription>
              コストコオンラインで検索したい商品のキーワードを入力してください
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                type="text"
                placeholder="例: ティッシュペーパー"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="flex-1"
              />
              <Button onClick={handleSearch} disabled={loading}>
                <Search className="mr-2 h-4 w-4" />
                {loading ? '検索中...' : '検索'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* エラーメッセージ */}
        {error && (
          <Card className="mb-8 border-red-500 bg-red-50 dark:bg-red-900/20">
            <CardContent className="pt-6">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* 検索結果 */}
        {results.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">
              検索結果 ({results.length}件)
            </h2>
            {results.map((result, index) => (
              <Card key={index} className="shadow-md hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-lg">{result.costco_product_name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* コストコ情報 */}
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <h3 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">
                        コストコオンライン
                      </h3>
                      <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                        ¥{result.costco_price.toLocaleString()}
                      </p>
                      <a
                        href={result.costco_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                      >
                        商品ページを開く
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>

                    {/* Amazon情報 */}
                    <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                      <h3 className="font-semibold text-orange-700 dark:text-orange-300 mb-2">
                        Amazon.co.jp
                      </h3>
                      <p className="text-2xl font-bold text-orange-600 dark:text-orange-400 mb-2">
                        ¥{result.amazon_price.toLocaleString()}
                      </p>
                      <a
                        href={result.amazon_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-orange-600 dark:text-orange-400 hover:underline flex items-center gap-1"
                      >
                        商品ページを開く
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                  </div>

                  {/* 価格差 */}
                  <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">価格差:</span>
                      <div className="flex items-center gap-2">
                        {result.percentage_difference > 0 ? (
                          <TrendingUp className="h-5 w-5 text-red-500" />
                        ) : (
                          <TrendingDown className="h-5 w-5 text-green-500" />
                        )}
                        <span
                          className={`text-xl font-bold ${
                            result.percentage_difference > 0
                              ? 'text-red-600 dark:text-red-400'
                              : 'text-green-600 dark:text-green-400'
                          }`}
                        >
                          {result.percentage_difference > 0 ? '+' : ''}
                          {result.percentage_difference}%
                        </span>
                        <span className="text-gray-600 dark:text-gray-400">
                          (¥{Math.abs(result.price_difference).toLocaleString()})
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* 結果が0件の場合 */}
        {!loading && results.length === 0 && searchTerm && !error && (
          <Card className="text-center py-12">
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400">
                20-25%以上の価格差がある商品は見つかりませんでした
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default App

