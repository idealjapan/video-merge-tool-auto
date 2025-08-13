#!/usr/bin/env python3
"""
NBチャンネルの認証を実行
"""

import os
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# YouTube APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_nb():
    """NBチャンネルの認証"""
    print("=" * 60)
    print("📺 NBチャンネル YouTube認証")
    print("=" * 60)
    
    # パス設定
    project_root = Path(__file__).parent
    credentials_dir = project_root / 'credentials'
    credentials_dir.mkdir(exist_ok=True)
    
    client_secrets_file = credentials_dir / 'client_secrets.json'
    token_file = credentials_dir / 'token_NB.pickle'
    
    # client_secrets.jsonの確認
    if not client_secrets_file.exists():
        print("❌ client_secrets.jsonが見つかりません")
        print(f"   場所: {client_secrets_file}")
        return False
    
    creds = None
    
    # 既存トークンの確認
    if token_file.exists():
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
            print("✅ 既存のトークンを読み込みました")
    
    # トークンの更新または新規作成
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 トークンを更新中...")
            creds.refresh(Request())
        else:
            print("\n🌐 ブラウザが開きます...")
            print("NBチャンネルのアカウントでログインしてください")
            print("⚠️ 注意: NBチャンネルの管理者/所有者アカウントが必要です\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secrets_file), SCOPES)
            creds = flow.run_local_server(port=0)  # 空いているポートを自動選択
            print("✅ 認証成功！")
        
        # トークンを保存
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
            print(f"💾 トークンを保存: {token_file}")
    
    print("\n✨ NBチャンネルの認証完了！")
    print("これでYouTubeアップロードが可能です")
    
    return True

if __name__ == "__main__":
    success = authenticate_nb()
    if not success:
        print("\n認証に失敗しました")
        exit(1)