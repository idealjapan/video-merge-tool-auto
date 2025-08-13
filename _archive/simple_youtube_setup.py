#!/usr/bin/env python3
"""
簡単YouTubeセットアップ - 1つのチャンネルだけ使う
"""

import os
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

print("=" * 60)
print("🎬 かんたんYouTube設定")
print("=" * 60)
print()
print("これから、YouTubeに動画をアップロードできるように")
print("設定します。")
print()
print("ブラウザが開いたら：")
print("1. いつも使っているGoogleアカウントでログイン")
print("2. 「許可」をクリック")
print()
input("準備ができたらEnterキーを押してください...")

# 設定
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
credentials_dir = Path("credentials")
token_file = credentials_dir / "youtube_token.pickle"
client_secrets = credentials_dir / "client_secrets.json"

# 認証
creds = None

# 既存のトークンがあれば削除（新しく作り直す）
if token_file.exists():
    os.remove(token_file)

# 新規認証
print("\n🌐 ブラウザを開いています...")
flow = InstalledAppFlow.from_client_secrets_file(
    str(client_secrets), SCOPES)
creds = flow.run_local_server(port=0)

# トークンを保存
with open(token_file, 'wb') as token:
    pickle.dump(creds, token)

print("\n✅ 認証完了！")

# チャンネル情報を確認
try:
    youtube = build('youtube', 'v3', credentials=creds)
    request = youtube.channels().list(
        part="snippet",
        mine=True
    )
    response = request.execute()
    
    if 'items' in response and len(response['items']) > 0:
        channel = response['items'][0]
        print(f"\n📺 YouTubeチャンネル: {channel['snippet']['title']}")
        print("\n設定完了！これで動画をアップロードできます。")
    else:
        print("\n⚠️ チャンネルが見つかりませんでした")
        print("YouTubeチャンネルを作成してから、もう一度実行してください")
        
except Exception as e:
    print(f"\n❌ エラー: {e}")

print("\n" + "=" * 60)