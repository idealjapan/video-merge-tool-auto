#!/usr/bin/env python3
"""
既存のYT動画URLスプレッドシートに必要なシートを追加（シンプル版）
"""

import gspread
from google.oauth2.service_account import Credentials

def add_sheets():
    """必要なシートを追加"""
    
    print("=" * 60)
    print("📊 管理用シートを追加")
    print("=" * 60)
    
    # 認証
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    creds = Credentials.from_service_account_file(
        'credentials/google_service_account.json', 
        scopes=scope
    )
    client = gspread.authorize(creds)
    
    # スプレッドシートを開く
    spreadsheet_id = '1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U'
    spreadsheet = client.open_by_key(spreadsheet_id)
    
    print(f"✅ スプレッドシート: {spreadsheet.title}")
    
    # 追加するシート
    sheets_to_add = {
        '処理待ち': ['広告名', 'キャンペーン', 'ステータス', '処理日時', 'YouTube URL', 'エラー'],
        '処理済み': ['広告名', 'キャンペーン', '処理日時', 'YouTube URL', '背景スタイル'],
        'エラーログ': ['日時', '広告名', 'エラー内容', '対処法', 'リトライ回数'],
        '広告差し替えキュー': [
            '処理ID', 'ステータス', '追加日時', '処理開始日時', '完了日時',
            '動画URL', '案件名', '広告名', '動画名', 'リトライ回数',
            'エラーメッセージ', '処理結果', '新広告ID', '処理時間(秒)', 'メタデータ'
        ]
    }
    
    # 既存のシート名を取得
    existing_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
    
    # シートを追加
    for sheet_name, headers in sheets_to_add.items():
        if sheet_name in existing_sheets:
            print(f"  ⚠️  既存: {sheet_name}")
        else:
            try:
                # 新規シート作成
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=1000,
                    cols=len(headers) + 5
                )
                
                # ヘッダー追加（新しい書式）
                worksheet.update(values=[headers], range_name='A1')
                
                # ヘッダーの書式設定
                worksheet.format('A1:Z1', {
                    "backgroundColor": {"red": 0.2, "green": 0.5, "blue": 0.8},
                    "textFormat": {
                        "bold": True, 
                        "foregroundColor": {"red": 1, "green": 1, "blue": 1}
                    }
                })
                
                print(f"  ✅ 追加: {sheet_name}")
                
            except Exception as e:
                print(f"  ❌ エラー ({sheet_name}): {e}")
    
    print("\n✅ 完了！")
    print(f"📌 スプレッドシート: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/")

if __name__ == "__main__":
    add_sheets()