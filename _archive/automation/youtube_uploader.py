import os
import pickle
import logging
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from .config import (
    YOUTUBE_CLIENT_SECRETS_FILE,
    YOUTUBE_CREDENTIALS_FILE,
    YOUTUBE_CATEGORY_ID,
    YOUTUBE_PRIVACY_STATUS
)

logger = logging.getLogger(__name__)


class YouTubeUploader:
    """YouTube動画アップロード管理クラス"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self):
        self.youtube = self._authenticate()
    
    def _authenticate(self):
        """YouTube API認証"""
        creds = None
        
        # 保存済みトークンがあれば読み込み
        if os.path.exists(YOUTUBE_CREDENTIALS_FILE):
            with open(YOUTUBE_CREDENTIALS_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # トークンがないか期限切れの場合は再認証
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(YOUTUBE_CLIENT_SECRETS_FILE),
                    self.SCOPES
                )
                creds = flow.run_local_server(port=8090)
            
            # トークンを保存
            os.makedirs(os.path.dirname(YOUTUBE_CREDENTIALS_FILE), exist_ok=True)
            with open(YOUTUBE_CREDENTIALS_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('youtube', 'v3', credentials=creds)
    
    def upload_video(self, 
                    video_path: str, 
                    title: str, 
                    description: str = "",
                    tags: list = None,
                    category_id: str = None) -> Optional[str]:
        """
        動画をYouTubeにアップロード
        
        Args:
            video_path: アップロードする動画ファイルのパス
            title: 動画タイトル
            description: 動画の説明
            tags: タグのリスト
            category_id: カテゴリID
            
        Returns:
            str: アップロードされた動画のURL、失敗時はNone
        """
        if not os.path.exists(video_path):
            logger.error(f"動画ファイルが存在しません: {video_path}")
            return None
        
        try:
            # メタデータ設定
            body = {
                'snippet': {
                    'title': title,
                    'description': description or f"{title} - 自動生成された背景付き広告動画",
                    'tags': tags or ['広告', '自動生成', '背景合成'],
                    'categoryId': category_id or YOUTUBE_CATEGORY_ID
                },
                'status': {
                    'privacyStatus': YOUTUBE_PRIVACY_STATUS,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # メディアアップロード設定
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024*1024  # 1MBずつアップロード
            )
            
            # アップロードリクエスト作成
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # アップロード実行（プログレス表示付き）
            response = None
            logger.info(f"動画のアップロード開始: {title}")
            
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    if progress % 20 == 0:  # 20%ごとにログ
                        logger.info(f"アップロード進捗: {progress}%")
            
            # 成功時はURLを返す
            video_id = response['id']
            video_url = f"https://youtube.com/watch?v={video_id}"
            
            logger.info(f"アップロード完了: {video_url}")
            return video_url
            
        except HttpError as e:
            logger.error(f"YouTube APIエラー: {e}")
            return None
        except Exception as e:
            logger.error(f"アップロードエラー: {e}")
            return None
    
    def update_video_metadata(self, video_id: str, title: str = None, 
                            description: str = None, tags: list = None) -> bool:
        """
        既存動画のメタデータを更新
        
        Args:
            video_id: 動画ID
            title: 新しいタイトル
            description: 新しい説明
            tags: 新しいタグ
            
        Returns:
            bool: 成功時True
        """
        try:
            # 現在の動画情報を取得
            video_response = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                logger.error(f"動画が見つかりません: {video_id}")
                return False
            
            snippet = video_response['items'][0]['snippet']
            
            # 更新する項目のみ変更
            if title:
                snippet['title'] = title
            if description:
                snippet['description'] = description
            if tags:
                snippet['tags'] = tags
            
            # 更新実行
            self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            ).execute()
            
            logger.info(f"動画メタデータ更新完了: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"メタデータ更新エラー: {e}")
            return False
    
    def get_upload_quota_status(self) -> dict:
        """
        YouTube APIのクォータ状況を確認（参考値）
        
        Returns:
            dict: クォータ情報
        """
        try:
            # チャンネル情報を取得してAPIが正常に動作しているか確認
            response = self.youtube.channels().list(
                part='statistics',
                mine=True
            ).execute()
            
            if response['items']:
                channel_stats = response['items'][0]['statistics']
                return {
                    'status': 'OK',
                    'video_count': channel_stats.get('videoCount', 0),
                    'message': 'API接続正常'
                }
            else:
                return {
                    'status': 'WARNING',
                    'message': 'チャンネル情報を取得できません'
                }
                
        except HttpError as e:
            if e.resp.status == 403:
                return {
                    'status': 'ERROR',
                    'message': 'APIクォータ制限の可能性があります'
                }
            return {
                'status': 'ERROR',
                'message': f'APIエラー: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'エラー: {str(e)}'
            }