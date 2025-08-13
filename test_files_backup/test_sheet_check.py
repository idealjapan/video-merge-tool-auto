#!/usr/bin/env python3
"""
スプレッドシートの記録を確認
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from automation.youtube_url_logger import YouTubeURLLogger

def check_sheet_records():
    """スプレッドシートの記録を確認"""
    
    print("=" * 60)
    print("スプレッドシート記録確認")
    print("=" * 60)
    
    # ロガーを初期化
    url_logger = YouTubeURLLogger()
    
    # 記録されているデータを取得
    records = url_logger.get_all_urls()
    
    print(f"\n現在の記録数: {len(records)}件")
    print("-" * 60)
    
    # 最新の5件を表示
    for i, record in enumerate(records[-5:], 1):
        print(f"\n{i}. 案件: {record.get('案件名', 'N/A')}")
        print(f"   動画名: {record.get('動画名', 'N/A')}")
        print(f"   URL: {record.get('YouTube URL', 'N/A')}")
    
    print("\n" + "=" * 60)
    
    # 最後のテストの記録を確認
    if records:
        last = records[-1]
        if "フルテスト広告" in str(last.get('動画名', '')):
            print("✅ 最新のテスト記録が見つかりました")
        else:
            print("⚠️ 最新のテスト記録が見つかりません")
            print("   最後の記録:", last.get('動画名', 'N/A'))

if __name__ == "__main__":
    check_sheet_records()