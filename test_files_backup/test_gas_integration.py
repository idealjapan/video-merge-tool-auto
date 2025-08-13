#!/usr/bin/env python3
"""
GAS連携テスト
キューに追加されたデータがGASで処理できることを確認
"""

import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'google_service_account.json')

from automation.simple_queue_manager import SimpleQueueManager
from automation.sheets_manager import SheetsManager

def test_gas_integration():
    """GAS連携のテスト"""
    print("=" * 80)
    print("🔗 GAS連携テスト")
    print("=" * 80)
    
    # 1. テストデータを準備
    print("\n1️⃣ テストデータ準備...")
    queue_manager = SimpleQueueManager()
    sheets_manager = SheetsManager()
    
    # キューにテストデータを追加
    test_data = {
        "video_url": "https://www.youtube.com/watch?v=test123",
        "project_name": "NB",
        "ad_name": f"GASテスト_{datetime.now().strftime('%H%M%S')}",
        "video_name": "テスト動画",
        "metadata": {
            "test": True,
            "purpose": "GAS integration test"
        }
    }
    
    process_id = queue_manager.add_to_queue(**test_data)
    print(f"✅ キューに追加: {process_id}")
    print(f"   広告名: {test_data['ad_name']}")
    
    # 2. キューの状態確認
    print("\n2️⃣ キューステータス確認...")
    status = queue_manager.get_queue_status()
    print(f"   待機中: {status.get('待機中', 0)}")
    print(f"   処理中: {status.get('処理中', 0)}")
    print(f"   完了: {status.get('完了', 0)}")
    print(f"   失敗: {status.get('失敗', 0)}")
    
    # 3. GAS Webアプリのテスト（手動で確認が必要）
    print("\n3️⃣ GAS側の処理確認...")
    print("⚠️ 以下を確認してください：")
    print("   1. Google Apps Scriptでトリガーが設定されているか")
    print("   2. processQueueFromSheets関数が定期実行されるか")
    print("   3. 広告キューシートの「ステータス」が更新されるか")
    
    # 4. 処理待ちデータの確認
    print("\n4️⃣ 処理待ちシート確認...")
    try:
        worksheet = sheets_manager.spreadsheet.worksheet("処理待ち")
        rows = worksheet.get_all_values()
        if len(rows) > 1:
            print(f"   処理待ち件数: {len(rows) - 1}")
            # 最新5件を表示
            for row in rows[-5:]:
                if row[0] != "作成日時":  # ヘッダー以外
                    print(f"   - {row[2]} ({row[3]})")
    except Exception as e:
        print(f"   処理待ちシート未作成: {e}")
    
    # 5. YT動画URLシートの確認
    print("\n5️⃣ YT動画URLシート確認...")
    try:
        yt_worksheet = sheets_manager.spreadsheet.worksheet("YT動画URL")
        yt_rows = yt_worksheet.get_all_values()
        if len(yt_rows) > 1:
            print(f"   登録済み動画数: {len(yt_rows) - 1}")
            # 最新3件を表示
            for row in yt_rows[-3:]:
                if row[0] != "投稿日時":  # ヘッダー以外
                    print(f"   - {row[2]}: {row[3]}")
    except Exception as e:
        print(f"   YT動画URLシート未作成: {e}")
    
    # 6. GAS Webアプリへの直接アクセステスト（オプション）
    print("\n6️⃣ GAS Webアプリ接続テスト...")
    print("   ⚠️ GAS側でWebアプリがデプロイされている必要があります")
    print("   デプロイURL: https://script.google.com/macros/s/[DEPLOYMENT_ID]/exec")
    
    # 手動確認用のガイド
    print("\n" + "=" * 80)
    print("📋 手動確認項目:")
    print("\n1. Google Apps Scriptエディタを開く:")
    print("   https://script.google.com/")
    print("\n2. 以下を確認:")
    print("   ✓ processQueueFromSheets関数が存在")
    print("   ✓ トリガー設定（5分ごと）")
    print("   ✓ 実行ログでエラーがないか")
    print("\n3. スプレッドシートで確認:")
    print(f"   https://docs.google.com/spreadsheets/d/{sheets_manager.spreadsheet.id}")
    print("   ✓ 「広告キュー」シートにデータが追加されているか")
    print("   ✓ ステータスが「処理中」→「完了」に変わるか")
    print("\n4. Google Ads側で確認:")
    print("   ✓ 新しい広告が作成されているか")
    print("   ✓ 動画URLが正しく設定されているか")
    
    print("\n⏰ GASトリガーは5分ごとに実行されます")
    print("💡 すぐにテストする場合は、GASエディタで手動実行してください")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_gas_integration()
    sys.exit(0 if success else 1)