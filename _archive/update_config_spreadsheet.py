#!/usr/bin/env python3
"""
config.pyのスプレッドシートIDを更新
"""

def update_config():
    print("=" * 60)
    print("📊 スプレッドシート設定の更新")
    print("=" * 60)
    
    print("\nどのスプレッドシートを使いますか？")
    print("1. 既存のYT動画URLスプレッドシート（推奨）")
    print("2. 新しいスプレッドシートID を入力")
    
    choice = input("\n選択 (1-2): ").strip()
    
    if choice == '1':
        spreadsheet_id = "1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U"
        print(f"\n既存のスプレッドシートを使用: {spreadsheet_id}")
    else:
        spreadsheet_id = input("\nスプレッドシートIDを入力: ").strip()
    
    # config.pyを読み込み
    config_path = "automation/config.py"
    with open(config_path, 'r') as f:
        lines = f.readlines()
    
    # SPREADSHEET_IDを追加または更新
    spreadsheet_id_found = False
    new_lines = []
    
    for line in lines:
        if line.startswith("SPREADSHEET_NAME"):
            new_lines.append(line)
            if not spreadsheet_id_found:
                new_lines.append(f'SPREADSHEET_ID = "{spreadsheet_id}"  # スプレッドシートID\n')
                spreadsheet_id_found = True
        elif line.startswith("SPREADSHEET_ID"):
            new_lines.append(f'SPREADSHEET_ID = "{spreadsheet_id}"  # スプレッドシートID\n')
            spreadsheet_id_found = True
        else:
            new_lines.append(line)
    
    # もしSPREADSHEET_IDがなければ、SPREADSHEET_NAMEの後に追加
    if not spreadsheet_id_found:
        final_lines = []
        for line in new_lines:
            final_lines.append(line)
            if line.startswith("SPREADSHEET_NAME"):
                final_lines.append(f'SPREADSHEET_ID = "{spreadsheet_id}"  # スプレッドシートID\n')
        new_lines = final_lines
    
    # config.pyを更新
    with open(config_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ config.py を更新しました")
    print(f"   SPREADSHEET_ID = {spreadsheet_id}")
    
    # sheets_manager.pyも更新が必要か確認
    sheets_manager_path = "automation/sheets_manager.py"
    print(f"\n📝 {sheets_manager_path} の更新も必要です")
    print("   以下のように変更してください:")
    print(f'   self.spreadsheet_id = "{spreadsheet_id}"')
    
    print("\n次のステップ:")
    print("1. python3 setup_existing_spreadsheet.py で必要なシートを追加")
    print("2. テスト実行: python3 test_full_system.py")

if __name__ == "__main__":
    update_config()