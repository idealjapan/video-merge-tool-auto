#!/usr/bin/env python3
"""
処理履歴記録のテスト
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from automation.sheets_manager import SheetsManager

def test_history_logging():
    """処理履歴記録のテスト"""
    
    print("=" * 60)
    print("処理履歴記録テスト")
    print("=" * 60)
    
    # SheetsManagerを初期化
    sheets = SheetsManager()
    
    # テスト用の処理履歴を追加
    test_records = [
        {
            'ad_name': 'NB_テストキャンペーン',
            'youtube_url': 'https://youtube.com/watch?v=test123',
            'process_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'ad_name': 'SBC_サンプル広告',
            'youtube_url': 'https://youtube.com/watch?v=test456',
            'process_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'ad_name': 'OM_新商品PR',
            'youtube_url': 'https://youtube.com/watch?v=test789',
            'process_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for record in test_records:
        print(f"\n記録中: {record['ad_name']}")
        sheets.add_process_history(
            ad_name=record['ad_name'],
            youtube_url=record['youtube_url'],
            process_time=record['process_time']
        )
        print(f"  ✅ 完了")
    
    print("\n" + "=" * 60)
    print("スプレッドシートに「処理履歴」シートが作成されました")
    print("以下の情報が記録されます：")
    print("  - 処理日時")
    print("  - 広告名")
    print("  - チャンネル（NB/SBC/OM）")
    print("  - YouTube URL")
    print("  - 背景スタイル")
    print("  - ステータス")
    print("=" * 60)

if __name__ == "__main__":
    test_history_logging()