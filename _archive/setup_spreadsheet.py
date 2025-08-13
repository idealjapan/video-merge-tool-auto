#!/usr/bin/env python3
"""
必要なスプレッドシートを自動作成
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

def create_management_spreadsheets():
    """管理用スプレッドシートを作成"""
    
    print("=" * 60)
    print("📊 スプレッドシート自動作成ツール")
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
    
    # 作成するスプレッドシート
    spreadsheets = {
        '広告管理': {
            'sheets': {
                '処理待ち': ['広告名', 'キャンペーン', 'ステータス', '処理日時', 'YouTube URL', 'エラー'],
                '処理済み': ['広告名', 'キャンペーン', '処理日時', 'YouTube URL'],
                'エラーログ': ['日時', '広告名', 'エラー内容', '対処法']
            }
        },
        'YT動画URL': {
            'sheets': {
                'YT動画URL': ['案件', '動画名', '動画URL', '使用済み', '審査落ち', '追加日時'],
                '広告差し替えキュー': [
                    '処理ID', 'ステータス', '追加日時', '処理開始日時', '完了日時',
                    '動画URL', '案件名', '広告名', '動画名', 'リトライ回数',
                    'エラーメッセージ', '処理結果', '新広告ID', '処理時間(秒)', 'メタデータ'
                ],
                '広告差し替え履歴': [
                    '処理日時', '案件名', '広告名', '広告グループ',
                    '旧広告ID', '新広告ID', '動画URL', 'ステータス'
                ]
            }
        }
    }
    
    created_sheets = []
    
    for sheet_name, config in spreadsheets.items():
        try:
            # 既存のスプレッドシートを探す
            try:
                spreadsheet = client.open(sheet_name)
                print(f"✅ 既存: {sheet_name}")
            except:
                # 新規作成
                spreadsheet = client.create(sheet_name)
                print(f"🆕 作成: {sheet_name}")
                
                # サービスアカウントのメールを取得して共有設定
                service_account_email = creds.service_account_email
                spreadsheet.share(service_account_email, perm_type='user', role='owner')
            
            # 各シートを作成
            for worksheet_name, headers in config['sheets'].items():
                try:
                    worksheet = spreadsheet.worksheet(worksheet_name)
                    print(f"  ✅ シート既存: {worksheet_name}")
                except:
                    # 新規シート作成
                    if worksheet_name == list(config['sheets'].keys())[0]:
                        # 最初のシートは既存のSheet1を使用
                        worksheet = spreadsheet.sheet1
                        worksheet.update_title(worksheet_name)
                    else:
                        worksheet = spreadsheet.add_worksheet(
                            title=worksheet_name,
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
                    
                    print(f"  🆕 シート作成: {worksheet_name}")
            
            created_sheets.append({
                'name': sheet_name,
                'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
            })
            
        except Exception as e:
            print(f"❌ エラー ({sheet_name}): {e}")
    
    # 結果表示
    print("\n" + "=" * 60)
    print("📋 作成されたスプレッドシート:")
    print("=" * 60)
    
    for sheet in created_sheets:
        print(f"\n📊 {sheet['name']}")
        print(f"   URL: {sheet['url']}")
    
    # 設定ファイルに記録
    if created_sheets:
        print("\n💾 スプレッドシートIDを保存中...")
        
        env_content = "\n# スプレッドシートID\n"
        for sheet in created_sheets:
            sheet_id = sheet['url'].split('/d/')[1].split('/')[0] if '/d/' in sheet['url'] else ''
            env_content += f"# {sheet['name']}: {sheet_id}\n"
        
        with open('.env.spreadsheets', 'w') as f:
            f.write(env_content)
        
        print("✅ .env.spreadsheetsに保存しました")
    
    print("\n" + "=" * 60)
    print("✅ セットアップ完了！")
    print("\n⚠️  重要: 作成したスプレッドシートを")
    print("   使用するGoogleアカウントと共有してください")
    print("=" * 60)

if __name__ == "__main__":
    create_management_spreadsheets()