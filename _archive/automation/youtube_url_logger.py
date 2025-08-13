#!/usr/bin/env python3
"""
YouTube URLを指定のスプレッドシートに記録
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class YouTubeURLLogger:
    """YouTube URLを専用スプレッドシートに記録"""
    
    SPREADSHEET_ID = "1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U"
    SHEET_NAME = "YT動画URL"
    
    def __init__(self, service_account_file: str = "credentials/google_service_account.json"):
        """
        初期化
        
        Args:
            service_account_file: サービスアカウントJSONファイルのパス
        """
        self.service_account_file = Path(service_account_file)
        self.client = self._authenticate()
        
    def _authenticate(self) -> gspread.Client:
        """Google Sheets APIの認証"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                str(self.service_account_file),
                scopes=scopes
            )
            
            client = gspread.authorize(credentials)
            logger.info("YouTube URL Logger: Google Sheets認証成功")
            return client
        except Exception as e:
            logger.error(f"YouTube URL Logger: 認証エラー: {e}")
            raise
    
    def extract_project_and_name(self, ad_name: str) -> tuple[str, str]:
        """
        広告名から案件名と動画名を抽出
        
        Args:
            ad_name: 広告名（例: "SBC_変わらない勇気"）
            
        Returns:
            (案件名, 動画名)のタプル
        """
        # プレフィックスで案件を判定
        if ad_name.startswith('NB_'):
            project = 'NB'
            video_name = ad_name[3:]  # "NB_"を除去
        elif ad_name.startswith('SBC_'):
            project = 'SBC'
            video_name = ad_name[4:]  # "SBC_"を除去
        elif ad_name.startswith('OM_'):
            project = 'OM'
            video_name = ad_name[3:]  # "OM_"を除去
        else:
            # プレフィックスがない場合
            project = '不明'
            video_name = ad_name
        
        return project, video_name
    
    def add_youtube_url(self, ad_name: str, youtube_url: str) -> bool:
        """
        YouTube URLをスプレッドシートに追加
        
        Args:
            ad_name: 広告名（プレフィックス付き）
            youtube_url: YouTube動画のURL
            
        Returns:
            成功時True
        """
        try:
            # スプレッドシートを開く
            spreadsheet = self.client.open_by_key(self.SPREADSHEET_ID)
            worksheet = spreadsheet.worksheet(self.SHEET_NAME)
            
            # 案件名と動画名を抽出
            project, video_name = self.extract_project_and_name(ad_name)
            
            # 新しい行を追加
            # A列: 案件名、B列: 動画名、C列: YouTube URL
            new_row = [project, video_name, youtube_url]
            
            # 最初の空の行を探す
            all_values = worksheet.get_all_values()
            
            # ヘッダー行をスキップして、最初の空の行を見つける
            empty_row_index = None
            for i, row in enumerate(all_values[1:], start=2):  # 2行目から開始
                # A列が空の行を探す
                if not row[0] or row[0] == '':
                    empty_row_index = i
                    break
            
            if empty_row_index:
                # 空の行が見つかった場合、その行を更新
                worksheet.update(f'A{empty_row_index}:C{empty_row_index}', [new_row])
                logger.info(f"行{empty_row_index}に記録: {project} / {video_name}")
            else:
                # 空の行がない場合は最後に追加
                worksheet.append_row(new_row)
                logger.info(f"最終行に追加: {project} / {video_name}")
            
            logger.info(f"YouTube URL記録完了: {project} / {video_name} -> {youtube_url}")
            
            # プルダウンの値と一致させる（既存のプルダウンオプションに合わせて調整）
            # 注: Google Sheetsのプルダウンは事前に設定されているため、
            # ここでは文字列として値を入力します。
            # 実際のプルダウンの選択肢と一致する必要があります。
            
            return True
            
        except Exception as e:
            logger.error(f"YouTube URL記録エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_all_urls(self) -> list:
        """
        記録されている全URLを取得（デバッグ用）
        
        Returns:
            URLのリスト
        """
        try:
            spreadsheet = self.client.open_by_key(self.SPREADSHEET_ID)
            worksheet = spreadsheet.worksheet(self.SHEET_NAME)
            
            # 全データを取得（ヘッダーも含む）
            all_values = worksheet.get_all_values()
            
            if not all_values:
                return []
            
            # ヘッダーを確認
            headers = all_values[0] if all_values else []
            print(f"ヘッダー: {headers}")
            
            # 全レコードを取得
            records = worksheet.get_all_records()
            
            return records
            
        except Exception as e:
            logger.error(f"URL取得エラー: {e}")
            return []


# テスト用
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # ロガーを初期化
    url_logger = YouTubeURLLogger()
    
    # テストデータ
    test_data = [
        ("NB_春のキャンペーン", "https://youtube.com/watch?v=test_nb_001"),
        ("SBC_変わらない勇気", "https://youtube.com/watch?v=test_sbc_001"),
        ("OM_新商品PR", "https://youtube.com/watch?v=test_om_001")
    ]
    
    print("=" * 60)
    print("YouTube URL記録テスト")
    print("=" * 60)
    
    for ad_name, url in test_data:
        print(f"\n記録中: {ad_name}")
        success = url_logger.add_youtube_url(ad_name, url)
        if success:
            print("  ✅ 成功")
        else:
            print("  ❌ 失敗")
    
    print("\n" + "=" * 60)
    print("記録完了")
    print("=" * 60)