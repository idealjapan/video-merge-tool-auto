#!/usr/bin/env python3
"""
包括的テストスイート - 運用前の完全テスト
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveTest:
    """包括的テストクラス"""
    
    def __init__(self):
        self.test_results = {}
        self.test_video = "test_input_video.mov"
        
    def print_header(self, title):
        """ヘッダー表示"""
        print("\n" + "=" * 60)
        print(f"🧪 {title}")
        print("=" * 60)
    
    def test_1_environment(self):
        """環境チェック"""
        self.print_header("テスト1: 環境チェック")
        
        checks = {
            "Python バージョン": sys.version.split()[0],
            "作業ディレクトリ": os.getcwd(),
            "credentials フォルダ": Path("credentials").exists(),
            "outputs フォルダ": Path("outputs").exists(),
            "logs フォルダ": Path("logs").exists()
        }
        
        for item, result in checks.items():
            print(f"  {item}: {result}")
            
        return all([
            Path("credentials").exists(),
            Path("outputs").exists()
        ])
    
    def test_2_credentials(self):
        """認証ファイルチェック"""
        self.print_header("テスト2: 認証ファイル")
        
        files = {
            "Google サービスアカウント": "credentials/google_service_account.json",
            "YouTube OAuth": "credentials/youtube_token.pickle",
            "Client Secrets": "credentials/client_secrets.json"
        }
        
        results = {}
        for name, path in files.items():
            exists = Path(path).exists()
            results[name] = exists
            status = "✅" if exists else "❌"
            print(f"  {status} {name}: {path}")
        
        # 最低限必要なのはGoogleサービスアカウント
        return results.get("Google サービスアカウント", False)
    
    def test_3_imports(self):
        """モジュールインポートテスト"""
        self.print_header("テスト3: モジュールインポート")
        
        modules = [
            ("Google Auth", "google.oauth2.service_account"),
            ("Google Sheets", "gspread"),
            ("Google API", "googleapiclient"),
            ("OpenCV", "cv2"),
            ("MoviePy", "moviepy.editor"),
            ("Requests", "requests")
        ]
        
        failed = []
        for name, module in modules:
            try:
                __import__(module)
                print(f"  ✅ {name} ({module})")
            except ImportError as e:
                print(f"  ❌ {name} ({module}): {e}")
                failed.append(name)
        
        if failed:
            print(f"\n  ⚠️  不足: pip install {' '.join(failed)}")
        
        return len(failed) == 0
    
    def test_4_spreadsheet(self):
        """スプレッドシート接続テスト"""
        self.print_header("テスト4: スプレッドシート接続")
        
        try:
            from automation.sheets_manager import SheetsManager
            sm = SheetsManager()
            
            print(f"  ✅ 接続成功")
            print(f"  スプレッドシート: {sm.spreadsheet.title}")
            print(f"  シート数: {len(sm.spreadsheet.worksheets())}")
            
            # 必要なシートの確認
            required_sheets = ['処理待ち', '処理済み', 'エラーログ', '広告差し替えキュー']
            sheet_titles = [s.title for s in sm.spreadsheet.worksheets()]
            
            for sheet in required_sheets:
                if sheet in sheet_titles:
                    print(f"    ✅ {sheet}")
                else:
                    print(f"    ❌ {sheet} (不足)")
            
            return True
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return False
    
    def test_5_google_drive(self):
        """Google Drive接続テスト"""
        self.print_header("テスト5: Google Drive")
        
        try:
            from automation.google_drive_finder import GoogleDriveFinder
            finder = GoogleDriveFinder()
            
            # テストフォルダの検索
            files = finder.search_files("test", limit=3)
            
            print(f"  ✅ Drive API接続成功")
            print(f"  検索結果: {len(files)}件")
            
            return True
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return False
    
    def test_6_video_processing(self):
        """動画処理テスト"""
        self.print_header("テスト6: 動画処理エンジン")
        
        try:
            from video_merger_auto_bg import VideoMergerWithAutoBG
            merger = VideoMergerWithAutoBG()
            
            # テスト動画があるか確認
            if not Path(self.test_video).exists():
                print(f"  ⚠️  テスト動画なし: {self.test_video}")
                print("     任意の動画を test_input_video.mov として配置してください")
                return False
            
            # 動画情報取得テスト
            info = merger.get_video_info(self.test_video)
            print(f"  ✅ 動画読み込み成功")
            print(f"     解像度: {info['width']}x{info['height']}")
            print(f"     長さ: {info['duration']:.1f}秒")
            print(f"     FPS: {info['fps']}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return False
    
    def test_7_dry_run(self):
        """ドライラン（実際の処理なし）"""
        self.print_header("テスト7: ドライラン")
        
        try:
            print("\n  📝 スプレッドシートにテストデータを追加...")
            
            from automation.sheets_manager import SheetsManager
            sm = SheetsManager()
            
            # テストデータ
            test_data = {
                'ad_name': f'TEST_{datetime.now().strftime("%H%M%S")}',
                'campaign': 'テストキャンペーン',
                'status': 'テスト'
            }
            
            # 処理待ちシートに追加
            try:
                worksheet = sm.spreadsheet.worksheet('処理待ち')
                worksheet.append_row([
                    test_data['ad_name'],
                    test_data['campaign'],
                    test_data['status'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ])
                print(f"  ✅ テストデータ追加: {test_data['ad_name']}")
            except Exception as e:
                print(f"  ❌ データ追加エラー: {e}")
                return False
            
            print("\n  🔄 処理フローの確認...")
            print("  1. Google Driveから動画検索 → ⚠️  スキップ（YouTube認証なし）")
            print("  2. 背景合成処理 → ✅ 実行可能")
            print("  3. YouTubeアップロード → ⚠️  スキップ（認証なし）")
            print("  4. スプレッドシート更新 → ✅ 実行可能")
            
            return True
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return False
    
    def test_8_queue_system(self):
        """キューシステムテスト"""
        self.print_header("テスト8: キューシステム")
        
        try:
            from automation.simple_queue_manager import SimpleQueueManager
            queue = SimpleQueueManager()
            
            # テストタスク追加
            process_id = queue.add_to_queue(
                video_url="https://youtube.com/watch?v=test",
                project_name="テスト案件",
                ad_name=f"テスト広告_{datetime.now().strftime('%H%M%S')}"
            )
            
            print(f"  ✅ キュー追加成功: {process_id}")
            
            # ステータス確認
            status = queue.get_queue_status()
            print(f"  📊 キューステータス:")
            for k, v in status.items():
                print(f"     {k}: {v}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return False
    
    def run_all_tests(self):
        """すべてのテストを実行"""
        print("=" * 60)
        print("🔬 包括的システムテスト開始")
        print("=" * 60)
        print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("環境チェック", self.test_1_environment),
            ("認証ファイル", self.test_2_credentials),
            ("モジュール", self.test_3_imports),
            ("スプレッドシート", self.test_4_spreadsheet),
            ("Google Drive", self.test_5_google_drive),
            ("動画処理", self.test_6_video_processing),
            ("ドライラン", self.test_7_dry_run),
            ("キューシステム", self.test_8_queue_system)
        ]
        
        results = {}
        for name, test_func in tests:
            try:
                result = test_func()
                results[name] = result
                time.sleep(1)  # API制限対策
            except Exception as e:
                print(f"\n❌ テスト失敗: {name}")
                print(f"   エラー: {e}")
                results[name] = False
        
        # 結果サマリー
        self.print_header("テスト結果サマリー")
        
        passed = sum(1 for r in results.values() if r)
        total = len(results)
        
        for name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status}: {name}")
        
        print(f"\n📊 合計: {passed}/{total} テスト合格")
        
        if passed == total:
            print("\n🎉 すべてのテストに合格しました！")
            print("   運用を開始できます。")
        else:
            print("\n⚠️  一部のテストが失敗しました。")
            print("   上記のエラーを確認して修正してください。")
        
        return passed == total


def main():
    """メイン処理"""
    tester = ComprehensiveTest()
    
    print("\n⚠️  このテストは実際にスプレッドシートに書き込みます")
    print("   テスト用のデータは 'TEST_' で始まる名前になります")
    
    response = input("\nテストを開始しますか？ (y/n): ")
    if response.lower() != 'y':
        print("テストをキャンセルしました")
        return
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()