#!/usr/bin/env python3
"""
シンプルなキュー管理システム
既存のスプレッドシートにキューシートを追加して使用
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


class SimpleQueueManager:
    """広告差し替えキューの簡潔な管理クラス"""
    
    # 既存のスプレッドシートを使用
    SPREADSHEET_ID = "1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U"
    QUEUE_SHEET_NAME = "広告キュー"  # GASと統一
    
    def __init__(self):
        """初期化"""
        self.client = None
        self.spreadsheet = None
        self.queue_sheet = None
        self._init_connection()
    
    def _init_connection(self):
        """スプレッドシート接続を初期化"""
        try:
            # 認証設定
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            
            # 認証ファイルのパスを探す
            service_account_file = None
            possible_paths = [
                os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
                'credentials.json',
                'automation/credentials.json',
                '../credentials.json'
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    service_account_file = path
                    break
            
            if not service_account_file:
                raise FileNotFoundError("認証ファイルが見つかりません")
            
            creds = Credentials.from_service_account_file(
                service_account_file, 
                scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.SPREADSHEET_ID)
            
            # キューシートを確認/作成
            self._ensure_queue_sheet()
            
            logger.info("キューシート接続成功")
            
        except Exception as e:
            logger.error(f"接続エラー: {e}")
            raise
    
    def _ensure_queue_sheet(self):
        """キューシートが存在することを確認"""
        try:
            self.queue_sheet = self.spreadsheet.worksheet(self.QUEUE_SHEET_NAME)
            logger.info(f"既存のキューシートを使用: {self.QUEUE_SHEET_NAME}")
        except gspread.WorksheetNotFound:
            # シートが存在しない場合は作成
            self.queue_sheet = self.spreadsheet.add_worksheet(
                title=self.QUEUE_SHEET_NAME,
                rows=1000,
                cols=15
            )
            
            # ヘッダー行を追加
            headers = [
                '処理ID',          # A列
                'ステータス',      # B列: pending/processing/completed/failed
                '追加日時',        # C列
                '処理開始日時',    # D列
                '完了日時',        # E列
                '動画URL',         # F列
                '案件名',          # G列
                '広告名',          # H列
                '動画名',          # I列
                '広告グループ名',  # J列（NEW）
                'アカウントID',    # K列（NEW）
                'リトライ回数',    # L列
                'エラーメッセージ', # M列
                '処理結果',        # N列
                '新広告ID',        # O列
                '処理時間(秒)',    # P列
                'メタデータ'       # Q列
            ]
            self.queue_sheet.update('A1:Q1', [headers])
            
            # 見やすくするために書式設定
            self.queue_sheet.format('A1:Q1', {
                "backgroundColor": {"red": 0.2, "green": 0.5, "blue": 0.8},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })
            
            logger.info(f"新規キューシート作成: {self.QUEUE_SHEET_NAME}")
    
    def add_to_queue(
        self,
        video_url: str,
        project_name: str,
        ad_name: str,
        video_name: Optional[str] = None,
        ad_group_name: Optional[str] = None,
        account_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        キューに新しいタスクを追加
        
        Args:
            video_url: YouTube動画URL
            project_name: 案件名
            ad_name: 広告名
            video_name: 動画名（オプション）
            metadata: メタデータ（オプション）
            
        Returns:
            str: 処理ID
        """
        try:
            # 処理IDを生成（タイムスタンプベース）
            process_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ad_name[:20].replace(' ', '_')}"
            
            # 新しい行のデータ（ヘッダーに合わせて修正）
            new_row = [
                process_id,                       # A列: 処理ID
                '待機中',                         # B列: ステータス
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # C列: 作成日時
                '',                               # D列: 処理開始日時
                '',                               # E列: 完了日時
                video_url,                        # F列: 動画URL
                project_name,                     # G列: 案件名
                ad_name,                          # H列: 広告名
                video_name or ad_name,            # I列: 動画名
                0,                                # J列: リトライ回数
                '',                               # K列: エラーメッセージ
                '',                               # L列: 処理結果
                '',                               # M列: 新広告ID
                '',                               # N列: 処理時間(秒)
                json.dumps(metadata or {}, ensure_ascii=False),  # O列: メタデータ
                ad_group_name or '',              # P列: 広告グループ名
                account_id or ''                  # Q列: アカウントID
            ]
            
            # キューに追加
            self.queue_sheet.append_row(new_row)
            
            logger.info(f"キューに追加: {process_id}")
            logger.info(f"  案件: {project_name}")
            logger.info(f"  広告: {ad_name}")
            logger.info(f"  URL: {video_url}")
            
            return process_id
            
        except Exception as e:
            logger.error(f"キュー追加エラー: {e}")
            raise
    
    def get_queue_status(self) -> Dict[str, int]:
        """
        キューの状態を取得
        
        Returns:
            dict: ステータスごとのタスク数
        """
        try:
            all_values = self.queue_sheet.get_all_values()
            
            if len(all_values) <= 1:
                return {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0}
            
            status_count = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0}
            
            for row in all_values[1:]:  # ヘッダー行をスキップ
                if len(row) >= 2 and row[1] in status_count:
                    status_count[row[1]] += 1
            
            return status_count
            
        except Exception as e:
            logger.error(f"ステータス取得エラー: {e}")
            return {}


# テスト用関数
def test_queue():
    """キューのテスト"""
    try:
        queue = SimpleQueueManager()
        
        # テストデータを追加
        process_id = queue.add_to_queue(
            video_url="https://www.youtube.com/watch?v=test123",
            project_name="テスト案件",
            ad_name="テスト広告_001",
            metadata={"test": True, "background_style": "style1"}
        )
        
        print(f"✅ キューに追加成功: {process_id}")
        
        # ステータス確認
        status = queue.get_queue_status()
        print(f"📊 キューステータス: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # テスト実行
    test_queue()