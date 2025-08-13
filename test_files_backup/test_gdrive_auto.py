#!/usr/bin/env python3
"""
Google Drive動画検索の自動テスト
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 環境変数設定
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'service_account.json')

from automation.google_drive_finder import GoogleDriveFinder

def test_google_drive():
    """Google Drive動画検索テスト"""
    print("=" * 60)
    print("🎥 Google Drive 動画検索テスト（自動実行）")
    print("=" * 60)
    
    try:
        # Google Drive Finder初期化
        finder = GoogleDriveFinder()
        
        # 動画検索
        print("\n📂 動画を検索中...")
        videos = finder.list_videos(limit=5)
        
        if videos:
            print(f"\n✅ {len(videos)}件の動画が見つかりました:")
            for i, video in enumerate(videos, 1):
                print(f"{i}. {video['name']} ({video.get('size', 'N/A')} bytes)")
                print(f"   ID: {video['id']}")
        else:
            print("\n⚠️ 動画が見つかりませんでした")
            print("Google Driveのフォルダ共有設定を確認してください")
            
        return len(videos) > 0
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_google_drive()
    sys.exit(0 if success else 1)