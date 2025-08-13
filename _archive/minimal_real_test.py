#!/usr/bin/env python3
"""
最小限の実データテスト - 1件だけ処理
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def prepare_test_data():
    """テストデータを準備"""
    print("\n" + "=" * 60)
    print("📋 テストデータ準備")
    print("=" * 60)
    
    # テスト用動画を作成（既存の動画をコピー）
    test_video_source = None
    for ext in ['*.mp4', '*.mov', '*.avi']:
        videos = list(Path('.').glob(ext))
        if videos:
            test_video_source = videos[0]
            break
    
    if not test_video_source:
        print("❌ テスト用動画が見つかりません")
        print("   任意の動画ファイル（.mp4/.mov/.avi）を配置してください")
        return False
    
    # ad-videosフォルダに配置
    test_dir = Path("ad-videos")
    test_dir.mkdir(exist_ok=True)
    
    test_video = test_dir / "TEST_サンプル広告.mov"
    shutil.copy2(test_video_source, test_video)
    
    print(f"✅ テスト動画を準備: {test_video}")
    return True

def add_test_to_spreadsheet():
    """スプレッドシートにテストデータを追加"""
    print("\n📝 スプレッドシートにテストデータを追加...")
    
    from automation.sheets_manager import SheetsManager
    sm = SheetsManager()
    
    try:
        worksheet = sm.spreadsheet.worksheet('処理待ち')
        
        # 既存のデータを確認
        all_values = worksheet.get_all_values()
        print(f"  既存の行数: {len(all_values)}")
        
        # テストデータを追加
        test_row = [
            'TEST_サンプル広告',  # 広告名
            'テストキャンペーン',  # キャンペーン
            '待機中',  # ステータス
            '',  # 処理日時
            '',  # YouTube URL
            ''   # エラー
        ]
        
        worksheet.append_row(test_row)
        print("✅ テストデータを追加しました")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def run_minimal_test():
    """最小限のテスト実行"""
    print("\n" + "=" * 60)
    print("🚀 最小限テスト実行")
    print("=" * 60)
    
    print("\n⚠️  注意事項:")
    print("  - 「TEST_」で始まる広告1件のみ処理")
    print("  - 背景合成まで実行")
    print("  - YouTube認証がない場合はアップロードをスキップ")
    
    try:
        # モックモードで実行（YouTubeアップロードなし）
        os.environ['TEST_MODE'] = '1'
        
        from automation.ad_processor import AdProcessor
        processor = AdProcessor()
        
        # TEST_で始まる広告のみ処理
        print("\n🔄 処理開始...")
        
        # sheets_managerから直接データ取得
        worksheet = processor.sheets_manager.spreadsheet.worksheet('処理待ち')
        all_values = worksheet.get_all_values()
        
        test_ads = []
        for i, row in enumerate(all_values[1:], start=2):  # ヘッダースキップ
            if row[0].startswith('TEST_'):
                test_ads.append({
                    'row': i,
                    'ad_name': row[0],
                    'campaign': row[1] if len(row) > 1 else '',
                    'status': row[2] if len(row) > 2 else ''
                })
        
        if not test_ads:
            print("❌ TEST_で始まる広告が見つかりません")
            return False
        
        print(f"✅ {len(test_ads)}件のテスト広告を発見")
        
        for ad in test_ads:
            print(f"\n処理中: {ad['ad_name']}")
            success = processor.process_single_ad(ad)
            
            if success:
                print(f"✅ 処理成功: {ad['ad_name']}")
            else:
                print(f"❌ 処理失敗: {ad['ad_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # テストモードを解除
        if 'TEST_MODE' in os.environ:
            del os.environ['TEST_MODE']

def cleanup_test_data():
    """テストデータのクリーンアップ"""
    print("\n" + "=" * 60)
    print("🧹 クリーンアップ")
    print("=" * 60)
    
    response = input("\nテストデータを削除しますか？ (y/n): ")
    if response.lower() != 'y':
        print("クリーンアップをスキップしました")
        return
    
    # テスト動画を削除
    test_videos = list(Path("ad-videos").glob("TEST_*"))
    for video in test_videos:
        video.unlink()
        print(f"  削除: {video}")
    
    # 出力ファイルを削除
    test_outputs = list(Path("outputs").glob("TEST_*"))
    for output in test_outputs:
        output.unlink()
        print(f"  削除: {output}")
    
    print("✅ クリーンアップ完了")

def main():
    """メイン処理"""
    print("\n" + "=" * 60)
    print("🧪 最小限の実データテスト")
    print("=" * 60)
    print("このテストは実際にデータを処理しますが、")
    print("TEST_で始まる1件のみを対象とします。")
    
    steps = [
        ("データ準備", prepare_test_data),
        ("スプレッドシート追加", add_test_to_spreadsheet),
        ("処理実行", run_minimal_test),
        ("クリーンアップ", cleanup_test_data)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔸 {step_name}...")
        if not step_func():
            print(f"❌ {step_name}で失敗しました")
            break
    else:
        print("\n" + "=" * 60)
        print("✅ すべてのテストが完了しました！")
        print("=" * 60)

if __name__ == "__main__":
    main()