#!/usr/bin/env python3
"""
Google Drive動画検索・ダウンロードテスト
"""

import os
from pathlib import Path
from datetime import datetime

def test_drive_connection():
    """Google Drive接続テスト"""
    print("\n" + "=" * 60)
    print("🔍 Google Drive接続テスト")
    print("=" * 60)
    
    try:
        from automation.google_drive_finder import GoogleDriveFinder
        finder = GoogleDriveFinder()
        
        print("✅ Google Drive API接続成功")
        return finder
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return None

def search_videos(finder, query=""):
    """動画ファイルを検索"""
    print("\n📂 動画ファイル検索")
    print("-" * 40)
    
    if not query:
        query = input("検索キーワード（空欄で全動画）: ").strip()
    
    try:
        # 動画ファイルを検索（mp4, mov, avi）
        video_extensions = ['mp4', 'mov', 'avi', 'mkv']
        all_videos = []
        
        for ext in video_extensions:
            mime_type = {
                'mp4': 'video/mp4',
                'mov': 'video/quicktime',
                'avi': 'video/x-msvideo',
                'mkv': 'video/x-matroska'
            }.get(ext, f'video/{ext}')
            
            if query:
                files = finder.search_files(f"{query}", mime_type=mime_type, limit=5)
            else:
                files = finder.search_files("", mime_type=mime_type, limit=10)
            
            all_videos.extend(files)
        
        if not all_videos:
            print("❌ 動画ファイルが見つかりません")
            print("\nGoogle Driveに動画をアップロードしてください：")
            print("1. Google Drive (https://drive.google.com) を開く")
            print("2. 任意の動画ファイル（.mp4/.mov）をアップロード")
            print("3. 共有設定でサービスアカウントと共有")
            return []
        
        print(f"\n✅ {len(all_videos)}件の動画を発見:")
        for i, video in enumerate(all_videos, 1):
            size_mb = int(video.get('size', 0)) / (1024 * 1024)
            print(f"  {i}. {video['name']}")
            print(f"     ID: {video['id']}")
            print(f"     サイズ: {size_mb:.1f} MB")
            print(f"     更新日: {video.get('modifiedTime', 'N/A')[:10]}")
        
        return all_videos
        
    except Exception as e:
        print(f"❌ 検索エラー: {e}")
        return []

def test_download(finder, video_file):
    """動画のダウンロードテスト"""
    print("\n⬇️ ダウンロードテスト")
    print("-" * 40)
    
    try:
        # テンポラリフォルダを作成
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        file_name = video_file['name']
        file_id = video_file['id']
        
        print(f"ダウンロード中: {file_name}")
        print(f"ファイルID: {file_id}")
        
        # ダウンロード実行
        output_path = temp_dir / f"test_{datetime.now().strftime('%H%M%S')}_{file_name}"
        
        # ダウンロードメソッドを呼び出し
        success = finder.download_file(file_id, str(output_path))
        
        if success and output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)
            print(f"✅ ダウンロード成功")
            print(f"   保存先: {output_path}")
            print(f"   サイズ: {file_size:.1f} MB")
            return str(output_path)
        else:
            print("❌ ダウンロード失敗")
            return None
            
    except Exception as e:
        print(f"❌ ダウンロードエラー: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_video_processing(video_path):
    """ダウンロードした動画の処理テスト"""
    print("\n🎬 動画処理テスト")
    print("-" * 40)
    
    if not video_path or not Path(video_path).exists():
        print("❌ 動画ファイルが存在しません")
        return False
    
    try:
        from video_merger_auto_bg import VideoMergerWithAutoBG
        merger = VideoMergerWithAutoBG()
        
        # 動画情報を取得
        info = merger.get_video_info(video_path)
        
        print("✅ 動画情報取得成功:")
        print(f"   解像度: {info['width']}x{info['height']}")
        print(f"   長さ: {info['duration']:.1f}秒")
        print(f"   FPS: {info['fps']}")
        print(f"   縦横比: {'縦型' if info['height'] > info['width'] else '横型'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return False

def test_full_flow():
    """完全なフローテスト"""
    print("\n" + "=" * 60)
    print("🔄 完全フローテスト")
    print("=" * 60)
    
    # 1. Google Drive接続
    finder = test_drive_connection()
    if not finder:
        return False
    
    # 2. 動画検索
    videos = search_videos(finder)
    if not videos:
        print("\n💡 ヒント: Google Driveに動画をアップロードしてから再実行してください")
        return False
    
    # 3. ダウンロードする動画を選択
    print("\n📝 ダウンロードする動画を選択")
    if len(videos) == 1:
        selected = videos[0]
        print(f"自動選択: {selected['name']}")
    else:
        choice = input(f"番号を入力 (1-{len(videos)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(videos):
                selected = videos[idx]
            else:
                print("❌ 無効な番号")
                return False
        except:
            print("❌ 数字を入力してください")
            return False
    
    # 4. ダウンロード
    downloaded_path = test_download(finder, selected)
    if not downloaded_path:
        return False
    
    # 5. 動画処理テスト
    success = test_video_processing(downloaded_path)
    
    # 6. クリーンアップ
    cleanup = input("\nダウンロードした動画を削除しますか？ (y/n): ").lower()
    if cleanup == 'y':
        Path(downloaded_path).unlink()
        print("✅ 削除しました")
    
    return success

def check_service_account_access():
    """サービスアカウントのアクセス権限確認"""
    print("\n🔐 サービスアカウント情報")
    print("-" * 40)
    
    try:
        import json
        cred_file = Path("credentials/google_service_account.json")
        
        if cred_file.exists():
            with open(cred_file) as f:
                creds = json.load(f)
            
            client_email = creds.get('client_email', 'N/A')
            print(f"サービスアカウント: {client_email}")
            print("\n⚠️  重要: Google Driveのファイル/フォルダを")
            print(f"   {client_email}")
            print("   と共有してください")
            
            return client_email
    except:
        pass
    
    return None

def main():
    """メイン処理"""
    print("\n" + "=" * 60)
    print("🎥 Google Drive 動画取得テスト")
    print("=" * 60)
    
    # サービスアカウント情報表示
    service_account = check_service_account_access()
    
    print("\n選択してください:")
    print("1. 完全フローテスト（推奨）")
    print("2. 接続テストのみ")
    print("3. 動画検索のみ")
    
    choice = input("\n選択 (1-3): ").strip()
    
    if choice == '1':
        test_full_flow()
    elif choice == '2':
        test_drive_connection()
    elif choice == '3':
        finder = test_drive_connection()
        if finder:
            search_videos(finder)
    else:
        print("無効な選択")

if __name__ == "__main__":
    main()