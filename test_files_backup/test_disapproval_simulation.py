#!/usr/bin/env python3
"""
不承認シミュレーションテスト
YT_NB_7stepパク応援特典8選_MCC02運用02_28_01が不承認になった想定
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルート設定
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(
    project_root / 'credentials' / 'google_service_account.json'
)

from automation.approval_status_reader import ApprovalStatusReader
from automation.simple_queue_manager import SimpleQueueManager
from automation.google_drive_finder import GoogleDriveFinder

def test_disapproval_flow():
    """不承認フローの完全テスト"""
    
    print("=" * 80)
    print("🔬 不承認シミュレーションテスト")
    print("=" * 80)
    
    # テスト対象の広告
    test_ad_group = "YT_NB_7stepパク応援特典8選_MCC02運用02_28_01"
    test_account_id = "7042358345"  # スプレッドシートから取得した実際のID
    
    print(f"\n📋 テスト対象:")
    print(f"   広告グループ: {test_ad_group}")
    print(f"   アカウントID: {test_account_id}")
    
    # 1. 審査状態シートから広告情報を取得（実際にはデータをシミュレート）
    print("\n1️⃣ 審査状態シートから情報取得（シミュレーション）...")
    
    # 広告グループ名を解析
    # YT_NB_7stepパク応援特典8選_MCC02運用02_28_01
    # YT_ は prefix
    # NB は案件名
    # 7stepパク応援特典8選 は動画名的な部分
    
    parts = test_ad_group.split('_')
    if parts[0] == 'YT':
        project_name = parts[1]  # NB
        # 動画名部分を推測（MCCより前の部分）
        video_name_parts = []
        for part in parts[2:]:
            if 'MCC' in part:
                break
            video_name_parts.append(part)
        video_name = '_'.join(video_name_parts) if video_name_parts else test_ad_group
    else:
        project_name = 'NB'
        video_name = test_ad_group
    
    print(f"   解析結果:")
    print(f"   - 案件名: {project_name}")
    print(f"   - 動画名: {video_name}")
    
    # 2. 代替動画を検索
    print("\n2️⃣ Google Driveから代替動画を検索...")
    finder = GoogleDriveFinder()
    
    # NBの動画を検索
    videos = finder.list_videos(limit=50)
    nb_videos = [v for v in videos if 'NB' in v['name']]
    
    if nb_videos:
        # 適当な動画を選択（実際には条件に基づいて選択）
        replacement_video = nb_videos[0]
        print(f"   代替動画発見: {replacement_video['name']}")
        
        # 動画をダウンロード
        print("\n3️⃣ 動画ダウンロード...")
        video_path = finder.find_and_download(replacement_video['name'].replace('.mp4', ''))
        
        if video_path:
            print(f"   ✅ ダウンロード完了: {video_path}")
            
            # 背景合成処理（今回はスキップ）
            print("\n4️⃣ 背景合成処理...")
            print("   ⏭️ テストのためスキップ")
            
            # YouTubeアップロード（今回はダミーURL）
            print("\n5️⃣ YouTubeアップロード...")
            print("   ⏭️ テストのためダミーURL使用")
            youtube_url = f"https://www.youtube.com/watch?v=test_{datetime.now().strftime('%H%M%S')}"
            print(f"   テストURL: {youtube_url}")
        else:
            print("   ❌ ダウンロード失敗、ダミーURLを使用")
            youtube_url = "https://www.youtube.com/watch?v=test_dummy"
    else:
        print("   ⚠️ 代替動画が見つからない、ダミーURLを使用")
        youtube_url = "https://www.youtube.com/watch?v=test_no_video"
    
    # 6. 広告キューに追加（重要！）
    print("\n6️⃣ 広告キューに追加...")
    queue_manager = SimpleQueueManager()
    
    process_id = queue_manager.add_to_queue(
        video_url=youtube_url,
        project_name=project_name,
        ad_name=f"{project_name}_再審査_{datetime.now().strftime('%H%M%S')}",
        video_name=video_name,
        ad_group_name=test_ad_group,  # 実際の広告グループ名を渡す！
        account_id=test_account_id,    # 実際のアカウントIDを渡す！
        metadata={
            "original_ad": test_ad_group,
            "reason": "不承認シミュレーション",
            "test": True
        }
    )
    
    print(f"   ✅ キュー追加完了: {process_id}")
    print(f"   - 広告グループ名: {test_ad_group}")
    print(f"   - アカウントID: {test_account_id}")
    print(f"   - YouTube URL: {youtube_url}")
    
    # 7. キューの状態確認
    print("\n7️⃣ キューステータス確認...")
    status = queue_manager.get_queue_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 80)
    print("✅ Python側のテスト完了！")
    print("\n次のステップ:")
    print("1. スプレッドシートの「広告キュー」シートを確認")
    print("2. GASで processQueueFromSheets() を実行")
    print("3. getAdGroupInfo() が正しく動作するか確認")
    print("4. createAdCopy() のパラメータが正しいか確認")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_disapproval_flow()
    sys.exit(0 if success else 1)