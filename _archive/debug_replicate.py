#!/usr/bin/env python3
"""
Replicate APIデバッグ
"""
import os
import sys
from pathlib import Path

# 環境変数設定
os.environ['REPLICATE_API_TOKEN'] = 'r8_byPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from video_merger_auto_bg import VideoMergerWithAutoBG

# デバッグ出力を有効化
import logging
logging.basicConfig(level=logging.DEBUG)

print("=" * 60)
print("Replicate APIデバッグ")
print("=" * 60)

# VideoMergerWithAutoBGのインスタンス作成
merger = VideoMergerWithAutoBG()

# APIトークンの確認
print(f"\n1. 環境変数のトークン: {os.environ.get('REPLICATE_API_TOKEN')}")
print(f"2. mergerのトークン: {merger.replicate_api_token}")
print(f"3. トークンの長さ: {len(merger.replicate_api_token) if merger.replicate_api_token else 0}")

# 実際のAPIキーで直接テスト
import requests

token = merger.replicate_api_token
print(f"\n4. 使用するトークン: {token[:10]}...{token[-5:] if token else 'None'}")

# ヘッダー作成
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

print(f"5. ヘッダー: {headers['Authorization'][:20]}...")

# APIテスト
print("\n6. API接続テスト...")
response = requests.get('https://api.replicate.com/v1/account', headers=headers)
print(f"   ステータスコード: {response.status_code}")
print(f"   レスポンス: {response.text[:200]}")