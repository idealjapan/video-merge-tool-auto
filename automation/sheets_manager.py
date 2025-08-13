import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging
from typing import List, Dict, Optional
from .config import (
    GOOGLE_SERVICE_ACCOUNT_FILE,
    SPREADSHEET_NAME,
    SPREADSHEET_ID,
    DISAPPROVED_SHEET_NAME,
    STOCK_SHEET_NAME
)

logger = logging.getLogger(__name__)


class SheetsManager:
    """Google Sheetsとの連携を管理するクラス"""
    
    def __init__(self):
        self.client = self._authenticate()
        self.spreadsheet = self._open_spreadsheet()
        
    def _authenticate(self) -> gspread.Client:
        """Google Sheets APIの認証"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                str(GOOGLE_SERVICE_ACCOUNT_FILE),
                scopes=scopes
            )
            
            client = gspread.authorize(credentials)
            logger.info("Google Sheets認証成功")
            return client
        except Exception as e:
            logger.error(f"Google Sheets認証エラー: {e}")
            raise
    
    def _open_spreadsheet(self):
        """スプレッドシートを開く"""
        try:
            # SPREADSHEET_IDがあればIDで開く（より確実）
            if SPREADSHEET_ID:
                spreadsheet = self.client.open_by_key(SPREADSHEET_ID)
                logger.info(f"スプレッドシート ID: {SPREADSHEET_ID} を開きました")
            else:
                spreadsheet = self.client.open(SPREADSHEET_NAME)
                logger.info(f"スプレッドシート '{SPREADSHEET_NAME}' を開きました")
            return spreadsheet
        except gspread.SpreadsheetNotFound:
            logger.error(f"スプレッドシート '{SPREADSHEET_NAME}' (ID: {SPREADSHEET_ID}) が見つかりません")
            raise
    
    def get_disapproved_ads(self) -> List[Dict]:
        """
        不承認広告のリストを取得
        
        Returns:
            List[Dict]: 不承認広告のリスト
            例: [{'ad_name': '広告A', 'status': '不承認', 'processed': False, 'row': 2}]
        """
        try:
            sheet = self.spreadsheet.worksheet(DISAPPROVED_SHEET_NAME)
            records = sheet.get_all_records()
            
            disapproved = []
            for idx, record in enumerate(records, start=2):  # ヘッダー行をスキップ
                if record.get('ステータス') == '不承認' and not record.get('処理済み'):
                    disapproved.append({
                        'ad_name': record.get('広告名'),
                        'campaign': record.get('キャンペーン', ''),
                        'reason': record.get('不承認理由', ''),
                        'row': idx
                    })
            
            logger.info(f"{len(disapproved)}件の不承認広告を検出")
            return disapproved
            
        except Exception as e:
            logger.error(f"不承認広告の取得エラー: {e}")
            return []
    
    def get_video_info(self, ad_name: str) -> Optional[Dict]:
        """
        動画ストックシートから動画情報を取得
        
        Args:
            ad_name: 広告名
            
        Returns:
            Dict: 動画情報 {'video_url': 'xxx', 'background_style': 'nature'}
        """
        try:
            sheet = self.spreadsheet.worksheet(STOCK_SHEET_NAME)
            records = sheet.get_all_records()
            
            for record in records:
                if record.get('広告名') == ad_name:
                    return {
                        'video_url': record.get('元動画URL'),
                        'background_style': record.get('背景スタイル', 'nature'),
                        'title': record.get('タイトル', ad_name)
                    }
            
            logger.warning(f"広告 '{ad_name}' の動画情報が見つかりません")
            return None
            
        except Exception as e:
            logger.error(f"動画情報の取得エラー: {e}")
            return None
    
    def update_processed_status(self, ad_name: str, row: int, youtube_url: str):
        """
        処理済みステータスを更新
        
        Args:
            ad_name: 広告名
            row: 更新する行番号
            youtube_url: アップロードされたYouTube URL
        """
        try:
            # 処理時刻
            process_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 不承認広告シートを更新
            disapproved_sheet = self.spreadsheet.worksheet(DISAPPROVED_SHEET_NAME)
            disapproved_sheet.update(f'D{row}', 'TRUE')  # 処理済みフラグ
            disapproved_sheet.update(f'E{row}', process_time)  # 処理日時
            
            # 動画ストックシートを更新
            stock_sheet = self.spreadsheet.worksheet(STOCK_SHEET_NAME)
            records = stock_sheet.get_all_records()
            
            for idx, record in enumerate(records, start=2):
                if record.get('広告名') == ad_name:
                    stock_sheet.update(f'D{idx}', youtube_url)  # 合成済みURL列
                    stock_sheet.update(f'E{idx}', process_time)
                    break
            
            # 処理履歴を記録
            self.add_process_history(ad_name, youtube_url, process_time)
            
            logger.info(f"広告 '{ad_name}' の処理ステータスを更新しました")
            
        except Exception as e:
            logger.error(f"ステータス更新エラー: {e}")
    
    def add_process_history(self, ad_name: str, youtube_url: str, process_time: str):
        """
        処理履歴を専用シートに記録
        
        Args:
            ad_name: 広告名
            youtube_url: YouTube URL
            process_time: 処理時刻
        """
        try:
            # 処理履歴シートがなければ作成
            try:
                history_sheet = self.spreadsheet.worksheet("処理履歴")
            except gspread.WorksheetNotFound:
                history_sheet = self.spreadsheet.add_worksheet(
                    title="処理履歴",
                    rows=10000,
                    cols=8
                )
                history_sheet.update('A1:H1', [[
                    '処理日時', '広告名', 'キャンペーン', 'チャンネル',
                    'YouTube URL', '背景スタイル', 'ステータス', '備考'
                ]])
            
            # プレフィックスからチャンネルを判定
            channel = 'unknown'
            if ad_name.startswith('NB_'):
                channel = 'NBチャンネル'
            elif ad_name.startswith('SBC_'):
                channel = 'SBCチャンネル'
            elif ad_name.startswith('OM_'):
                channel = 'OMチャンネル'
            
            # 履歴を追加
            history_sheet.append_row([
                process_time,
                ad_name,
                '',  # キャンペーン（必要に応じて取得）
                channel,
                youtube_url,
                'AI自動生成',
                '処理完了',
                '自動処理'
            ])
            
            logger.info(f"処理履歴を記録: {ad_name}")
            
        except Exception as e:
            logger.error(f"処理履歴記録エラー: {e}")
    
    def add_error_log(self, ad_name: str, error_message: str):
        """
        エラーログをシートに追加
        
        Args:
            ad_name: 広告名
            error_message: エラーメッセージ
        """
        try:
            # エラーログシートがなければ作成
            try:
                error_sheet = self.spreadsheet.worksheet("エラーログ")
            except gspread.WorksheetNotFound:
                error_sheet = self.spreadsheet.add_worksheet(
                    title="エラーログ",
                    rows=1000,
                    cols=5
                )
                error_sheet.update('A1:E1', [['日時', '広告名', 'エラー内容', 'ステータス', '備考']])
            
            # エラーログを追加
            error_sheet.append_row([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                ad_name,
                error_message[:500],  # 長すぎる場合は切り詰め
                'エラー',
                ''
            ])
            
            logger.info(f"エラーログを記録: {ad_name}")
            
        except Exception as e:
            logger.error(f"エラーログ記録失敗: {e}")