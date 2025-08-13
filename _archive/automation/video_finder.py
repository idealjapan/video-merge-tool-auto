"""
シンプルな動画ファイル検索モジュール
命名規則: 広告名.mp4
"""
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 動画保存ディレクトリ（EC2の場合）
VIDEO_STORAGE_DIR = Path("/home/ec2-user/ad-videos")
# ローカルテスト用
LOCAL_VIDEO_DIR = Path(__file__).parent.parent / "ad-videos"


class VideoFinder:
    """広告名から動画ファイルを見つけるシンプルなクラス"""
    
    def __init__(self, video_dir: Path = None):
        if video_dir:
            self.video_dir = video_dir
        elif VIDEO_STORAGE_DIR.exists():
            self.video_dir = VIDEO_STORAGE_DIR
        else:
            self.video_dir = LOCAL_VIDEO_DIR
            
        # ディレクトリがなければ作成
        self.video_dir.mkdir(exist_ok=True)
        logger.info(f"動画ディレクトリ: {self.video_dir}")
    
    def find_video(self, ad_name: str) -> Optional[Path]:
        """
        広告名から動画ファイルを検索
        
        Args:
            ad_name: 広告名
            
        Returns:
            Path: 動画ファイルのパス、見つからない場合はNone
        """
        # 1. 完全一致を試す（拡張子違いも含む）
        for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
            video_path = self.video_dir / f"{ad_name}{ext}"
            if video_path.exists():
                logger.info(f"動画ファイル発見: {video_path}")
                return video_path
        
        # 2. 部分一致を試す（広告名が含まれるファイル）
        for video_file in self.video_dir.glob("*"):
            if video_file.is_file() and ad_name in video_file.stem:
                logger.info(f"動画ファイル発見（部分一致）: {video_file}")
                return video_file
        
        # 3. スペースやアンダースコアの違いを吸収
        normalized_name = ad_name.replace(' ', '_')
        for ext in ['.mp4', '.mov', '.avi']:
            video_path = self.video_dir / f"{normalized_name}{ext}"
            if video_path.exists():
                logger.info(f"動画ファイル発見（正規化）: {video_path}")
                return video_path
        
        logger.warning(f"動画ファイルが見つかりません: {ad_name}")
        return None
    
    def list_videos(self) -> list:
        """
        利用可能な動画ファイル一覧を取得
        
        Returns:
            list: 動画ファイルのリスト
        """
        videos = []
        for video_file in self.video_dir.glob("*"):
            if video_file.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                videos.append({
                    'name': video_file.stem,
                    'file': video_file.name,
                    'size': video_file.stat().st_size / (1024*1024),  # MB
                    'path': str(video_file)
                })
        
        return sorted(videos, key=lambda x: x['name'])
    
    def add_video(self, source_path: Path, ad_name: str) -> bool:
        """
        動画ファイルを追加（コピー）
        
        Args:
            source_path: コピー元の動画ファイル
            ad_name: 広告名（ファイル名になる）
            
        Returns:
            bool: 成功時True
        """
        try:
            source = Path(source_path)
            if not source.exists():
                logger.error(f"ソースファイルが存在しません: {source}")
                return False
            
            # 拡張子を保持
            ext = source.suffix
            dest = self.video_dir / f"{ad_name}{ext}"
            
            # コピー実行
            import shutil
            shutil.copy2(source, dest)
            logger.info(f"動画ファイルを追加: {dest}")
            return True
            
        except Exception as e:
            logger.error(f"動画追加エラー: {e}")
            return False


# 使用例
if __name__ == "__main__":
    finder = VideoFinder()
    
    # 動画を検索
    video = finder.find_video("広告A")
    if video:
        print(f"Found: {video}")
    
    # 一覧表示
    videos = finder.list_videos()
    for v in videos:
        print(f"{v['name']}: {v['size']:.1f}MB")