"""
動画URLから動画をダウンロードするモジュール
Google Drive、Dropbox、直接URLに対応
"""
import os
import logging
import tempfile
import requests
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class VideoDownloader:
    """動画をURLからダウンロード"""
    
    def __init__(self, temp_dir: Path = None):
        if temp_dir:
            self.temp_dir = temp_dir
        else:
            self.temp_dir = Path(tempfile.gettempdir()) / "ad_videos_temp"
        
        self.temp_dir.mkdir(exist_ok=True)
        logger.info(f"一時ディレクトリ: {self.temp_dir}")
    
    def download_from_url(self, url: str, ad_name: str) -> Optional[Path]:
        """
        URLから動画をダウンロード
        
        Args:
            url: 動画のURL（Google Drive、Dropbox、直接URL）
            ad_name: 広告名（ファイル名に使用）
            
        Returns:
            Path: ダウンロードした動画ファイルのパス
        """
        try:
            # Google Driveの場合
            if 'drive.google.com' in url:
                return self._download_from_google_drive(url, ad_name)
            
            # Dropboxの場合
            elif 'dropbox.com' in url:
                return self._download_from_dropbox(url, ad_name)
            
            # その他の直接URL
            else:
                return self._download_direct(url, ad_name)
                
        except Exception as e:
            logger.error(f"ダウンロードエラー: {e}")
            return None
    
    def _download_from_google_drive(self, url: str, ad_name: str) -> Optional[Path]:
        """
        Google Driveからダウンロード
        """
        try:
            # Google DriveのURLからファイルIDを抽出
            if '/file/d/' in url:
                file_id = url.split('/file/d/')[1].split('/')[0]
            elif 'id=' in url:
                file_id = parse_qs(urlparse(url).query)['id'][0]
            else:
                raise ValueError(f"Invalid Google Drive URL: {url}")
            
            # ダウンロード用URL
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            logger.info(f"Google Driveからダウンロード: {file_id}")
            
            # ダウンロード実行
            response = requests.get(download_url, stream=True)
            
            # 大きいファイルの場合の確認画面を回避
            if 'download_warning' in response.headers.get('Set-Cookie', ''):
                params = {'id': file_id, 'confirm': 't'}
                response = requests.get(download_url, params=params, stream=True)
            
            # ファイルに保存
            output_path = self.temp_dir / f"{ad_name}.mp4"
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"ダウンロード完了: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Google Driveダウンロードエラー: {e}")
            return None
    
    def _download_from_dropbox(self, url: str, ad_name: str) -> Optional[Path]:
        """
        Dropboxからダウンロード
        """
        try:
            # Dropboxの共有URLを直接ダウンロードURLに変換
            if '?dl=0' in url:
                download_url = url.replace('?dl=0', '?dl=1')
            else:
                download_url = url + '?dl=1'
            
            logger.info(f"Dropboxからダウンロード: {download_url}")
            
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # ファイルに保存
            output_path = self.temp_dir / f"{ad_name}.mp4"
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"ダウンロード完了: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Dropboxダウンロードエラー: {e}")
            return None
    
    def _download_direct(self, url: str, ad_name: str) -> Optional[Path]:
        """
        直接URLからダウンロード
        """
        try:
            logger.info(f"直接URLからダウンロード: {url}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 拡張子を推定
            content_type = response.headers.get('content-type', '')
            if 'mp4' in content_type or url.endswith('.mp4'):
                ext = '.mp4'
            elif 'quicktime' in content_type or url.endswith('.mov'):
                ext = '.mov'
            else:
                ext = '.mp4'  # デフォルト
            
            # ファイルに保存
            output_path = self.temp_dir / f"{ad_name}{ext}"
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"ダウンロード完了: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"直接ダウンロードエラー: {e}")
            return None
    
    def cleanup_temp_files(self, keep_hours: int = 24):
        """
        古い一時ファイルを削除
        
        Args:
            keep_hours: 保持する時間（デフォルト24時間）
        """
        import time
        current_time = time.time()
        
        for file_path in self.temp_dir.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > keep_hours * 3600:
                    try:
                        file_path.unlink()
                        logger.info(f"古い一時ファイルを削除: {file_path}")
                    except Exception as e:
                        logger.error(f"ファイル削除エラー: {e}")


# 使用例
if __name__ == "__main__":
    downloader = VideoDownloader()
    
    # Google Driveからダウンロード
    video = downloader.download_from_url(
        "https://drive.google.com/file/d/xxx/view",
        "テスト広告"
    )
    
    if video:
        print(f"Downloaded: {video}")