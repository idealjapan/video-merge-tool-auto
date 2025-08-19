#!/usr/bin/env python3
"""
SBCチャンネル単独テスト
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'google_service_account.json')
os.environ['REPLICATE_API_TOKEN'] = 'r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'

def main():
    """SBCチャンネルテスト"""
    print("="*70)
    print("SBCチャンネル 本番テスト")
    print("="*70)
    
    # 実際のSBC動画でテスト
    test_ad = {
        'ad_group_name': 'YT_SBC_変わらない勇気_撮影01(パク)_おとうふさんインタビュー_MCC01運用01_01_01',
        'project_name': 'SBC',
        'video_name': 'SBC_変わらない勇気_撮影01(パク)_おとうふさんインタビュー',
        'account_id': '1234567890',
        'status': '不承認'
    }
    
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
        if result:
            print("\n✅ SBCチャンネル: テスト成功")
        else:
            print("\n❌ SBCチャンネル: テスト失敗")
        return result
    finally:
        handler.ApprovalStatusReader = original_reader

if __name__ == "__main__":
    main()