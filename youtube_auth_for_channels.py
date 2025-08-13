#\!/usr/bin/env python3
"""
YouTube チャンネル別認証スクリプト
特定のチャンネルIDを指定して認証を行う
"""

import os
import pickle
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# アップロード権限のみ（シンプル）
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_specific_channel(channel_name, channel_handle):
    """特定チャンネル用の認証"""
    
    print(f"=== {channel_name}チャンネル認証 ===")
    print(f"目標チャンネル: {channel_handle}")
    print()
    
    client_secret = 'credentials/client_secrets.json'
    if not os.path.exists(client_secret):
        print("❌ client_secrets.jsonが見つかりません")
        return False
    
    try:
        # OAuth2認証フロー
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret, SCOPES
        )
        
        print("📌 手順：")
        print("1. ブラウザが開きます")
        print("2. Googleアカウントでログイン")
        print(f"3. 複数のチャンネルがある場合、{channel_handle}を選択")
        print("4. 「許可」をクリック")
        print()
        
        # ローカルサーバーで認証
        creds = flow.run_local_server(
            port=0,
            success_message='認証成功！このタブを閉じてターミナルに戻ってください。'
        )
        
        # トークンを保存
        output_file = f'credentials/token_{channel_name}.pickle'
        with open(output_file, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"✅ トークン保存: {output_file}")
        
        # 認証テスト
        youtube = build('youtube', 'v3', credentials=creds)
        print("✅ YouTube API接続成功")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("YouTube チャンネル別認証セットアップ")
    print("=" * 60)
    print()
    
    channels = {
        'OM': 'https://www.youtube.com/@yuki_om',
        'SBC': 'https://www.youtube.com/@SBC-fp9zq'
    }
    
    print("認証するチャンネルを選択してください：")
    print("1. OM  (@yuki_om)")
    print("2. SBC (@SBC-fp9zq)")
    print("3. 両方")
    print()
    
    choice = input("選択 (1-3): ").strip()
    
    if choice == '1':
        authenticate_specific_channel('OM', channels['OM'])
    elif choice == '2':
        authenticate_specific_channel('SBC', channels['SBC'])
    elif choice == '3':
        authenticate_specific_channel('OM', channels['OM'])
        print()
        authenticate_specific_channel('SBC', channels['SBC'])
    else:
        print("無効な選択です")
        return
    
    print()
    print("=" * 60)
    print("⚠️ 重要な確認事項：")
    print()
    print("認証時に以下を確認してください：")
    print("1. 正しいGoogleアカウントでログインしたか")
    print("2. チャンネル選択画面が出た場合、正しいチャンネルを選んだか")
    print("3. 個人チャンネルではなく、広告用チャンネルを選んだか")
    print("=" * 60)

if __name__ == "__main__":
    main()
