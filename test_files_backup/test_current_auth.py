#!/usr/bin/env python3
"""
現在の認証状態をテスト
"""
import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def test_token(token_file):
    """トークンをテスト"""
    token_path = Path("credentials") / token_file
    
    if not token_path.exists():
        print(f"❌ {token_file}: ファイルが存在しません")
        return False
    
    try:
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        print(f"\n📁 {token_file}:")
        print(f"  有効: {creds.valid}")
        print(f"  期限切れ: {creds.expired if hasattr(creds, 'expired') else 'N/A'}")
        print(f"  リフレッシュトークン: {'あり' if creds.refresh_token else 'なし'}")
        
        # トークンをリフレッシュしてみる
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                print("  🔄 トークンを更新中...")
                creds.refresh(Request())
                # 更新したトークンを保存
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                print("  ✅ トークンを更新しました")
        
        # APIアクセステスト
        try:
            youtube = build('youtube', 'v3', credentials=creds)
            request = youtube.channels().list(
                part="snippet",
                mine=True
            )
            response = request.execute()
            
            if 'items' in response and len(response['items']) > 0:
                channel = response['items'][0]
                print(f"  ✅ チャンネル: {channel['snippet']['title']}")
                return True
            else:
                print("  ❌ チャンネル情報を取得できません")
                return False
                
        except Exception as e:
            print(f"  ❌ APIエラー: {e}")
            return False
            
    except Exception as e:
        print(f"❌ {token_file}: エラー - {e}")
        return False

# テスト実行
print("=" * 60)
print("🔍 認証トークンの状態確認")
print("=" * 60)

# 各トークンをテスト
tokens = [
    "youtube_main_token.pickle",
    "youtube_nb_token.pickle",
    "youtube_sbc_token.pickle",
    "youtube_om_token.pickle",
    "youtube_test_token.pickle"
]

valid_count = 0
for token_file in tokens:
    if test_token(token_file):
        valid_count += 1

print("\n" + "=" * 60)
print(f"📊 結果: {valid_count}/{len(tokens)} のトークンが有効です")

if valid_count == 0:
    print("\n⚠️  有効なトークンがありません")
    print("./run_channel_setup.sh を実行して認証してください")