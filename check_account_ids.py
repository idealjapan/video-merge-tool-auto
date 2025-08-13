#!/usr/bin/env python3
"""アカウントIDを自動検出"""

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
    
    # アカウントIDを収集
    account_ids = {}
    for i, row in enumerate(all_values[5:], start=6):  # データは6行目から
        if len(row) > 25:
            ad_name = str(row[0]).strip()
            account_id = str(row[25]).strip()  # Z列
            if account_id and account_id != '-' and account_id != '':
                # 案件名を推測
                if 'YT_' in ad_name:
                    parts = ad_name.split('_')
                    if len(parts) > 1:
                        project = parts[1]
                        if project not in account_ids:
                            account_ids[project] = account_id
    
    print('=== 検出されたアカウントID ===')
    for project, acc_id in sorted(account_ids.items()):
        print(f'{project}: {acc_id}')
    
    if not account_ids:
        print('アカウントIDが見つかりませんでした')
        print('\n最初の5件のデータを確認:')
        for i, row in enumerate(all_values[5:10], start=6):
            if len(row) > 25 and row[0]:
                print(f'行{i}: 広告名={row[0][:30]}, Z列={row[25]}')

if __name__ == "__main__":
    main()