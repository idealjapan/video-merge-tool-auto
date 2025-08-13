#!/usr/bin/env python3
"""
動画ダウンロードをスキップする設定
Google DriveのURLを記録するだけのモード
"""

import os

# 環境変数で制御
os.environ['SKIP_VIDEO_DOWNLOAD'] = '1'
os.environ['VIDEO_URLS_ONLY'] = '1'

print("=" * 60)
print("📝 動画URLのみモード設定")
print("=" * 60)
print("\nこのモードでは：")
print("✅ Google Driveで動画を検索")
print("✅ 動画のURLを記録")
print("❌ ダウンロードはしない")
print("❌ 背景合成はしない")
print("✅ スプレッドシートに記録")
print("\n設定完了！")

# 確認
from automation.sheets_manager import SheetsManager
sm = SheetsManager()

print("\n動画URLのみを記録するモードで動作します")
print("スプレッドシート:", sm.spreadsheet.title)