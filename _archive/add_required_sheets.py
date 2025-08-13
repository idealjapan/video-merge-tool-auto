#!/usr/bin/env python3
"""
既存のYT動画URLスプレッドシートに必要なシートを追加
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def add_required_sheets():
    """必要なシートを追加"""
    
    print("=" * 60)
    print("📊 必要なシートを追加")
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
    print(f"   URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/")
    
    # 追加するシート（自動処理用）
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
    print(f"\n📋 既存のシート数: {len(existing_sheets)}")
    
    # シートを追加
    added_sheets = []
    skipped_sheets = []
    
    for sheet_name, headers in sheets_to_add.items():
        if sheet_name in existing_sheets:
            skipped_sheets.append(sheet_name)
            print(f"  ⚠️  既存: {sheet_name}")
        else:
            try:
                # 新規シート作成
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=1000,
                    cols=len(headers) + 5
                )
                
                # ヘッダー追加
                worksheet.update('A1', [headers])
                
                # ヘッダーの書式設定（青背景、白文字、太字）
                worksheet.format('A1:Z1', {
                    "backgroundColor": {"red": 0.2, "green": 0.5, "blue": 0.8},
                    "textFormat": {
                        "bold": True, 
                        "foregroundColor": {"red": 1, "green": 1, "blue": 1}
                    }
                })
                
                # 列幅を自動調整
                worksheet.format('A:Z', {"autoResize": {"width": True}})
                
                added_sheets.append(sheet_name)
                print(f"  ✅ 追加: {sheet_name}")
                
            except Exception as e:
                print(f"  ❌ エラー ({sheet_name}): {e}")
    
    # 結果表示
    print("\n" + "=" * 60)
    print("📊 完了！")
    print("=" * 60)
    
    if added_sheets:
        print(f"\n🆕 追加されたシート ({len(added_sheets)}個):")
        for sheet in added_sheets:
            print(f"   - {sheet}")
    
    if skipped_sheets:
        print(f"\n⚠️  既存のためスキップ ({len(skipped_sheets)}個):")
        for sheet in skipped_sheets:
            print(f"   - {sheet}")
    
    print(f"\n📌 スプレッドシートURL:")
    print(f"   https://docs.google.com/spreadsheets/d/{spreadsheet_id}/")
    
    print("\n✅ これで自動処理の準備が整いました！")
    print("   - 処理待ち: 処理する広告を記入")
    print("   - 処理済み: 完了した広告の記録")
    print("   - エラーログ: エラーの記録")
    print("   - 広告差し替えキュー: Google Ads連携用")

if __name__ == "__main__":
    add_required_sheets()