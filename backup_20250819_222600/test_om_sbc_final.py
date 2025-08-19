#!/usr/bin/env python3
"""
OM/SBCチャンネル本番テスト
実際の動画名を使用
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'google_service_account.json')
os.environ['REPLICATE_API_TOKEN'] = 'r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'

def test_om():
    """OMチャンネルテスト"""
    print("\n" + "="*70)
    print("OMチャンネル テスト")
    print("="*70)
    
    # 実際のOM動画でテスト
    test_ads = [
        {
            'ad_group_name': 'YT_OM_愛されクリエイター_撮影01_お家で趣味をお仕事にする_MCC01運用01_01_01',
            'project_name': 'OM',
            'video_name': 'OM_愛されクリエイター_撮影01_お家で趣味をお仕事にする',
            'account_id': '1234567890'
        },
        {
            'ad_group_name': 'YT_OM_愛されクリエイター_撮影01_好きをお仕事にする_MCC01運用01_01_01',
            'project_name': 'OM',
            'video_name': 'OM_愛されクリエイター_撮影01_好きをお仕事にする',
            'account_id': '1234567890'
        }
    ]
    
    # 最初の動画でテスト
    test_ad = test_ads[0]
    print(f"テスト動画: {test_ad['video_name']}")
    
    # モックを使って本番処理を実行
    class MockReader:
        def get_disapproved_ads(self):
            return [test_ad]
    
    import production_disapproval_handler as handler
    original_reader = handler.ApprovalStatusReader
    handler.ApprovalStatusReader = MockReader
    
    try:
        result = handler.process_disapproved_ad()
        return result
    finally:
        handler.ApprovalStatusReader = original_reader

def test_sbc():
    """SBCチャンネルテスト"""
    print("\n" + "="*70)
    print("SBCチャンネル テスト")
    print("="*70)
    
    # 実際のSBC動画でテスト
    test_ads = [
        {
            'ad_group_name': 'YT_SBC_変わらない勇気_撮影01(パク)_おとうふさんインタビュー_MCC01運用01_01_01',
            'project_name': 'SBC',
            'video_name': 'SBC_変わらない勇気_撮影01(パク)_おとうふさんインタビュー',
            'account_id': '1234567890'
        },
        {
            'ad_group_name': 'YT_SBC_変わらない勇気_撮影01(パク)_皆さんにちょっと変わったお願いをさせて下さい_4分_MCC01運用01_01_01',
            'project_name': 'SBC',
            'video_name': 'SBC_変わらない勇気_撮影01(パク)_皆さんにちょっと変わったお願いをさせて下さい_4分',
            'account_id': '1234567890'
        }
    ]
    
    # 最初の動画でテスト
    test_ad = test_ads[0]
    print(f"テスト動画: {test_ad['video_name']}")
    
    # モックを使って本番処理を実行
    class MockReader:
        def get_disapproved_ads(self):
            return [test_ad]
    
    import production_disapproval_handler as handler
    original_reader = handler.ApprovalStatusReader
    handler.ApprovalStatusReader = MockReader
    
    try:
        result = handler.process_disapproved_ad()
        return result
    finally:
        handler.ApprovalStatusReader = original_reader

def main():
    """メイン処理"""
    print("="*70)
    print("OM/SBCチャンネル 本番テスト")
    print("="*70)
    print("\n設定:")
    print("- 本番と同じ処理フロー")
    print("- 背景合成あり")
    print("- YouTubeアップロード（限定公開）")
    print("- キューシート登録")
    
    results = []
    
    # OMチャンネルテスト
    print("\n【OMチャンネル】")
    try:
        om_result = test_om()
        if om_result:
            results.append("✅ OM: 成功")
        else:
            results.append("❌ OM: 失敗")
    except Exception as e:
        print(f"❌ エラー: {e}")
        results.append(f"❌ OM: エラー - {e}")
    
    # SBCチャンネルテスト
    print("\n【SBCチャンネル】")
    try:
        sbc_result = test_sbc()
        if sbc_result:
            results.append("✅ SBC: 成功")
        else:
            results.append("❌ SBC: 失敗")
    except Exception as e:
        print(f"❌ エラー: {e}")
        results.append(f"❌ SBC: エラー - {e}")
    
    # 結果サマリー
    print("\n" + "="*70)
    print("テスト結果サマリー")
    print("="*70)
    for result in results:
        print(result)
    
    print("\n次のステップ:")
    print("1. YouTubeで動画を確認")
    print("2. 広告キューシートを確認")
    print("3. 必要に応じてGASを実行")

if __name__ == "__main__":
    main()