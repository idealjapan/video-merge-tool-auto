#!/usr/bin/env python3
"""
Google Ads API用のリフレッシュトークンを取得するスクリプト
"""
import json
from google_auth_oauthlib.flow import Flow

# デスクトップアプリのクライアント設定
CLIENT_CONFIG = {
    "installed": {
        "client_id": "YOUR_CLIENT_ID_HERE",  # ← ここに新しいClient IDを入力
        "client_secret": "YOUR_CLIENT_SECRET_HERE",  # ← ここに新しいSecretを入力
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

# Google Ads APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/adwords']

def get_refresh_token():
    """リフレッシュトークンを取得"""
    # OAuth フローを作成
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri='http://localhost:8080'
    )
    
    # 認証URLを生成
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    
    print('=== Google Ads API 認証 ===\n')
    print('1. 以下のURLをブラウザで開いてください:')
    print(auth_url)
    print('\n2. Googleアカウントでログインして許可してください')
    print('3. リダイレクト後のURLをコピーしてください')
    print('   (http://localhost:8080/?code=... のような形式)\n')
    
    # リダイレクトURLを入力
    redirect_url = input('リダイレクトURL全体を貼り付けてください: ')
    
    # トークンを取得
    flow.fetch_token(authorization_response=redirect_url)
    
    # リフレッシュトークンを表示
    print('\n=== 取得成功！ ===')
    print(f'Refresh Token: {flow.credentials.refresh_token}')
    print('\nこのリフレッシュトークンをGASのプロパティに設定してください')
    
    # 設定用のGASコードも生成
    print('\n=== GASで実行するコード ===')
    print(f"""
function setNewRefreshToken() {{
  PropertiesService.getScriptProperties().setProperty(
    'OAUTH_REFRESH_TOKEN', 
    '{flow.credentials.refresh_token}'
  );
  console.log('✅ リフレッシュトークンを更新しました');
}}
""")

if __name__ == '__main__':
    get_refresh_token()