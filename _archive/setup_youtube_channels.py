#!/usr/bin/env python3
"""
YouTube各チャンネルの認証設定
OM, SBC, RL用のトークンを生成
"""

import os
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# スコープ（YouTubeアップロードに必要な権限）
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_channel(channel_name):
    """指定チャンネルの認証を実行"""
    
    project_root = Path(__file__).parent
    credentials_dir = project_root / 'credentials'
    
    # client_secrets.jsonファイルの確認
    client_secret_file = credentials_dir / 'client_secrets.json'
    if not client_secret_file.exists():
        print(f"❌ client_secrets.jsonが見つかりません: {client_secret_file}")
        print("\nセットアップ手順:")
        print("1. Google Cloud Consoleで新しいOAuth 2.0クライアントIDを作成")
        print("2. クライアントシークレットJSONをダウンロード")
        print("3. credentials/client_secrets.json として保存")
        return False
    
    token_file = credentials_dir / f'token_{channel_name}.pickle'
    
    creds = None
    
    # 既存のトークンがあれば読み込み
    if token_file.exists():
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # トークンが無効または存在しない場合は新規認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print(f"\n🔐 {channel_name}チャンネルの認証を開始...")
            print("ブラウザが開きます。適切なYouTubeチャンネルのアカウントでログインしてください。")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret_file), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # トークンを保存
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"✅ {channel_name}チャンネルの認証完了: {token_file}")
        return True
    
    print(f"✅ {channel_name}チャンネルは既に認証済み: {token_file}")
    return True

def main():
    """メイン処理"""
    print("=" * 80)
    print("YouTube各チャンネル認証セットアップ")
    print("=" * 80)
    
    channels = ['OM', 'SBC', 'RL']
    
    print("\n設定するチャンネル:")
    for ch in channels:
        print(f"  - {ch}")
    
    print("\n注意事項:")
    print("- 各チャンネルごとに適切なGoogleアカウントでログインしてください")
    print("- NBチャンネルは既に設定済みです")
    
    input("\nEnterキーを押して続行...")
    
    for channel in channels:
        print(f"\n{'=' * 40}")
        print(f"{channel}チャンネルの設定")
        print('=' * 40)
        
        success = authenticate_channel(channel)
        if not success:
            print(f"⚠️ {channel}チャンネルの設定をスキップしました")
            continue
        
        if channel != channels[-1]:
            input("\n次のチャンネルに進むにはEnterキーを押してください...")
    
    print("\n" + "=" * 80)
    print("✅ セットアップ完了！")
    
    # 設定されたトークンを確認
    credentials_dir = Path(__file__).parent / 'credentials'
    tokens = list(credentials_dir.glob('token_*.pickle'))
    
    print("\n利用可能なチャンネル:")
    for token in tokens:
        channel_name = token.stem.replace('token_', '')
        print(f"  - {channel_name}")
    
    print("\n各案件で自動的に適切なチャンネルが使用されます:")
    print("  - NB案件 → NBチャンネル")
    print("  - OM案件 → OMチャンネル")
    print("  - SBC案件 → SBCチャンネル")
    print("  - RL案件 → RLチャンネル")
    print("=" * 80)

if __name__ == "__main__":
    main()