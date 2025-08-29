#!/usr/bin/env python3
"""
トークン健全性チェックスクリプト
GitHub Actionsで定期的に実行して、トークンの状態を監視
"""

import os
import pickle
import sys
from datetime import datetime, timedelta
from pathlib import Path
from youtube_auth_manager import YouTubeAuthManager

def check_all_tokens():
    """全チャンネルのトークン状態を確認"""
    
    channels = ['NB', 'OM', 'SBC', 'RL']
    all_healthy = True
    warning_messages = []
    
    print("=== トークン健全性チェック ===")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for channel in channels:
        token_file = f'token_{channel}.pickle'
        
        if not os.path.exists(token_file):
            print(f"⏭️ {channel}: トークンファイルなし")
            continue
        
        try:
            with open(token_file, 'rb') as f:
                creds = pickle.load(f)
            
            # トークンの状態を確認
            manager = YouTubeAuthManager(channel)
            status = manager.check_token_status()
            
            # リフレッシュトークンの有無を確認
            if not creds.refresh_token:
                warning_messages.append(f"{channel}: リフレッシュトークンがありません！再認証が必要です。")
                all_healthy = False
                print(f"⚠️ {channel}: リフレッシュトークンなし")
            else:
                print(f"✅ {channel}: 正常")
            
            # 最終使用日を記録（トークンファイルの更新日時）
            last_used = datetime.fromtimestamp(os.path.getmtime(token_file))
            days_since_used = (datetime.now() - last_used).days
            
            if days_since_used > 150:  # 5ヶ月以上使われていない
                warning_messages.append(
                    f"{channel}: {days_since_used}日間使用されていません。"
                    f"6ヶ月（180日）で失効します。"
                )
                print(f"   ⚠️ 最終使用: {days_since_used}日前")
            else:
                print(f"   最終使用: {days_since_used}日前")
                
        except Exception as e:
            warning_messages.append(f"{channel}: エラー - {str(e)}")
            all_healthy = False
            print(f"❌ {channel}: エラー - {e}")
    
    print("\n" + "="*50)
    
    if warning_messages:
        print("⚠️ 警告:")
        for msg in warning_messages:
            print(f"  - {msg}")
        print("\n対処法:")
        print("  python3 youtube_auth_manager.py --channel [チャンネル名] --force")
    
    if all_healthy and not warning_messages:
        print("✅ すべてのトークンは健全です")
        print("リフレッシュトークンが存在し、定期的に使用されています。")
        return 0
    else:
        return 1

def refresh_active_tokens():
    """アクティブなトークンをリフレッシュして最終使用日を更新"""
    
    channels = ['NB', 'OM', 'SBC', 'RL']
    
    print("\n=== トークンのリフレッシュ ===")
    
    for channel in channels:
        token_file = f'token_{channel}.pickle'
        
        if not os.path.exists(token_file):
            continue
        
        try:
            manager = YouTubeAuthManager(channel)
            # get_authenticated_service を呼ぶことで自動的にリフレッシュされる
            youtube = manager.get_authenticated_service()
            print(f"✅ {channel}: トークンをリフレッシュしました")
        except Exception as e:
            print(f"❌ {channel}: リフレッシュ失敗 - {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='トークン健全性チェック')
    parser.add_argument('--refresh', action='store_true',
                       help='トークンをリフレッシュして最終使用日を更新')
    
    args = parser.parse_args()
    
    exit_code = check_all_tokens()
    
    if args.refresh:
        refresh_active_tokens()
    
    sys.exit(exit_code)