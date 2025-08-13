#!/usr/bin/env python3
"""
完全テストスイート - すべての機能を一括テスト
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# プロジェクトルート
project_root = Path(__file__).parent

def run_test(test_name: str, command: str) -> bool:
    """個別テストを実行"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 出力表示
        if result.stdout:
            print(result.stdout)
        if result.stderr and "Warning" not in result.stderr:
            print(result.stderr, file=sys.stderr)
        
        # 成功判定
        success = result.returncode == 0
        if success:
            print(f"✅ {test_name}: 成功")
        else:
            print(f"❌ {test_name}: 失敗")
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ {test_name}: タイムアウト")
        return False
    except Exception as e:
        print(f"❌ {test_name}: エラー - {e}")
        return False

def main():
    """メインテスト実行"""
    print("="*80)
    print("🚀 完全システムテスト開始")
    print(f"📅 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 環境変数設定
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(
        project_root / 'credentials' / 'google_service_account.json'
    )
    
    # テストリスト
    tests = [
        ("システム診断", "python3 test_full_system.py"),
        ("Google Drive接続", "python3 test_gdrive_auto.py"),
        ("キューシステム", "python3 test_queue_auto.py"),
    ]
    
    # 結果記録
    results = {}
    
    # 各テスト実行
    for test_name, command in tests:
        success = run_test(test_name, command)
        results[test_name] = success
    
    # 結果サマリー
    print("\n" + "="*80)
    print("📊 テスト結果サマリー")
    print("="*80)
    
    all_success = True
    for test_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if not success:
            all_success = False
    
    print("\n" + "="*80)
    
    if all_success:
        print("🎉 すべてのテストが成功しました！")
        print("\n📋 残りのタスク:")
        print("1. GAS側の設定（5分）")
        print("   - スプレッドシートを開く")
        print("   - Apps Scriptにコードを追加")
        print("   - トリガー設定（5分ごと）")
        print("")
        print("2. YouTube認証（オフィスで実施）")
        print("   - 所有者アカウントでログイン")
        print("   - 認証実行")
        print("")
        print("3. 本番テスト（1件だけ）")
        print("   - 実データで動作確認")
        
    else:
        print("⚠️ 一部のテストが失敗しました")
        print("\n失敗したテストを確認してください:")
        for test_name, success in results.items():
            if not success:
                print(f"  - {test_name}")
    
    print("="*80)
    
    # スプレッドシートURL表示
    print("\n📋 スプレッドシートURL:")
    print("https://docs.google.com/spreadsheets/d/1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U/")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())