#!/usr/bin/env python3
"""
OMチャンネルの状態確認
"""

import pickle
import sys
from pathlib import Path
from googleapiclient.discovery import build

token_file = Path('credentials/token_OM.pickle')

if not token_file.exists():
    print("❌ OMトークンファイルがありません")
    sys.exit(1)

try:
    with open(token_file, 'rb') as f:
        creds = pickle.load(f)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    # チャンネル情報を取得
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    )
    response = request.execute()
    
    if response['items']:
        channel = response['items'][0]
        print("✅ OMチャンネル接続成功")
        print(f"チャンネル名: {channel['snippet']['title']}")
        print(f"チャンネルID: {channel['id']}")
        
        # 最新の動画を確認
        uploads_id = channel['contentDetails']['relatedPlaylists']['uploads']
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_id,
            maxResults=3
        )
        videos = request.execute()
        
        print("\n最新の動画:")
        for item in videos.get('items', []):
            video_title = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']
            print(f"  - {video_title}")
            print(f"    URL: https://www.youtube.com/watch?v={video_id}")
    else:
        print("❌ チャンネル情報を取得できません")
        
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()