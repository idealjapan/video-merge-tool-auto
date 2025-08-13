#!/usr/bin/env python3
"""
Google Drive API 簡易テストスクリプト（非対話式）
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from automation.google_drive_finder import GoogleDriveFinder

def test():
    print("=" * 60)
    print("Google Drive API 接続テスト")
    print("=" * 60)
    
    try:
        # 接続
        finder = GoogleDriveFinder()
        print("✅ API接続: 成功")
        print(f"📁 フォルダID: {finder.folder_id}")
        
        # 動画一覧
        print("\n📹 動画ファイル一覧:")
        videos = finder.list_videos()
        
        if videos:
            for v in videos:
                print(f"  - {v['name']}: {v['size_mb']:.1f}MB")
        else:
            print("  動画がありません")
            print("\n💡 テスト用動画をアップロードするには:")
            print("  1. Google Driveを開く")
            print(f"  2. フォルダID: {finder.folder_id} のフォルダに動画をアップロード")
            print("  3. サービスアカウントと共有されているか確認")
        
        # サービスアカウントのメールアドレスを表示
        import json
        creds_file = Path(__file__).parent / "credentials" / "google_service_account.json"
        with open(creds_file) as f:
            creds = json.load(f)
            print(f"\n📧 サービスアカウント: {creds['client_email']}")
            print("  ↑ このメールアドレスがフォルダに共有されている必要があります")
        
        print("\n" + "=" * 60)
        print("接続テスト完了")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()