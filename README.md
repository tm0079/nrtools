# Newrelic tools

## 初期設定

API_Keyを記載した`config.json`を事前に用意します

```bash
# config.json を作成して、APIキーとアカウントIDを設定
cat > config.json << EOF
{
  "api_key": "YOUR_NEW_RELIC_API_KEY_HERE",
  "account_id": 3186371
}
EOF
```

## newrelic_chart.py

指定したnrqlのグラフ画像を取得します

使用例
```bash
# 基本的な使用方法
uv run python3 newrelic_chart.py "SELECT average(duration) FROM Transaction WHERE appName IN ('todo-service', 'user-service') FACET appName TIMESERIES" chart.png

# 別の設定ファイルを使用する場合
uv run python3 newrelic_chart.py "SELECT count(*) FROM Transaction TIMESERIES" output.png my_config.json
```

主な機能:

1. APIキーをconfig.jsonから読み込み
2. NRQLクエリを引数として指定可能(エンコード前の生の文字列)
3. 出力ファイル名を第2引数で指定
4. エラーハンドリング付き
5. クエリ結果とチャートURLの表示
6. 画像の自動ダウンロード

