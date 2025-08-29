#!/usr/bin/env python3
"""
自動トークン更新機能のテストスクリプト
アクセストークンの期限を強制的に切らせて、自動更新が動作するか確認
"""

import os
import pickle
import sys
from datetime import datetime, timedelta
from pathlib import Path
from youtube_auth_manager import YouTubeAuthManager

def test_token_refresh(channel_name='NB'):
    """トークンの自動更新をテスト"""
    
    print(f"=== {channel_name}チャンネルの自動更新テスト ===\n")
    
    # 1. 現在のトークン状態を確認
    manager = YouTubeAuthManager(channel_name)
    status = manager.check_token_status()
    
    print("【現在の状態】")
    print(f"  ステータス: {status['status']}")
    print(f"  詳細: {status['message']}")
    if 'expiry' in status:
        print(f"  期限: {status['expiry']}")
    if 'has_refresh_token' in status:
        print(f"  リフレッシュトークン: {'あり' if status['has_refresh_token'] else 'なし'}")
    
    # リフレッシュトークンがない場合は警告
    if status['status'] == 'valid' and not status.get('has_refresh_token'):
        print("\n⚠️ リフレッシュトークンがありません！")
        print("   以下のコマンドで再認証してください：")
        print(f"   python3 youtube_auth_manager.py --channel {channel_name} --force")
        return False
    
    # 2. トークンの期限を強制的に切らせる
    token_file = f'token_{channel_name}.pickle'
    if os.path.exists(token_file):
        print(f"\n【テスト実行】")
        print("1. トークンの期限を強制的に過去に設定...")
        
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        # 期限を1時間前に設定（期限切れ状態にする）
        original_expiry = creds.expiry
        creds.expiry = datetime.utcnow() - timedelta(hours=1)
        
        with open(token_file, 'wb') as f:
            pickle.dump(creds, f)
        
        print(f"   元の期限: {original_expiry}")
        print(f"   テスト用期限: {creds.expiry} (期限切れ)")
        
        # 3. 自動更新が動作するか確認
        print("\n2. YouTubeサービスを取得（自動更新が発動するはず）...")
        
        try:
            manager2 = YouTubeAuthManager(channel_name)
            youtube = manager2.get_authenticated_service()
            
            # 成功したら、トークンが更新されているはず
            with open(token_file, 'rb') as f:
                updated_creds = pickle.load(f)
            
            print(f"\n【結果】")
            if updated_creds.expiry > datetime.utcnow():
                print("✅ 自動更新成功！")
                print(f"   新しい期限: {updated_creds.expiry}")
                print(f"   リフレッシュトークン: {'保持' if updated_creds.refresh_token else 'なし'}")
                
                # チャンネル情報を取得してテスト
                print("\n3. YouTubeAPIの動作確認...")
                try:
                    channels_response = youtube.channels().list(
                        part="snippet",
                        mine=True
                    ).execute()
                    
                    if channels_response.get('items'):
                        channel_title = channels_response['items'][0]['snippet']['title']
                        print(f"   ✅ API呼び出し成功: {channel_title}")
                    else:
                        print("   ⚠️ チャンネル情報が取得できませんでした")
                except Exception as e:
                    print(f"   ❌ API呼び出しエラー: {e}")
                
                return True
            else:
                print("❌ 自動更新失敗：トークンが更新されていません")
                return False
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            return False
    else:
        print(f"\n❌ トークンファイルが存在しません: {token_file}")
        print(f"   先に認証を実行してください：")
        print(f"   python3 youtube_auth_manager.py --channel {channel_name}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='トークン自動更新テスト')
    parser.add_argument('--channel', default='NB', 
                       choices=['NB', 'OM', 'SBC', 'RL'],
                       help='テストするチャンネル（デフォルト: NB）')
    
    args = parser.parse_args()
    
    success = test_token_refresh(args.channel)
    
    print("\n" + "="*50)
    if success:
        print("🎉 自動更新機能は正常に動作しています！")
        print("今後6ヶ月間は自動的にトークンが更新されます。")
    else:
        print("⚠️ 自動更新機能のテストに失敗しました。")
        print("上記のエラーメッセージを確認してください。")