#!/usr/bin/env python3
"""
テスト用スプレッドシートを作成
"""
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path

def create_test_spreadsheet():
    """テスト用スプレッドシートを作成"""
    
    print("=" * 60)
    print("テスト用スプレッドシート作成")
    print("=" * 60)
    
    # 認証
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds_path = Path("credentials/google_service_account.json")
    if not creds_path.exists():
        print(f"❌ サービスアカウントファイルが見つかりません: {creds_path}")
        return
    
    credentials = Credentials.from_service_account_file(
        str(creds_path),
        scopes=scopes
    )
    
    client = gspread.authorize(credentials)
    
    # スプレッドシートを作成
    try:
        # 既存のスプレッドシートを探す
        spreadsheet = client.open("広告管理")
        print("✅ 既存のスプレッドシートを発見")
    except gspread.SpreadsheetNotFound:
        # 新規作成
        spreadsheet = client.create("広告管理")
        print("✅ 新しいスプレッドシートを作成")
    
    # 不承認広告シートを作成
    try:
        sheet = spreadsheet.worksheet("不承認広告")
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="不承認広告", rows=1000, cols=10)
        sheet.update('A1:F1', [[
            '広告名', 'キャンペーン', 'ステータス', 
            '処理済み', '処理日時', '不承認理由'
        ]])
        # テストデータを追加
        sheet.append_row([
            'NB_テスト広告', 'テストキャンペーン', '不承認',
            'FALSE', '', '背景なし'
        ])
        print("✅ 不承認広告シートを作成")
    
    # 動画ストックシートを作成
    try:
        stock_sheet = spreadsheet.worksheet("動画ストック")
    except gspread.WorksheetNotFound:
        stock_sheet = spreadsheet.add_worksheet(title="動画ストック", rows=1000, cols=10)
        stock_sheet.update('A1:E1', [[
            '広告名', 'タイトル', '元動画URL', 
            '合成済みURL', '更新日時'
        ]])
        print("✅ 動画ストックシートを作成")
    
    # スプレッドシートを共有（オプション）
    # spreadsheet.share('your-email@gmail.com', perm_type='user', role='writer')
    
    print("\n" + "=" * 60)
    print(f"スプレッドシートURL: {spreadsheet.url}")
    print("=" * 60)
    
    return spreadsheet.url

if __name__ == "__main__":
    url = create_test_spreadsheet()
    if url:
        print(f"\nスプレッドシートにアクセス: {url}")