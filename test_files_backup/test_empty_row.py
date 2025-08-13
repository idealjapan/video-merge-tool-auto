#!/usr/bin/env python3
"""
最初の空の行に追加するテスト
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from automation.youtube_url_logger import YouTubeURLLogger

def test_empty_row():
    """最初の空の行に追加"""
    
    print("=" * 60)
    print("最初の空の行に追加テスト")
    print("=" * 60)
    
    # ロガーを初期化
    url_logger = YouTubeURLLogger()
    
    # テストデータ
    test_time = datetime.now().strftime("%H%M%S")
    test_data = (f"SBC_空行テスト_{test_time}", f"https://youtube.com/watch?v=empty_{test_time}")
    
    print(f"\n追加するデータ:")
    print(f"  広告名: {test_data[0]}")
    print(f"  URL: {test_data[1]}")
    
    # 追加
    success = url_logger.add_youtube_url(test_data[0], test_data[1])
    
    if success:
        print("\n✅ 追加成功！")
        print("スプレッドシートの最初の空の行を確認してください")
    else:
        print("\n❌ 追加失敗")

if __name__ == "__main__":
    test_empty_row()