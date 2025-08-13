"""
Google Driveから広告名で動画を検索・ダウンロード
"""
import os
import io
import logging
import tempfile
from pathlib import Path
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

logger = logging.getLogger(__name__)


class GoogleDriveFinder:
    """Google Driveから動画を検索・取得"""
    
    def __init__(self, credentials_file: str = None, folder_id: str = None):
        """
        Args:
            credentials_file: サービスアカウントのJSONファイル
            folder_id: 検索対象のフォルダID（省略可能）
        """
        if credentials_file is None:
            credentials_file = str(Path(__file__).parent.parent / "credentials" / "google_service_account.json")
        
        # デフォルトのフォルダIDを設定
        if folder_id is None:
            folder_id = "1GQSw_hQEsTCKAjtt9FyVmZryVUXsbyLL"
        
        self.folder_id = folder_id  # 特定フォルダに限定する場合
        self.service = self._init_service(credentials_file)
        self.temp_dir = Path(tempfile.gettempdir()) / "ad_videos_temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    def _init_service(self, credentials_file: str):
        """Google Drive APIサービスを初期化"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive API初期化成功")
            return service
        except Exception as e:
            logger.error(f"Google Drive API初期化エラー: {e}")
            raise
    
    def find_and_download(self, ad_name: str) -> Optional[Path]:
        """
        広告名で動画を検索してダウンロード
        
        Args:
            ad_name: 広告名
            
        Returns:
            Path: ダウンロードした動画ファイルのパス
        """
        try:
            # 1. ファイルを検索
            query_parts = [
                f"name contains '{ad_name}'",
                "mimeType contains 'video/'"
            ]
            
            if self.folder_id:
                query_parts.append(f"'{self.folder_id}' in parents")
            
            query = " and ".join(query_parts)
            
            logger.info(f"Google Driveで検索: {ad_name}")
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)",
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                logger.warning(f"動画が見つかりません: {ad_name}")
                return None
            
            # 最初に見つかったファイルを使用
            file_info = files[0]
            logger.info(f"動画ファイル発見: {file_info['name']}")
            
            # 2. ファイルをダウンロード
            return self._download_file(file_info['id'], file_info['name'], ad_name)
            
        except Exception as e:
            logger.error(f"検索・ダウンロードエラー: {e}")
            return None
    
    def _download_file(self, file_id: str, file_name: str, ad_name: str) -> Optional[Path]:
        """
        ファイルIDから動画をダウンロード
        
        Args:
            file_id: Google DriveのファイルID
            file_name: オリジナルのファイル名
            ad_name: 広告名
            
        Returns:
            Path: ダウンロードしたファイルのパス
        """
        try:
            # 拡張子を取得
            ext = Path(file_name).suffix or '.mp4'
            output_path = self.temp_dir / f"{ad_name}{ext}"
            
            # ダウンロード実行
            request = self.service.files().get_media(fileId=file_id)
            
            with open(output_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        if progress % 20 == 0:
                            logger.info(f"ダウンロード進捗: {progress}%")
            
            logger.info(f"ダウンロード完了: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"ダウンロードエラー: {e}")
            return None
    
    def list_videos(self, limit: int = 100):
        """
        利用可能な動画一覧を取得
        
        Args:
            limit: 取得する最大数
            
        Returns:
            list: 動画ファイルのリスト
        """
        try:
            query_parts = ["mimeType contains 'video/'"]
            
            if self.folder_id:
                query_parts.append(f"'{self.folder_id}' in parents")
            
            query = " and ".join(query_parts)
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, size)",
                pageSize=limit
            ).execute()
            
            files = results.get('files', [])
            
            video_list = []
            for file in files:
                video_list.append({
                    'id': file['id'],
                    'name': file['name'],
                    'size_mb': int(file.get('size', 0)) / (1024 * 1024)
                })
            
            return video_list
            
        except Exception as e:
            logger.error(f"リスト取得エラー: {e}")
            return []


# 使用例
if __name__ == "__main__":
    finder = GoogleDriveFinder()
    
    # 動画を検索してダウンロード
    video_path = finder.find_and_download("広告A")
    if video_path:
        print(f"Downloaded: {video_path}")
    
    # 動画一覧
    videos = finder.list_videos()
    for v in videos:
        print(f"{v['name']}: {v['size_mb']:.1f}MB")