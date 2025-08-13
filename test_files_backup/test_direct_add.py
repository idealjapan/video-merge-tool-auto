#!/usr/bin/env python3
"""
直接スプレッドシートに追加してテスト
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def direct_test():
    """直接スプレッドシートに追加"""
    
    print("=" * 60)
    print("直接スプレッドシート追加テスト")
    print("=" * 60)
    
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
    
    # 現在の行数を確認
    all_values = worksheet.get_all_values()
    print(f"現在の行数: {len(all_values)}")
    print(f"最後の行: {all_values[-1] if all_values else 'なし'}")
    
    # テストデータを追加
    test_time = datetime.now().strftime("%H:%M:%S")
    test_row = ["NB", f"直接テスト_{test_time}", f"https://youtube.com/watch?v=test_{test_time}"]
    
    print(f"\n追加するデータ: {test_row}")
    worksheet.append_row(test_row)
    print("✅ 追加完了")
    
    # 再度確認
    all_values = worksheet.get_all_values()
    print(f"\n追加後の行数: {len(all_values)}")
    print(f"最後の行: {all_values[-1]}")
    
    # 最後の5行を表示
    print("\n最後の5行:")
    for row in all_values[-5:]:
        print(f"  {row}")

if __name__ == "__main__":
    direct_test()