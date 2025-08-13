#!/usr/bin/env python3
"""
シンプルなYouTubeアップローダー
1つのチャンネルに全てアップロード
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class SimpleYouTubeUploader:
    """シンプルなYouTubeアップローダー"""
    
    def __init__(self):
        """初期化"""
        self.token_path = Path("credentials/youtube_token.pickle")
        self.youtube = None
        self._init_youtube()
    
    def _init_youtube(self):
        """YouTube APIを初期化"""
        if not self.token_path.exists():
            raise FileNotFoundError(
                "認証が必要です。python3 simple_youtube_setup.py を実行してください"
            )
        
        try:
            # トークンを読み込み
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
            
            # 期限切れなら更新
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    with open(self.token_path, 'wb') as token:
                        pickle.dump(creds, token)
            
            # YouTube APIを構築
            self.youtube = build('youtube', 'v3', credentials=creds)
            logger.info("YouTube API初期化完了")
            
        except Exception as e:
            logger.error(f"YouTube API初期化エラー: {e}")
            raise
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: Optional[list] = None,
        category_id: str = "22"  # People & Blogs
    ) -> Optional[str]:
        """
        動画をアップロード
        
        Args:
            video_path: 動画ファイルのパス
            title: 動画タイトル
            description: 動画説明
            tags: タグリスト
            category_id: カテゴリID
            
        Returns:
            str: YouTube動画URL（成功時）、None（失敗時）
        """
        try:
            # ファイル確認
            if not Path(video_path).exists():
                logger.error(f"動画ファイルが見つかりません: {video_path}")
                return None
            
            # メタデータ設定
            body = {
                'snippet': {
                    'title': title,
                    'description': description or f"{title} - 自動アップロード",
                    'tags': tags or [title],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': 'unlisted'  # public, private, unlisted
                }
            }
            
            # メディアアップロード設定
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/*'
            )
            
            # アップロード実行
            logger.info(f"アップロード開始: {title}")
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    if progress % 20 == 0:  # 20%ごとに表示
                        logger.info(f"アップロード進捗: {progress}%")
            
            # 成功
            video_id = response.get('id')
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"✅ アップロード完了: {video_url}")
            return video_url
            
        except HttpError as e:
            logger.error(f"YouTube APIエラー: {e}")
            return None
        except Exception as e:
            logger.error(f"アップロードエラー: {e}")
            return None


# テスト用
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # テスト動画を作成
    test_video = "test_upload.mp4"
    if not Path(test_video).exists():
        print(f"テスト動画 {test_video} を用意してください")
    else:
        uploader = SimpleYouTubeUploader()
        url = uploader.upload_video(
            video_path=test_video,
            title="テストアップロード",
            description="これはテストです"
        )
        
        if url:
            print(f"✅ 成功: {url}")
        else:
            print("❌ 失敗")