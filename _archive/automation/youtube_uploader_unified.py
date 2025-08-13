#!/usr/bin/env python3
"""
YouTube統合アップローダー
1つのOAuth2アプリで複数チャンネル対応
"""
import os
import logging
import pickle
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from automation.channel_manager import ChannelManager

logger = logging.getLogger(__name__)

class YouTubeUploaderUnified:
    """YouTube動画アップローダー（1つのOAuth2アプリで複数チャンネル対応）"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    CLIENT_SECRETS_FILE = 'credentials/client_secrets.json'  # 共通のOAuth2ファイル
    
    def __init__(self, credentials_dir: str = "credentials"):
        """
        初期化
        
        Args:
            credentials_dir: 認証ファイルのディレクトリ
        """
        self.credentials_dir = Path(credentials_dir)
        self.channel_manager = ChannelManager(credentials_dir)
        self.client_secrets_path = Path(self.CLIENT_SECRETS_FILE)
        
    def authenticate_channel(self, token_path: Path, channel_name: str) -> Credentials:
        """
        特定チャンネルの認証
        
        Args:
            token_path: トークンファイルのパス
            channel_name: チャンネル名（表示用）
            
        Returns:
            認証情報
        """
        creds = None
        
        # 保存済みトークンがあれば読み込み
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
                logger.info(f"{channel_name}のトークンを読み込みました")
        
        # トークンがないか期限切れの場合は再認証
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logger.info(f"{channel_name}のトークンを更新しました")
            else:
                if not self.client_secrets_path.exists():
                    raise FileNotFoundError(
                        f"OAuth2認証ファイルが見つかりません: {self.client_secrets_path}\n"
                        f"Google Cloud ConsoleからOAuth2クライアントIDをダウンロードして、"
                        f"{self.client_secrets_path}に配置してください"
                    )
                
                print(f"\n{channel_name}の認証が必要です")
                print(f"ブラウザが開きます。{channel_name}のGoogleアカウントでログインしてください")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.client_secrets_path), self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # トークンを保存
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
                logger.info(f"{channel_name}のトークンを保存しました")
        
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
            creds = self.authenticate_channel(
                channel_info['token_path'], 
                channel_info['channel_name']
            )
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
    
    def setup_all_channels(self):
        """
        全チャンネルの初期設定（順番に認証）
        """
        print("=" * 60)
        print("YouTubeチャンネル設定")
        print("1つのOAuth2アプリで複数チャンネルを設定します")
        print("=" * 60)
        
        if not self.client_secrets_path.exists():
            print(f"\n❌ OAuth2認証ファイルが見つかりません: {self.client_secrets_path}")
            print("\n設定手順:")
            print("1. Google Cloud Consoleにアクセス")
            print("2. YouTube Data API v3を有効化")
            print("3. OAuth 2.0クライアントIDを作成")
            print("4. ダウンロードしたJSONファイルを")
            print(f"   {self.client_secrets_path} に配置")
            return
        
        channels = [
            ('NB', 'NBチャンネル'),
            ('SBC', 'SBCチャンネル'),
            ('OM', 'OMチャンネル')
        ]
        
        for project_type, channel_name in channels:
            print(f"\n[{channel_name}の設定]")
            
            # 擬似的な広告名でチャンネル情報を取得
            test_ad_name = f"{project_type}_テスト"
            try:
                channel_info = self.channel_manager.get_channel_info(test_ad_name)
                
                if channel_info['token_path'].exists():
                    print(f"  ✓ すでに認証済みです")
                    continue
                
                input(f"  {channel_name}のGoogleアカウントで認証します。Enterキーを押して続行...")
                
                creds = self.authenticate_channel(
                    channel_info['token_path'],
                    channel_name
                )
                print(f"  ✅ {channel_name}の認証成功！")
                
            except Exception as e:
                print(f"  ❌ 認証失敗: {e}")
        
        print("\n" + "=" * 60)
        print("設定状況:")
        status = self.channel_manager.validate_tokens()
        for channel_id, exists in status.items():
            status_text = "✓ 認証済み" if exists else "✗ 未認証"
            print(f"  {channel_id}: {status_text}")
        print("=" * 60)


# テスト用
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    uploader = YouTubeUploaderUnified()
    
    # 初期設定を実行
    uploader.setup_all_channels()
    
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