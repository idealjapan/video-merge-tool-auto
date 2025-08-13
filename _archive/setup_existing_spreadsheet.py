#!/usr/bin/env python3
"""
既存のスプレッドシートにシートを追加
"""

import gspread
from google.oauth2.service_account import Credentials
import os

def setup_existing_spreadsheet():
    """既存のスプレッドシートに必要なシートを追加"""
    
    print("=" * 60)
    print("📊 既存スプレッドシートへのシート追加")
    print("=" * 60)
    
    # 認証
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    creds_file = 'credentials/google_service_account.json'
    if not os.path.exists(creds_file):
        print(f"❌ {creds_file} が見つかりません")
        return
    
    creds = Credentials.from_service_account_file(creds_file, scopes=scope)
    client = gspread.authorize(creds)
    
    print("\n既存のスプレッドシートのURLを入力してください")
    print("例: https://docs.google.com/spreadsheets/d/xxxxx/edit")
    spreadsheet_url = input("URL: ").strip()
    
    # URLからIDを抽出
    if '/d/' in spreadsheet_url:
        spreadsheet_id = spreadsheet_url.split('/d/')[1].split('/')[0]
    else:
        spreadsheet_id = spreadsheet_url
    
    print(f"\nスプレッドシートID: {spreadsheet_id}")
    
    try:
        # スプレッドシートを開く
        spreadsheet = client.open_by_key(spreadsheet_id)
        print(f"✅ スプレッドシート取得: {spreadsheet.title}")
        
        # 追加するシート
        sheets_to_add = {
            '処理待ち': ['広告名', 'キャンペーン', 'ステータス', '処理日時', 'YouTube URL', 'エラー'],
            '処理済み': ['広告名', 'キャンペーン', '処理日時', 'YouTube URL'],
            'エラーログ': ['日時', '広告名', 'エラー内容', '対処法'],
            '広告差し替えキュー': [
                '処理ID', 'ステータス', '追加日時', '処理開始日時', '完了日時',
                '動画URL', '案件名', '広告名', '動画名', 'リトライ回数',
                'エラーメッセージ', '処理結果', '新広告ID', '処理時間(秒)', 'メタデータ'
            ],
            'YT動画URL': ['案件', '動画名', '動画URL', '使用済み', '審査落ち', '追加日時']
        }
        
        print("\n📝 追加するシートを選択してください:")
        print("1. すべて追加（推奨）")
        print("2. 処理待ち・処理済み・エラーログのみ")
        print("3. 広告差し替えキューのみ")
        print("4. YT動画URLのみ")
        print("5. カスタム選択")
        
        choice = input("\n選択 (1-5): ").strip()
        
        selected_sheets = {}
        if choice == '1':
            selected_sheets = sheets_to_add
        elif choice == '2':
            selected_sheets = {k: v for k, v in sheets_to_add.items() 
                             if k in ['処理待ち', '処理済み', 'エラーログ']}
        elif choice == '3':
            selected_sheets = {k: v for k, v in sheets_to_add.items() 
                             if k == '広告差し替えキュー'}
        elif choice == '4':
            selected_sheets = {k: v for k, v in sheets_to_add.items() 
                             if k == 'YT動画URL'}
        elif choice == '5':
            print("\n追加したいシートを選択（y/n）:")
            for sheet_name in sheets_to_add.keys():
                add = input(f"  {sheet_name}? (y/n): ").lower() == 'y'
                if add:
                    selected_sheets[sheet_name] = sheets_to_add[sheet_name]
        
        # シートを追加
        print("\n🔄 シート追加中...")
        added_sheets = []
        
        for sheet_name, headers in selected_sheets.items():
            try:
                # 既存のシートをチェック
                worksheet = spreadsheet.worksheet(sheet_name)
                print(f"  ⚠️  既存: {sheet_name}")
            except:
                # 新規シート作成
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=1000,
                    cols=len(headers) + 5
                )
                
                # ヘッダー追加
                worksheet.update('A1', [headers])
                
                # ヘッダーの書式設定
                worksheet.format('A1:Z1', {
                    "backgroundColor": {"red": 0.2, "green": 0.5, "blue": 0.8},
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
                })
                
                added_sheets.append(sheet_name)
                print(f"  ✅ 追加: {sheet_name}")
        
        # 設定ファイルを更新
        print("\n💾 設定を保存中...")
        
        # automation/config.pyを更新する必要があるか確認
        config_file = 'automation/config.py'
        if os.path.exists(config_file):
            print(f"\n⚠️  {config_file} のSPREADSHEET_IDを更新してください:")
            print(f'   SPREADSHEET_ID = "{spreadsheet_id}"')
        
        # .envファイルに記録
        env_content = f"""
# スプレッドシート設定
SPREADSHEET_ID={spreadsheet_id}
SPREADSHEET_URL={spreadsheet_url}
"""
        
        with open('.env.spreadsheet', 'w') as f:
            f.write(env_content)
        
        print("✅ .env.spreadsheetに保存しました")
        
        # 結果表示
        print("\n" + "=" * 60)
        print("✅ セットアップ完了！")
        print("\n📊 使用するスプレッドシート:")
        print(f"   {spreadsheet.title}")
        print(f"   URL: {spreadsheet_url}")
        
        if added_sheets:
            print(f"\n🆕 追加されたシート:")
            for sheet in added_sheets:
                print(f"   - {sheet}")
        
        print("\n⚠️  次のステップ:")
        print("1. automation/config.py のSPREADSHEET_IDを更新")
        print(f'   SPREADSHEET_ID = "{spreadsheet_id}"')
        print("2. スプレッドシートを共有設定で使用するアカウントと共有")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print("\nトラブルシューティング:")
        print("1. URLが正しいか確認")
        print("2. サービスアカウントがスプレッドシートにアクセス権限があるか確認")
        print("3. スプレッドシートの共有設定を確認")

if __name__ == "__main__":
    setup_existing_spreadsheet()