#!/usr/bin/env python3
"""
現在認証されているYouTubeチャンネル情報を確認
"""
import pickle
from pathlib import Path
from googleapiclient.discovery import build

def check_channel():
    """どのチャンネルに接続しているか確認"""
    
    token_path = Path("credentials/youtube_nb_token.pickle")
    
    if not token_path.exists():
        print("トークンファイルが見つかりません")
        return
    
    # トークンを読み込み
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    
    # YouTube APIに接続
    youtube = build('youtube', 'v3', credentials=creds)
    
    # チャンネル情報を取得
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    )
    response = request.execute()
    
    if response['items']:
        channel = response['items'][0]
        print("=" * 60)
        print("現在接続中のYouTubeチャンネル:")
        print("=" * 60)
        print(f"チャンネル名: {channel['snippet']['title']}")
        print(f"チャンネルID: {channel['id']}")
        print(f"説明: {channel['snippet'].get('description', 'なし')[:100]}")
        print(f"登録者数: {channel['statistics'].get('subscriberCount', '非公開')}")
        print(f"動画数: {channel['statistics']['videoCount']}")
        print(f"チャンネルURL: https://youtube.com/channel/{channel['id']}")
        print("=" * 60)
    else:
        print("チャンネル情報を取得できませんでした")

if __name__ == "__main__":
    check_channel()