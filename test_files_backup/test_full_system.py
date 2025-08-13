#!/usr/bin/env python3
"""
システム全体の動作確認
"""

import os
from pathlib import Path

def check_system():
    """システムチェック"""
    
    print("=" * 60)
    print("🔍 システム診断")
    print("=" * 60)
    
    checks = {
        "Google認証": False,
        "スプレッドシート": False,
        "YouTube認証": False,
        "Google Drive": False,
        "動画処理": False
    }
    
    # 1. Google認証確認
    if Path("credentials/google_service_account.json").exists():
        checks["Google認証"] = True
    
    # 2. スプレッドシート確認
    try:
        from automation.sheets_manager import SheetsManager
        sm = SheetsManager()
        checks["スプレッドシート"] = True
    except:
        pass
    
    # 3. YouTube認証確認
    if Path("credentials/youtube_token.pickle").exists():
        checks["YouTube認証"] = True
    elif Path("credentials/youtube_nb_token.pickle").exists():
        checks["YouTube認証"] = "部分的"
    
    # 4. Google Drive確認
    try:
        from automation.google_drive_finder import GoogleDriveFinder
        finder = GoogleDriveFinder()
        checks["Google Drive"] = True
    except:
        pass
    
    # 5. 動画処理確認
    try:
        from video_merger_auto_bg import VideoMergerWithAutoBG
        merger = VideoMergerWithAutoBG()
        checks["動画処理"] = True
    except:
        pass
    
    # 結果表示
    print("\n📊 診断結果:")
    print("-" * 40)
    
    for item, status in checks.items():
        if status == True:
            print(f"✅ {item}: OK")
        elif status == "部分的":
            print(f"⚠️  {item}: 部分的に設定済み")
        else:
            print(f"❌ {item}: 未設定")
    
    # 推奨事項
    print("\n💡 次のステップ:")
    print("-" * 40)
    
    if not checks["スプレッドシート"]:
        print("1. python3 setup_spreadsheet.py でスプレッドシート作成")
    
    if not checks["YouTube認証"]:
        print("2. オフィスで広告担当者と YouTube認証")
    
    if checks["YouTube認証"] == "部分的":
        print("2. YouTube認証を完了させる")
    
    if all(checks.values()):
        print("✨ すべて設定済み！動画処理を開始できます")
        print("   python3 test_complete_flow.py でテスト実行")

if __name__ == "__main__":
    check_system()