#!/usr/bin/env python3
"""
実際のYouTubeアップロード機能
複数チャンネル対応版
"""
import os
import logging
import time
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

from automation.channel_manager import ChannelManager

logger = logging.getLogger(__name__)

class YouTubeUploaderMulti:
    """YouTube動画アップローダー（複数チャンネル対応）"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_dir: str = "credentials"):
        """
        初期化
        
        Args:
            credentials_dir: 認証ファイルのディレクトリ
        """
        self.credentials_dir = Path(credentials_dir)
        self.channel_manager = ChannelManager(credentials_dir)
        
    def authenticate(self, credentials_path: Path) -> Credentials:
        """
        YouTube API認証
        
        Args:
            credentials_path: OAuth2認証ファイルのパス
            
        Returns:
            認証情報
        """
        creds = None
        token_path = credentials_path.parent / f"{credentials_path.stem}_token.pickle"
        
        # 保存済みトークンがあれば読み込み
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # トークンがないか期限切れの場合は再認証
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_path.exists():
                    raise FileNotFoundError(f"認証ファイルが見つかりません: {credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def upload_video(self, 
                    ad_name: str,
                    video_path: str,
                    description: str = "",
                    tags: Optional[List[str]] = None,
                    category: str = "22",  # People & Blogs
                    privacy_status: str = "private") -> Optional[str]:
        """
        動画をYouTubeにアップロード（チャンネル自動振り分け）
        
        Args:
            ad_name: 広告名（プレフィックス付き）
            video_path: アップロードする動画のパス
            description: 動画の説明
            tags: タグのリスト
            category: YouTubeカテゴリID
            privacy_status: 公開設定 (private/unlisted/public)
            
        Returns:
            アップロードされた動画のURL
        """
        try:
            # チャンネル情報を取得
            channel_info = self.channel_manager.get_channel_info(ad_name)
            logger.info(f"アップロード先: {channel_info['channel_name']}")
            
            # タイトルを生成
            title = self.channel_manager.get_upload_title(ad_name)
            
            # 認証
            creds = self.authenticate(channel_info['credentials_path'])
            youtube = build('youtube', 'v3', credentials=creds)
            
            # アップロード用のbody
            body = {
                'snippet': {
                    'title': title,
                    'description': description or f"自動アップロード: {datetime.now()}",
                    'tags': tags or [channel_info['project_type'], '自動生成', '背景合成'],
                    'categoryId': category
                },
                'status': {
                    'privacyStatus': privacy_status
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
            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"アップロード進捗: {progress}%")
            
            video_id = response['id']
            video_url = f"https://youtube.com/watch?v={video_id}"
            
            logger.info(f"アップロード完了: {video_url}")
            logger.info(f"  チャンネル: {channel_info['channel_name']}")
            logger.info(f"  タイトル: {title}")
            
            return video_url
            
        except Exception as e:
            logger.error(f"アップロードエラー: {e}")
            return None
    
    def setup_channels(self):
        """
        各チャンネルの初期設定（初回認証）
        """
        print("=" * 60)
        print("YouTubeチャンネル設定")
        print("=" * 60)
        
        channels = [
            ('NB', 'youtube_nb_credentials.json'),
            ('SBC', 'youtube_sbc_credentials.json'),
            ('OM', 'youtube_om_credentials.json')
        ]
        
        for project_type, cred_file in channels:
            cred_path = self.credentials_dir / cred_file
            
            print(f"\n[{project_type}チャンネル]")
            
            if not cred_path.exists():
                print(f"  ❌ 認証ファイルがありません: {cred_path}")
                print(f"     Google Cloud Consoleから{project_type}用のOAuth2認証ファイルを")
                print(f"     ダウンロードして配置してください")
                continue
            
            try:
                print(f"  認証開始... ブラウザが開きます")
                creds = self.authenticate(cred_path)
                print(f"  ✅ 認証成功！")
            except Exception as e:
                print(f"  ❌ 認証失敗: {e}")
        
        print("\n" + "=" * 60)
        print("設定完了")
        print("=" * 60)


# テスト用
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    uploader = YouTubeUploaderMulti()
    
    # 初期設定を実行
    # uploader.setup_channels()
    
    # テストアップロード（実際にはコメントアウト）
    """
    result = uploader.upload_video(
        ad_name="SBC_テスト動画",
        video_path="test_output/test_video.mp4",
        description="テストアップロード",
        tags=["テスト", "自動アップロード"],
        privacy_status="private"
    )
    
    if result:
        print(f"✅ アップロード成功: {result}")
    """