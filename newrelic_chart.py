#!/usr/bin/env python3
"""
New Relic NerdGraph API を使用してNRQLクエリからチャート画像を取得するスクリプト
"""

import sys
import json
import requests
from pathlib import Path


def load_api_key(config_file='config.json'):
    """
    設定ファイルからAPIキーを読み込む
    
    Args:
        config_file: 設定ファイルのパス
        
    Returns:
        str: APIキー
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config['api_key']
    except FileNotFoundError:
        print(f"エラー: 設定ファイル '{config_file}' が見つかりません")
        print("config.json ファイルを作成してください:")
        print('{"api_key": "YOUR_API_KEY_HERE", "account_id": YOUR_ACCOUNT_ID}')
        sys.exit(1)
    except KeyError:
        print("エラー: 設定ファイルに 'api_key' が含まれていません")
        sys.exit(1)


def load_account_id(config_file='config.json'):
    """
    設定ファイルからアカウントIDを読み込む
    
    Args:
        config_file: 設定ファイルのパス
        
    Returns:
        int: アカウントID
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config['account_id']
    except KeyError:
        print("エラー: 設定ファイルに 'account_id' が含まれていません")
        sys.exit(1)


def get_chart_from_nrql(nrql_query, api_key, account_id, 
                       chart_type='LINE', format='PNG', 
                       width=400, height=200):
    """
    NRQLクエリを実行してチャート画像のURLを取得する
    
    Args:
        nrql_query: NRQLクエリ文字列
        api_key: New Relic APIキー
        account_id: New RelicアカウントID
        chart_type: チャートタイプ (LINE, BAR, PIE など)
        format: 画像フォーマット (PNG, PDF)
        width: 画像の幅
        height: 画像の高さ
        
    Returns:
        tuple: (結果データ, チャート画像URL)
    """
    url = 'https://api.newrelic.com/graphql'
    
    # GraphQLクエリを構築
    graphql_query = """
    {
      actor {
        account(id: %d) {
          id
          nrql(
            query: "%s"
          ) {
            results
            staticChartUrl(chartType: %s, format: %s, width: %d, height: %d)
          }
        }
      }
    }
    """ % (account_id, nrql_query.replace('"', '\\"'), chart_type, format, width, height)
    
    headers = {
        'Content-Type': 'application/json',
        'API-Key': api_key
    }
    
    payload = {
        'query': graphql_query,
        'variables': ''
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # エラーチェック
        if 'errors' in data:
            print("GraphQL エラー:")
            for error in data['errors']:
                print(f"  - {error['message']}")
            return None, None
        
        # データ取得
        nrql_data = data['data']['actor']['account']['nrql']
        results = nrql_data['results']
        chart_url = nrql_data['staticChartUrl']
        
        return results, chart_url
        
    except requests.exceptions.RequestException as e:
        print(f"API リクエストエラー: {e}")
        return None, None


def download_chart_image(chart_url, output_filename):
    """
    チャート画像をダウンロードする
    
    Args:
        chart_url: チャート画像のURL
        output_filename: 保存先ファイル名
        
    Returns:
        bool: 成功した場合True
    """
    try:
        response = requests.get(chart_url)
        response.raise_for_status()
        
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"チャート画像を保存しました: {output_filename}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"画像ダウンロードエラー: {e}")
        return False


def main():
    """
    メイン処理
    """
    # 引数チェック
    if len(sys.argv) < 3:
        print("使用方法:")
        print(f"  {sys.argv[0]} <NRQLクエリ> <出力ファイル名> [設定ファイル]")
        print()
        print("例:")
        print(f"  {sys.argv[0]} \"SELECT average(duration) FROM Transaction WHERE appName IN ('todo-service', 'user-service') FACET appName TIMESERIES\" chart.png")
        print()
        print("設定ファイル (config.json) の形式:")
        print('  {"api_key": "YOUR_API_KEY", "account_id": YOUR_ACCOUNT_ID}')
        sys.exit(1)
    
    nrql_query = sys.argv[1]
    output_filename = sys.argv[2]
    config_file = sys.argv[3] if len(sys.argv) > 3 else 'config.json'
    
    # 設定ファイルから読み込み
    api_key = load_api_key(config_file)
    account_id = load_account_id(config_file)
    
    print(f"NRQLクエリを実行中...")
    print(f"クエリ: {nrql_query}")
    print()
    
    # チャート画像URLを取得
    results, chart_url = get_chart_from_nrql(nrql_query, api_key, account_id)
    
    if chart_url:
        print(f"チャートURL: {chart_url}")
        print()
        
        # クエリ結果を表示
        if results:
            print("クエリ結果:")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            print()
        
        # 画像をダウンロード
        download_chart_image(chart_url, output_filename)
    else:
        print("チャート画像の取得に失敗しました")
        sys.exit(1)


if __name__ == '__main__':
    main()