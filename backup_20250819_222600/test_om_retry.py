#!/usr/bin/env python3
"""
OMチャンネル再テスト（タイムアウト対策済み）
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'google_service_account.json')
os.environ['REPLICATE_API_TOKEN'] = 'r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'

def main():
    """OMチャンネルテスト"""
    print("="*70)
    print("OMチャンネル 再テスト（タイムアウト対策済み）")
    print("="*70)
    
    # 実際のOM動画でテスト
    test_ad = {
        'ad_group_name': 'YT_OM_愛されクリエイター_撮影01_お家で趣味をお仕事にする_MCC01運用01_01_01',
        'project_name': 'OM',
        'video_name': 'OM_愛されクリエイター_撮影01_お家で趣味をお仕事にする',
        'account_id': '1234567890',
        'status': '不承認'
    }
    
    print(f"テスト動画: {test_ad['video_name']}")
    print("タイムアウト対策: 背景生成最大5分")
    print()
    
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
            print("\n✅ OMチャンネル: テスト成功")
        else:
            print("\n❌ OMチャンネル: テスト失敗")
        return result
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        handler.ApprovalStatusReader = original_reader

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)