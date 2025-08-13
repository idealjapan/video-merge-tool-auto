#\!/usr/bin/env python3
"""取得したトークンがどのチャンネルか確認"""

import pickle
from pathlib import Path
from googleapiclient.discovery import build

def check_token_channel():
    """トークンで最近アップロードした動画を確認"""
    
    # 取得したトークン（OM/SBCとして保存されているが実際は同じ）
    token_file = Path('credentials/token_OM.pickle')
    
    if not token_file.exists():
        print('トークンファイルがありません')
        return
    
    try:
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        print('=== 最近アップロードした動画を確認 ===\n')
        
        # 最近アップロードした動画を取得
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId='UU' + 'CHANNEL_ID',  # これは動作しないが、別の方法を試す
            maxResults=5
        )
        
        # 動画リストを直接検索
        search_request = youtube.search().list(
            part='snippet',
            forMine=True,
            type='video',
            order='date',
            maxResults=10
        )
        
        response = search_request.execute()
        
        if response.get('items'):
            print('最近アップロードした動画:')
            for item in response['items']:
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                channel_title = item['snippet'].get('channelTitle', '不明')
                
                print(f'\n動画: {title}')
                print(f'URL: https://www.youtube.com/watch?v={video_id}')
                print(f'チャンネル: {channel_title}')
                
                # テスト動画を探す
                if 'テスト' in title or 'test' in title.lower():
                    print('  ← これがテスト動画です！')
            
            print('\n上記のURLを確認して、どのチャンネルか教えてください:')
            print('- OM (https://www.youtube.com/@yuki_om)')
            print('- SBC (https://www.youtube.com/@SBC-fp9zq)')
            print('- それ以外')
            
        else:
            print('動画が見つかりませんでした')
            
    except Exception as e:
        print(f'エラー: {e}')
        
        # 別の方法：動画を直接指定して確認
        print('\n代替方法: アップロードした動画IDから確認')
        video_ids = [
            'GpirVoPan2I',  # OM_テスト_20250813_150337
            'eLtVCQZU8Lk',  # SBC_テスト_20250813_150339
        ]
        
        for vid in video_ids:
            try:
                video_request = youtube.videos().list(
                    part='snippet',
                    id=vid
                )
                video_response = video_request.execute()
                
                if video_response.get('items'):
                    video = video_response['items'][0]
                    print(f'\n動画ID: {vid}')
                    print(f'タイトル: {video["snippet"]["title"]}')
                    print(f'チャンネル: {video["snippet"]["channelTitle"]}')
                    print(f'URL: https://www.youtube.com/watch?v={vid}')
            except:
                pass

if __name__ == '__main__':
    check_token_channel()
