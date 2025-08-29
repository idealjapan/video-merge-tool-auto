#!/usr/bin/env python3
"""
YouTube認証トークン管理システム
自動的にトークンをリフレッシュして期限切れを防ぐ
"""

import os
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

class YouTubeAuthManager:
    """YouTube認証の管理クラス"""
    
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.token_file = f'token_{channel_name}.pickle'
        self.client_secrets_file = 'credentials/client_secrets.json'
        self.creds = None
        
    def get_authenticated_service(self):
        """認証済みのYouTubeサービスを取得（自動リフレッシュ機能付き）"""
        
        # 既存のトークンファイルを読み込み
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # トークンが無効か期限切れの場合
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # リフレッシュトークンで自動更新
                print(f"🔄 {self.channel_name}チャンネルのトークンを自動更新中...")
                try:
                    self.creds.refresh(Request())
                    # 更新したトークンを保存
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(self.creds, token)
                    print(f"✅ トークン更新成功！")
                except Exception as e:
                    print(f"❌ トークン更新失敗: {e}")
                    print("新規認証が必要です")
                    return self._new_authentication()
            else:
                # 新規認証が必要
                print(f"⚠️ {self.channel_name}チャンネルの認証が必要です")
                return self._new_authentication()
        
        # YouTubeサービスを構築
        return build('youtube', 'v3', credentials=self.creds)
    
    def _new_authentication(self):
        """新規認証を実行"""
        if not os.path.exists(self.client_secrets_file):
            raise FileNotFoundError(f"認証ファイルが見つかりません: {self.client_secrets_file}")
        
        print(f"📌 ブラウザで{self.channel_name}チャンネルの認証を行ってください...")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, SCOPES
        )
        
        # access_typeをofflineに設定してrefresh_tokenを取得
        self.creds = flow.run_local_server(
            port=0,
            access_type='offline',
            prompt='consent'  # 強制的に同意画面を表示してrefresh_tokenを取得
        )
        
        # トークンを保存
        with open(self.token_file, 'wb') as token:
            pickle.dump(self.creds, token)
        
        print(f"✅ 認証成功！トークンを{self.token_file}に保存しました")
        
        return build('youtube', 'v3', credentials=self.creds)
    
    def check_token_status(self):
        """トークンの状態を確認"""
        if not os.path.exists(self.token_file):
            return {
                'status': 'not_found',
                'message': f'{self.token_file}が存在しません'
            }
        
        with open(self.token_file, 'rb') as token:
            creds = pickle.load(token)
        
        if not creds:
            return {
                'status': 'invalid',
                'message': 'トークンが無効です'
            }
        
        if creds.expired:
            if creds.refresh_token:
                return {
                    'status': 'expired_refreshable',
                    'message': '期限切れですが、自動更新可能です',
                    'expiry': str(creds.expiry) if creds.expiry else 'unknown'
                }
            else:
                return {
                    'status': 'expired_no_refresh',
                    'message': '期限切れで、再認証が必要です',
                    'expiry': str(creds.expiry) if creds.expiry else 'unknown'
                }
        
        if creds.valid:
            return {
                'status': 'valid',
                'message': '有効なトークンです',
                'expiry': str(creds.expiry) if creds.expiry else 'unknown',
                'has_refresh_token': bool(creds.refresh_token)
            }
        
        return {
            'status': 'unknown',
            'message': 'トークンの状態が不明です'
        }

def migrate_existing_tokens():
    """既存のトークンファイルをリフレッシュトークン付きに移行"""
    channels = ['NB', 'OM', 'SBC', 'RL']
    
    print("=== 既存トークンの移行処理 ===\n")
    
    for channel in channels:
        token_file = f'token_{channel}.pickle'
        
        if not os.path.exists(token_file):
            print(f"⏭️ {channel}: トークンファイルが存在しません")
            continue
        
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        if creds and creds.refresh_token:
            print(f"✅ {channel}: リフレッシュトークンあり（移行不要）")
        else:
            print(f"⚠️ {channel}: リフレッシュトークンなし（再認証推奨）")
            print(f"   → python youtube_auth_manager.py --channel {channel} --force")
    
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube認証管理ツール')
    parser.add_argument('--channel', choices=['NB', 'OM', 'SBC', 'RL'], 
                       help='認証するチャンネル')
    parser.add_argument('--check', action='store_true',
                       help='全チャンネルのトークン状態を確認')
    parser.add_argument('--force', action='store_true',
                       help='強制的に再認証')
    parser.add_argument('--migrate', action='store_true',
                       help='既存トークンの移行チェック')
    
    args = parser.parse_args()
    
    if args.migrate:
        migrate_existing_tokens()
    elif args.check:
        print("=== 全チャンネルのトークン状態 ===\n")
        for channel in ['NB', 'OM', 'SBC', 'RL']:
            manager = YouTubeAuthManager(channel)
            status = manager.check_token_status()
            print(f"{channel}チャンネル:")
            print(f"  状態: {status['status']}")
            print(f"  詳細: {status['message']}")
            if 'expiry' in status and status['expiry'] != 'unknown':
                print(f"  期限: {status['expiry']}")
            if 'has_refresh_token' in status:
                print(f"  リフレッシュトークン: {'あり' if status['has_refresh_token'] else 'なし'}")
            print()
    elif args.channel:
        manager = YouTubeAuthManager(args.channel)
        
        if args.force:
            # 強制再認証
            print(f"強制的に{args.channel}チャンネルの再認証を実行します...")
            if os.path.exists(manager.token_file):
                os.remove(manager.token_file)
            manager.get_authenticated_service()
        else:
            # 通常の認証チェック
            status = manager.check_token_status()
            print(f"{args.channel}チャンネルの状態: {status['message']}")
            
            if status['status'] in ['expired_no_refresh', 'not_found', 'invalid']:
                print("新規認証を開始します...")
                manager.get_authenticated_service()
    else:
        parser.print_help()