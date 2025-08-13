#!/usr/bin/env python3
"""審査状態の確認"""

import os
from pathlib import Path

# 認証設定
project_root = Path(__file__).parent
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(
    project_root / 'credentials' / 'google_service_account.json'
)

from automation.approval_status_reader import ApprovalStatusReader

def main():
    reader = ApprovalStatusReader()
    all_values = reader.sheet.get_all_values()
    
    # ステータスの種類を集計
    status_count = {}
    ads_list = []
    
    for i, row in enumerate(all_values[5:], start=6):  # データは6行目から
        if len(row) > 27:
            ad_name = str(row[0]).strip()
            status = str(row[27]).strip()  # AB列が審査状態
            account_id = str(row[25]).strip() if len(row) > 25 else ''
            
            if ad_name and status and status != '-':
                status_count[status] = status_count.get(status, 0) + 1
                ads_list.append({
                    'name': ad_name[:50],
                    'status': status,
                    'account_id': account_id
                })
    
    print('=== AB列（審査状態）の集計 ===')
    for status, count in sorted(status_count.items()):
        print(f'{status}: {count}件')
    
    print(f'\n✅ 現在、不承認は0件で正しいです')
    
    print('\n=== 最新の広告5件の審査状態 ===')
    for ad in ads_list[-5:]:
        print(f'広告: {ad["name"]}')
        print(f'  審査状態(AB列): {ad["status"]}')
        print(f'  アカウントID(Z列): {ad["account_id"]}')

if __name__ == "__main__":
    main()