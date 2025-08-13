#!/usr/bin/env python3
"""
Google Ads差し替えキュー管理システム
スプレッドシートをキューとして使用し、安定した非同期処理を実現
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


class AdsQueueManager:
    """Google Ads差し替えキューの管理クラス"""
    
    def __init__(self, spreadsheet_id: Optional[str] = None):
        """
        初期化
        
        Args:
            spreadsheet_id: キュー管理用スプレッドシートID
        """
        self.spreadsheet_id = spreadsheet_id or os.getenv('ADS_QUEUE_SPREADSHEET_ID')
        self.queue_sheet_name = 'ads_queue'
        self.history_sheet_name = 'processing_history'
        self.client = None
        self.spreadsheet = None
        
        if self.spreadsheet_id:
            self._init_sheets()
    
    def _init_sheets(self):
        """スプレッドシート接続を初期化"""
        try:
            # 認証設定
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            
            # サービスアカウントキーのパスを環境変数から取得
            service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not service_account_file:
                service_account_file = 'credentials.json'
            
            creds = Credentials.from_service_account_file(
                service_account_file, 
                scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            # キューシートの初期化
            self._ensure_queue_sheet()
            self._ensure_history_sheet()
            
            logger.info("キュー管理スプレッドシート接続成功")
            
        except Exception as e:
            logger.error(f"スプレッドシート初期化エラー: {e}")
            raise
    
    def _ensure_queue_sheet(self):
        """キューシートが存在することを確認"""
        try:
            self.queue_sheet = self.spreadsheet.worksheet(self.queue_sheet_name)
        except gspread.WorksheetNotFound:
            # シートが存在しない場合は作成
            self.queue_sheet = self.spreadsheet.add_worksheet(
                title=self.queue_sheet_name,
                rows=1000,
                cols=20
            )
            # ヘッダー行を追加
            headers = [
                'queue_id',
                'status',
                'priority',
                'created_at',
                'updated_at',
                'video_url',
                'project_name',
                'ad_name',
                'video_name',
                'metadata',
                'retry_count',
                'last_error',
                'processed_at',
                'result'
            ]
            self.queue_sheet.update('A1:N1', [headers])
            logger.info(f"キューシート作成: {self.queue_sheet_name}")
    
    def _ensure_history_sheet(self):
        """履歴シートが存在することを確認"""
        try:
            self.history_sheet = self.spreadsheet.worksheet(self.history_sheet_name)
        except gspread.WorksheetNotFound:
            # シートが存在しない場合は作成
            self.history_sheet = self.spreadsheet.add_worksheet(
                title=self.history_sheet_name,
                rows=10000,
                cols=20
            )
            # ヘッダー行を追加
            headers = [
                'process_id',
                'queue_id',
                'processed_at',
                'project_name',
                'ad_name',
                'video_url',
                'status',
                'result',
                'processing_time_sec',
                'error_message'
            ]
            self.history_sheet.update('A1:J1', [headers])
            logger.info(f"履歴シート作成: {self.history_sheet_name}")
    
    def add_to_queue(
        self,
        video_url: str,
        project_name: str,
        ad_name: str,
        video_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: int = 5
    ) -> str:
        """
        キューに新しいタスクを追加
        
        Args:
            video_url: YouTube動画URL
            project_name: 案件名
            ad_name: 広告名
            video_name: 動画名（オプション）
            metadata: メタデータ（オプション）
            priority: 優先度（1-10、1が最高）
            
        Returns:
            str: キューID
        """
        try:
            # キューIDを生成
            queue_id = f"q_{datetime.now().strftime('%Y%m%d%H%M%S')}_{ad_name[:10]}"
            
            # 新しい行のデータ
            new_row = [
                queue_id,
                'pending',  # status
                priority,
                datetime.now().isoformat(),  # created_at
                datetime.now().isoformat(),  # updated_at
                video_url,
                project_name,
                ad_name,
                video_name or ad_name,
                json.dumps(metadata or {}, ensure_ascii=False),
                0,  # retry_count
                '',  # last_error
                '',  # processed_at
                ''   # result
            ]
            
            # キューに追加
            self.queue_sheet.append_row(new_row)
            
            logger.info(f"キューに追加: {queue_id} - {ad_name}")
            return queue_id
            
        except Exception as e:
            logger.error(f"キュー追加エラー: {e}")
            raise
    
    def get_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        処理待ちタスクを取得
        
        Args:
            limit: 取得する最大数
            
        Returns:
            list: 処理待ちタスクのリスト
        """
        try:
            # 全データを取得
            all_values = self.queue_sheet.get_all_values()
            
            if len(all_values) <= 1:
                return []
            
            headers = all_values[0]
            pending_tasks = []
            
            # pending状態のタスクを抽出
            for row_idx, row in enumerate(all_values[1:], start=2):
                if len(row) >= 2 and row[1] == 'pending':
                    task = {
                        'row_number': row_idx,
                        'queue_id': row[0],
                        'status': row[1],
                        'priority': int(row[2]) if row[2] else 5,
                        'created_at': row[3],
                        'video_url': row[5],
                        'project_name': row[6],
                        'ad_name': row[7],
                        'video_name': row[8],
                        'metadata': json.loads(row[9]) if row[9] else {},
                        'retry_count': int(row[10]) if row[10] else 0
                    }
                    pending_tasks.append(task)
            
            # 優先度でソート（優先度が低い数値ほど高優先）
            pending_tasks.sort(key=lambda x: (x['priority'], x['created_at']))
            
            return pending_tasks[:limit]
            
        except Exception as e:
            logger.error(f"タスク取得エラー: {e}")
            return []
    
    def update_task_status(
        self,
        queue_id: str,
        status: str,
        result: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        タスクのステータスを更新
        
        Args:
            queue_id: キューID
            status: 新しいステータス（processing, completed, failed, retrying）
            result: 処理結果
            error: エラーメッセージ
        """
        try:
            # 該当行を検索
            all_values = self.queue_sheet.get_all_values()
            
            for row_idx, row in enumerate(all_values[1:], start=2):
                if row[0] == queue_id:
                    # ステータス更新
                    self.queue_sheet.update_cell(row_idx, 2, status)
                    self.queue_sheet.update_cell(row_idx, 5, datetime.now().isoformat())
                    
                    if status == 'completed':
                        self.queue_sheet.update_cell(row_idx, 13, datetime.now().isoformat())
                        if result:
                            self.queue_sheet.update_cell(row_idx, 14, result)
                    
                    if error:
                        self.queue_sheet.update_cell(row_idx, 12, error)
                        # リトライカウントを増やす
                        retry_count = int(row[10]) if row[10] else 0
                        self.queue_sheet.update_cell(row_idx, 11, retry_count + 1)
                    
                    logger.info(f"タスク更新: {queue_id} -> {status}")
                    break
                    
        except Exception as e:
            logger.error(f"ステータス更新エラー: {e}")
    
    def record_history(
        self,
        queue_id: str,
        project_name: str,
        ad_name: str,
        video_url: str,
        status: str,
        result: Optional[str] = None,
        error: Optional[str] = None,
        processing_time: Optional[float] = None
    ):
        """
        処理履歴を記録
        
        Args:
            queue_id: キューID
            project_name: 案件名
            ad_name: 広告名
            video_url: 動画URL
            status: 処理ステータス
            result: 処理結果
            error: エラーメッセージ
            processing_time: 処理時間（秒）
        """
        try:
            # 履歴IDを生成
            process_id = f"p_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 履歴データ
            history_row = [
                process_id,
                queue_id,
                datetime.now().isoformat(),
                project_name,
                ad_name,
                video_url,
                status,
                result or '',
                processing_time or 0,
                error or ''
            ]
            
            # 履歴に追加
            self.history_sheet.append_row(history_row)
            
            logger.info(f"履歴記録: {process_id} - {ad_name}")
            
        except Exception as e:
            logger.error(f"履歴記録エラー: {e}")
    
    def cleanup_old_tasks(self, days: int = 7):
        """
        古い完了タスクをクリーンアップ
        
        Args:
            days: 保持する日数
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            all_values = self.queue_sheet.get_all_values()
            rows_to_delete = []
            
            for row_idx, row in enumerate(all_values[1:], start=2):
                if row[1] in ['completed', 'failed']:
                    try:
                        processed_at = datetime.fromisoformat(row[12]) if row[12] else None
                        if processed_at and processed_at < cutoff_date:
                            rows_to_delete.append(row_idx)
                    except:
                        pass
            
            # 古い順（下から）削除
            for row_idx in reversed(rows_to_delete):
                self.queue_sheet.delete_rows(row_idx)
            
            if rows_to_delete:
                logger.info(f"{len(rows_to_delete)}件の古いタスクを削除")
                
        except Exception as e:
            logger.error(f"クリーンアップエラー: {e}")


# テスト実行
if __name__ == "__main__":
    # キューマネージャー初期化
    queue_manager = AdsQueueManager()
    
    # テストデータを追加
    queue_id = queue_manager.add_to_queue(
        video_url="https://www.youtube.com/watch?v=test123",
        project_name="テスト案件",
        ad_name="テスト広告",
        priority=1
    )
    
    print(f"キューに追加: {queue_id}")
    
    # 処理待ちタスクを取得
    pending_tasks = queue_manager.get_pending_tasks(limit=5)
    print(f"処理待ちタスク: {len(pending_tasks)}件")
    
    for task in pending_tasks:
        print(f"  - {task['queue_id']}: {task['ad_name']} (優先度: {task['priority']})")