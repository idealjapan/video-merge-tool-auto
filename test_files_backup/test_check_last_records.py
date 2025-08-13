#!/usr/bin/env python3
"""
最後の数件のレコードを詳細確認
"""
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path

def check_last_records():
    """最後の数件のレコードを詳細確認"""
    
    # 認証
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    credentials = Credentials.from_service_account_file(
        "credentials/google_service_account.json",
        scopes=scopes
    )
    
    client = gspread.authorize(credentials)
    
    # スプレッドシートを開く
    spreadsheet = client.open_by_key("1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U")
    worksheet = spreadsheet.worksheet("YT動画URL")
    
    # 全データを取得
    all_values = worksheet.get_all_values()
    
    print("=" * 60)
    print("最後の10件のレコード")
    print("=" * 60)
    
    # 最後の10件を表示
    for row in all_values[-10:]:
        print(f"案件: {row[0]:<5} | 動画名: {row[1]:<20} | URL: {row[2] if len(row) > 2 else 'なし'}")
    
    print("=" * 60)
    
    # 最後の行を確認
    last_row = all_values[-1]
    if "tGG8Q_GNpXw" in str(last_row):
        print("✅ 最新のテスト動画URLが記録されています！")
    else:
        print("⚠️ 最新のテスト動画URLが見つかりません")
        print(f"最後の行: {last_row}")

if __name__ == "__main__":
    check_last_records()