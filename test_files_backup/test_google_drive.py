#!/usr/bin/env python3
"""
Google Drive API テストスクリプト
サービスアカウントの設定確認と動画検索テスト
"""
import os
import sys
from pathlib import Path

# モジュールパスを追加
sys.path.append(str(Path(__file__).parent))

def test_google_drive_connection():
    """Google Drive接続テスト"""
    print("=" * 60)
    print("Google Drive API テスト")
    print("=" * 60)
    
    # 1. 認証情報ファイルの確認
    creds_file = Path(__file__).parent / "credentials" / "google_service_account.json"
    
    if not creds_file.exists():
        print("\n❌ 認証情報ファイルが見つかりません")
        print(f"   期待される場所: {creds_file}")
        print("\n📝 セットアップ手順:")
        print("   1. Google Cloud Consoleでサービスアカウントを作成")
        print("   2. JSONキーをダウンロード")
        print("   3. credentials/google_service_account.json として保存")
        print("\n詳細は GOOGLE_DRIVE_SETUP.md を参照してください")
        return False
    
    print("✅ 認証情報ファイル: 見つかりました")
    
    try:
        # 2. Google Drive APIのインポートテスト
        from automation.google_drive_finder import GoogleDriveFinder
        print("✅ モジュールインポート: 成功")
        
        # 3. API接続テスト
        print("\n🔄 Google Drive APIに接続中...")
        finder = GoogleDriveFinder(credentials_file=str(creds_file))
        print("✅ API接続: 成功")
        
        # 4. 動画一覧取得テスト
        print("\n📹 動画ファイル一覧を取得中...")
        videos = finder.list_videos(limit=10)
        
        if videos:
            print(f"✅ {len(videos)}個の動画が見つかりました:")
            for v in videos[:5]:  # 最初の5個だけ表示
                print(f"   - {v['name']}: {v['size_mb']:.1f}MB")
            if len(videos) > 5:
                print(f"   ... 他 {len(videos) - 5} 個")
        else:
            print("⚠️  動画が見つかりません")
            print("   Google Driveに動画をアップロードしてください")
        
        # 5. 検索テスト
        print("\n🔍 検索テスト")
        test_name = input("検索する広告名を入力（Enterでスキップ）: ").strip()
        
        if test_name:
            print(f"\n'{test_name}' を検索中...")
            video_path = finder.find_and_download(test_name)
            
            if video_path:
                print(f"✅ 動画をダウンロードしました: {video_path}")
                print(f"   サイズ: {video_path.stat().st_size / (1024*1024):.1f}MB")
                
                # ダウンロードしたファイルを削除
                video_path.unlink()
                print("   (テストファイルは削除しました)")
            else:
                print(f"❌ '{test_name}' が見つかりませんでした")
        
        print("\n" + "=" * 60)
        print("✅ すべてのテストが成功しました！")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"\n❌ モジュールインポートエラー: {e}")
        print("   必要なパッケージをインストールしてください:")
        print("   pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print("\n考えられる原因:")
        print("   1. サービスアカウントの権限不足")
        print("   2. Google Drive APIが有効になっていない")
        print("   3. フォルダの共有設定が正しくない")
        print("\n詳細は GOOGLE_DRIVE_SETUP.md を参照してください")
        return False


if __name__ == "__main__":
    success = test_google_drive_connection()
    sys.exit(0 if success else 1)