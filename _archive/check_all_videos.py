#!/usr/bin/env python3
"""
Google Drive内の全動画を確認
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'google_service_account.json')

from automation.google_drive_finder import GoogleDriveFinder

def check_all_videos():
    print("=" * 60)
    print("📹 Google Drive 全動画確認")
    print("=" * 60)
    
    finder = GoogleDriveFinder()
    videos = finder.list_videos(limit=50)  # 多めに取得
    
    print(f"\n見つかった動画: {len(videos)}件\n")
    for i, video in enumerate(videos, 1):
        print(f"{i:2}. {video['name']}")
    
    return len(videos)

if __name__ == "__main__":
    count = check_all_videos()
    print(f"\n合計: {count}件の動画")