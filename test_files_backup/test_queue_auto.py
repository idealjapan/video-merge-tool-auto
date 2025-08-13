#!/usr/bin/env python3
"""
キューシステムの自動テスト
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 環境変数設定
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'google_service_account.json')

from automation.simple_queue_manager import SimpleQueueManager

def test_queue_system():
    """キューシステムのテスト"""
    print("=" * 60)
    print("📝 キューシステムテスト（自動実行）")
    print("=" * 60)
    
    try:
        # Queue Manager初期化
        print("\n⚙️ Queue Manager初期化中...")
        queue_manager = SimpleQueueManager()
        
        # テストデータ
        test_data = {
            "video_url": f"https://youtube.com/watch?v=TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "project_name": "TEST_プロジェクト",
            "ad_name": f"TEST_広告_{datetime.now().strftime('%H%M%S')}",
            "video_name": "テスト動画.mp4"
        }
        
        # キューに追加
        print(f"\n📥 キューに追加中...")
        print(f"  - URL: {test_data['video_url']}")
        print(f"  - プロジェクト: {test_data['project_name']}")
        print(f"  - 広告名: {test_data['ad_name']}")
        
        process_id = queue_manager.add_to_queue(
            video_url=test_data['video_url'],
            project_name=test_data['project_name'],
            ad_name=test_data['ad_name'],
            video_name=test_data['video_name']
        )
        
        print(f"\n✅ キューに追加成功!")
        print(f"   Process ID: {process_id}")
        
        # ステータス確認
        print(f"\n📊 キューステータス確認中...")
        status = queue_manager.get_queue_status()
        
        if status:
            print(f"   全体ステータス:")
            for key, value in status.items():
                print(f"     {key}: {value}")
        
        # スプレッドシート情報
        print(f"\n📋 スプレッドシート情報:")
        print(f"   名前: {queue_manager.spreadsheet.title}")
        print(f"   URL: https://docs.google.com/spreadsheets/d/{queue_manager.spreadsheet.id}/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_queue_system()
    if success:
        print("\n" + "=" * 60)
        print("✨ キューシステムは正常に動作しています!")
        print("\n⚠️ 注意: GAS側でトリガーを設定すると")
        print("  5分ごとに自動処理されます")
        print("=" * 60)
    sys.exit(0 if success else 1)