#!/usr/bin/env python3
"""
NBチャンネルでのフルフローテスト
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'google_service_account.json')

from automation.google_drive_finder import GoogleDriveFinder
from automation.simple_queue_manager import SimpleQueueManager
from automation.sheets_manager import SheetsManager
from video_merger_auto_bg import VideoMergerWithAutoBG

def test_nb_full_flow():
    """NBチャンネルでフルフローをテスト"""
    print("=" * 80)
    print("🎬 NBチャンネル フルフローテスト")
    print("=" * 80)
    
    # 1. NBの動画を選択
    print("\n1️⃣ Google DriveからNBの動画を検索...")
    finder = GoogleDriveFinder()
    videos = finder.list_videos(limit=50)
    
    nb_videos = [v for v in videos if v['name'].startswith('NB_')]
    if not nb_videos:
        print("❌ NBの動画が見つかりません")
        return False
    
    test_video = nb_videos[0]  # 最初のNB動画を使用
    print(f"✅ テスト動画: {test_video['name']}")
    
    # 2. 動画をダウンロード（オプション）
    if os.getenv('SKIP_VIDEO_DOWNLOAD') != '1':
        print("\n2️⃣ 動画をダウンロード...")
        video_path = finder.find_and_download(test_video['name'].replace('.mp4', ''))
        if video_path:
            print(f"✅ ダウンロード完了: {video_path}")
            
            # 3. 背景合成
            print("\n3️⃣ 背景合成処理...")
            merger = VideoMergerWithAutoBG()
            output_path = Path(f"test_output/NB_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            output_path.parent.mkdir(exist_ok=True)
            
            success = merger.merge_with_auto_bg(
                str(video_path),
                str(output_path),
                background_style="style1"
            )
            if success:
                print(f"✅ 背景合成完了: {output_path}")
            else:
                print("❌ 背景合成失敗")
                return False
    else:
        print("\n📝 動画ダウンロードスキップモード")
        output_path = None
    
    # 4. YouTube アップロード（NBチャンネル）
    print("\n4️⃣ YouTube アップロード準備...")
    
    # NBチャンネルのトークン確認
    nb_token_path = project_root / 'credentials' / 'youtube_token_NB.json'
    if nb_token_path.exists():
        print("✅ NBチャンネルの認証トークン確認")
        
        # YouTubeアップロードのテスト（実際にはアップロードしない）
        print("⚠️ テストモードのため、実際のアップロードはスキップ")
        youtube_url = f"https://youtube.com/watch?v=NB_TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    else:
        print("⚠️ NBチャンネルの認証トークンがありません")
        youtube_url = f"https://youtube.com/watch?v=NB_MOCK_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 5. スプレッドシート更新
    print("\n5️⃣ スプレッドシート更新...")
    sheets_manager = SheetsManager()
    
    # YT動画URLシートに記録
    try:
        worksheet = sheets_manager.get_or_create_worksheet("YT動画URL")
        row_data = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "NB_TEST",
            test_video['name'],
            youtube_url,
            "テスト実行"
        ]
        worksheet.append_row(row_data)
        print(f"✅ スプレッドシートに記録")
    except Exception as e:
        print(f"⚠️ スプレッドシート更新エラー: {e}")
    
    # 6. キューに追加
    print("\n6️⃣ Google Ads連携キューに追加...")
    queue_manager = SimpleQueueManager()
    
    process_id = queue_manager.add_to_queue(
        video_url=youtube_url,
        project_name="NB_テストプロジェクト",
        ad_name=f"NB_テスト広告_{datetime.now().strftime('%H%M%S')}",
        video_name=test_video['name']
    )
    
    print(f"✅ キューに追加: {process_id}")
    
    # 7. ステータス確認
    status = queue_manager.get_queue_status()
    print(f"\n📊 キューステータス:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("✨ NBチャンネル フルフローテスト完了！")
    print("\n📋 次のステップ:")
    print("1. GASにキュー処理システムを追加")
    print("2. 実際のYouTubeアップロードを有効化")
    print("3. 本番データでテスト")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    # 環境設定
    os.environ['SKIP_VIDEO_DOWNLOAD'] = '1'  # ダウンロードをスキップ
    
    success = test_nb_full_flow()
    sys.exit(0 if success else 1)