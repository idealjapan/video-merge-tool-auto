#!/usr/bin/env python3
"""
特定のチャンネルIDを指定してアップロード
"""
import os
import logging
import pickle
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

class YouTubeChannelUploader:
    """特定チャンネルへの確実なアップロード"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 
              'https://www.googleapis.com/auth/youtube.readonly']
    
    # チャンネルIDマッピング（実際のチャンネルIDに置き換えてください）
    CHANNEL_IDS = {
        'NB': 'UC_xxxxx_NBチャンネルID',  # NBチャンネルのID
        'SBC': 'UC_xxxxx_SBCチャンネルID', # SBCチャンネルのID
        'OM': 'UC_xxxxx_OMチャンネルID'    # OMチャンネルのID
    }
    
    def __init__(self, credentials_dir: str = "credentials"):
        self.credentials_dir = Path(credentials_dir)
        self.client_secrets_path = Path(credentials_dir) / "client_secrets.json"
        
    def list_available_channels(self, creds: Credentials) -> List[Dict]:
        """
        認証したアカウントで利用可能な全チャンネルをリスト
        """
        youtube = build('youtube', 'v3', credentials=creds)
        
        # 自分が管理している全チャンネルを取得
        request = youtube.channels().list(
            part="snippet,contentDetails",
            mine=True
        )
        response = request.execute()
        
        channels = []
        for item in response.get('items', []):
            channels.append({
                'id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet'].get('description', '')[:100]
            })
        
        return channels
    
    def select_channel(self, project_type: str) -> str:
        """
        プロジェクトタイプに基づいてチャンネルを選択
        """
        token_path = self.credentials_dir / f"youtube_{project_type.lower()}_token.pickle"
        
        # 認証
        creds = self.authenticate(token_path, f"{project_type}チャンネル")
        
        # 利用可能なチャンネルを表示
        channels = self.list_available_channels(creds)
        
        print("\n利用可能なチャンネル:")
        print("=" * 60)
        for i, ch in enumerate(channels, 1):
            print(f"{i}. {ch['title']}")
            print(f"   ID: {ch['id']}")
            print(f"   説明: {ch['description']}")
        print("=" * 60)
        
        if len(channels) == 1:
            selected = channels[0]
            print(f"\n自動選択: {selected['title']}")
        else:
            print(f"\n{project_type}チャンネルとして使用するチャンネルを選択してください")
            while True:
                try:
                    choice = int(input("番号を入力 (1-{}): ".format(len(channels))))
                    if 1 <= choice <= len(channels):
                        selected = channels[choice - 1]
                        break
                except ValueError:
                    pass
                print("正しい番号を入力してください")
        
        # チャンネルIDを保存
        config_path = self.credentials_dir / "channel_config.pickle"
        config = {}
        if config_path.exists():
            with open(config_path, 'rb') as f:
                config = pickle.load(f)
        
        config[project_type] = selected['id']
        
        with open(config_path, 'wb') as f:
            pickle.dump(config, f)
        
        print(f"\n✅ {project_type}チャンネルとして設定: {selected['title']}")
        return selected['id']
    
    def authenticate(self, token_path: Path, channel_name: str) -> Credentials:
        """認証処理"""
        creds = None
        
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.client_secrets_path.exists():
                    raise FileNotFoundError(f"認証ファイルが見つかりません: {self.client_secrets_path}")
                
                print(f"\n{channel_name}の認証が必要です")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.client_secrets_path), self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def upload_to_specific_channel(self, 
                                  project_type: str,
                                  video_path: str,
                                  title: str,
                                  description: str = "",
                                  tags: Optional[List[str]] = None,
                                  privacy_status: str = "private") -> Optional[str]:
        """
        特定のチャンネルに確実にアップロード
        """
        # チャンネルIDを取得または選択
        config_path = self.credentials_dir / "channel_config.pickle"
        if config_path.exists():
            with open(config_path, 'rb') as f:
                config = pickle.load(f)
                channel_id = config.get(project_type)
        else:
            channel_id = None
        
        if not channel_id:
            channel_id = self.select_channel(project_type)
        
        # 認証
        token_path = self.credentials_dir / f"youtube_{project_type.lower()}_token.pickle"
        creds = self.authenticate(token_path, f"{project_type}チャンネル")
        youtube = build('youtube', 'v3', credentials=creds)
        
        # アップロード
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'channelId': channel_id,  # 明示的にチャンネルIDを指定
                'categoryId': "22"
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype='video/*'
        )
        
        logger.info(f"チャンネルID {channel_id} にアップロード開始: {title}")
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"アップロード進捗: {int(status.progress() * 100)}%")
        
        video_url = f"https://youtube.com/watch?v={response['id']}"
        logger.info(f"アップロード完了: {video_url}")
        
        return video_url


# 設定スクリプト
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    uploader = YouTubeChannelUploader()
    
    print("=" * 60)
    print("YouTubeチャンネル設定")
    print("=" * 60)
    
    # NBチャンネルを設定
    print("\n[NBチャンネルの設定]")
    uploader.select_channel('NB')