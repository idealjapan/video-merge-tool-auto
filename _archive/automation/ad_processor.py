#!/usr/bin/env python3
import os
import sys
import logging
import tempfile
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional

# 親ディレクトリをパスに追加（既存モジュールをインポートするため）
sys.path.append(str(Path(__file__).parent.parent))

from video_merger_auto_bg import VideoMergerWithAutoBG
from automation.sheets_manager import SheetsManager
from automation.youtube_uploader import YouTubeUploader
from automation.google_ads_connector import GoogleAdsConnector
from automation.simple_queue_manager import SimpleQueueManager
from automation.config import (
    VIDEO_TEMP_DIR,
    OUTPUT_DIR,
    LOG_DIR,
    LOG_LEVEL,
    LOG_FORMAT,
    DEFAULT_BACKGROUND_STYLE,
    MAX_PROCESSING_TIME
)

# ログ設定
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_DIR / f"ad_processor_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdProcessor:
    """広告動画処理のメインクラス"""
    
    def __init__(self):
        self.sheets_manager = SheetsManager()
        self.youtube_uploader = YouTubeUploader()
        self.video_merger = VideoMergerWithAutoBG()
        self.google_ads_connector = GoogleAdsConnector()
        self.queue_manager = SimpleQueueManager()
        
        # 作業ディレクトリの準備
        VIDEO_TEMP_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)
    
    def get_video_file(self, ad_name: str) -> Optional[str]:
        """
        広告名から動画ファイルを取得
        
        Args:
            ad_name: 広告名
            
        Returns:
            str: 動画ファイルのパス
        """
        try:
            # VideoFinderを使って動画を検索
            from automation.video_finder import VideoFinder
            finder = VideoFinder()
            
            video_path = finder.find_video(ad_name)
            if video_path:
                logger.info(f"動画ファイル取得: {video_path}")
                return str(video_path)
            else:
                logger.error(f"動画ファイルが見つかりません: {ad_name}")
                return None
            
        except Exception as e:
            logger.error(f"動画取得エラー: {e}")
            return None
    
    def process_single_ad(self, ad_info: dict) -> bool:
        """
        単一の広告を処理
        
        Args:
            ad_info: 広告情報
            
        Returns:
            bool: 処理成功時True
        """
        ad_name = ad_info['ad_name']
        logger.info(f"=" * 50)
        logger.info(f"広告処理開始: {ad_name}")
        
        try:
            # 1. Google Driveから動画を取得（広告名で検索）
            from automation.google_drive_finder import GoogleDriveFinder
            drive_finder = GoogleDriveFinder()
            video_path = drive_finder.find_and_download(ad_name)
            
            if not video_path:
                logger.error(f"Google Driveに動画が見つかりません: {ad_name}")
                self.sheets_manager.add_error_log(ad_name, "動画ファイルが見つかりません")
                return False
            
            video_path = str(video_path)
            is_temp_file = True  # 後で削除するフラグ
            
            # 2. 背景スタイルを取得（オプション：スプレッドシートから）
            video_info = self.sheets_manager.get_video_info(ad_name)
            if video_info:
                background_style = video_info.get('background_style', DEFAULT_BACKGROUND_STYLE)
                title = video_info.get('title', ad_name)
            else:
                # デフォルト値を使用
                background_style = DEFAULT_BACKGROUND_STYLE
                title = ad_name
            
            # 動画ファイルが存在しない場合はエラー
            if not Path(video_path).exists():
                self.sheets_manager.add_error_log(ad_name, "動画ダウンロード失敗")
                return False
            
            # 3. 背景合成処理
            logger.info(f"背景合成開始: {ad_name}")
            output_filename = f"{ad_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            output_path = OUTPUT_DIR / output_filename
            
            try:
                # 動画情報を取得して背景を生成
                main_info = self.video_merger.get_video_info(str(video_path))
                bg_video = self.video_merger.generate_background_with_replicate(
                    orientation=main_info['orientation'],
                    duration=main_info['duration'],
                    style=background_style
                )
                
                if bg_video:
                    # 背景と合成
                    self.video_merger.merge_videos(
                        main_video=str(video_path),
                        background_video=bg_video,
                        output_video=str(output_path),
                        disclaimer_text="この動画は自動生成された背景を使用しています"
                    )
                logger.info(f"背景合成完了: {output_path}")
            except Exception as e:
                logger.error(f"背景合成エラー: {e}")
                self.sheets_manager.add_error_log(ad_name, f"背景合成エラー: {str(e)}")
                return False
            
            # 4. YouTubeにアップロード
            logger.info(f"YouTubeアップロード開始: {ad_name}")
            upload_title = title + " - 背景合成版"
            description = f"""
{ad_name} の背景合成版動画です。

キャンペーン: {ad_info.get('campaign', '')}
処理日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

自動生成された動画です。
            """.strip()
            
            youtube_url = self.youtube_uploader.upload_video(
                video_path=str(output_path),
                title=upload_title,
                description=description,
                tags=['広告', '背景合成', ad_info.get('campaign', ''), ad_name]
            )
            
            if not youtube_url:
                logger.error(f"YouTubeアップロード失敗: {ad_name}")
                self.sheets_manager.add_error_log(ad_name, "YouTubeアップロード失敗")
                return False
            
            # 5. スプレッドシートを更新
            self.sheets_manager.update_processed_status(
                ad_name=ad_name,
                row=ad_info['row'],
                youtube_url=youtube_url
            )
            
            # 6. YouTube URLを専用スプレッドシートに記録
            try:
                from automation.youtube_url_logger import YouTubeURLLogger
                url_logger = YouTubeURLLogger()
                url_logger.add_youtube_url(ad_name, youtube_url)
                logger.info(f"YouTube URL記録完了: {ad_name}")
            except Exception as e:
                logger.warning(f"YouTube URL記録エラー（処理は継続）: {e}")
            
            # 7. Google Ads差し替えキューに追加（安定性重視の新方式）
            try:
                # プロジェクト名（案件名）を取得
                project_name = ad_info.get('campaign', ad_info.get('project_name', ''))
                
                if project_name:
                    logger.info(f"Google Ads差し替えキューに追加: {ad_name}")
                    
                    # キューに追加
                    process_id = self.queue_manager.add_to_queue(
                        video_url=youtube_url,
                        project_name=project_name,
                        ad_name=ad_name,
                        video_name=ad_info.get('video_name', ad_name),
                        metadata={
                            'background_style': background_style,
                            'upload_date': datetime.now().isoformat(),
                            'title': title,
                            'original_row': ad_info.get('row', '')
                        }
                    )
                    
                    logger.info(f"キュー登録完了 - 処理ID: {process_id}")
                    logger.info("※Google Ads側で定期的に処理されます（約5分以内）")
                else:
                    logger.warning("プロジェクト名が取得できないため、Google Ads連携をスキップ")
                        
            except Exception as e:
                logger.error(f"キュー追加エラー（処理は継続）: {e}")
            
            logger.info(f"処理完了: {ad_name} -> {youtube_url}")
            
            # 6. 一時ファイルを削除（URLからダウンロードした場合）
            if 'is_temp_file' in locals() and is_temp_file and os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"一時ファイル削除: {video_path}")
            
            # 処理済み動画を削除してストレージ節約
            if os.path.exists(output_path):
                os.remove(output_path)
                logger.info(f"処理済み動画を削除: {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"予期しないエラー: {ad_name} - {e}")
            self.sheets_manager.add_error_log(ad_name, f"システムエラー: {str(e)}")
            return False
    
    def run(self):
        """メイン処理を実行"""
        logger.info("広告処理バッチ開始")
        
        try:
            # APIクォータ確認
            quota_status = self.youtube_uploader.get_upload_quota_status()
            if quota_status['status'] == 'ERROR':
                logger.warning(f"YouTube API警告: {quota_status['message']}")
            
            # 不承認広告を取得
            disapproved_ads = self.sheets_manager.get_disapproved_ads()
            
            if not disapproved_ads:
                logger.info("処理対象の不承認広告はありません")
                return
            
            # 各広告を処理
            success_count = 0
            error_count = 0
            
            for ad_info in disapproved_ads:
                try:
                    if self.process_single_ad(ad_info):
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    logger.error(f"広告処理エラー: {ad_info['ad_name']} - {e}")
                    error_count += 1
            
            # 結果サマリー
            logger.info("=" * 50)
            logger.info(f"処理完了 - 成功: {success_count}, エラー: {error_count}")
            
        except Exception as e:
            logger.error(f"バッチ処理エラー: {e}")
            raise


def main():
    """エントリーポイント"""
    processor = AdProcessor()
    processor.run()


if __name__ == "__main__":
    main()