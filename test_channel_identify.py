#\!/usr/bin/env python3
"""チャンネル識別テスト"""

import pickle
import sys
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def test_upload():
    """テスト動画をアップロードしてチャンネルを確認"""
    
    token_file = Path('credentials/youtube_token.pickle')
    
    if not token_file.exists():
        print('❌ トークンファイルがありません')
        return
    
    try:
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        # 小さなテストファイルを作成
        test_file = Path('test_video_temp.mp4')
        
        # 既存の小さな動画を探す
        for video in Path('.').glob('*.mp4'):
            if video.stat().st_size < 10 * 1024 * 1024:  # 10MB以下
                test_file = video
                break
        
        if not test_file.exists():
            print('テスト用動画ファイルがありません')
            return
        
        print(f'テストファイル: {test_file}')
        print(f'サイズ: {test_file.stat().st_size / 1024 / 1024:.1f} MB')
        
        # アップロード設定
        body = {
            'snippet': {
                'title': 'チャンネル確認テスト（削除してください）',
                'description': 'このビデオはチャンネル確認用です。削除してください。',
                'tags': ['test'],
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': 'private',  # 非公開
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(
            str(test_file),
            mimetype='video/mp4',
            resumable=True,
            chunksize=1024*1024
        )
        
        print('\n📤 テストアップロード中...')
        
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = request.execute()
        
        video_id = response['id']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        
        print('✅ アップロード成功！')
        print(f'URL: {video_url}')
        print()
        print('⚠️ 重要：')
        print('1. このURLを開いてください')
        print('2. どのチャンネルにアップロードされたか確認')
        print('3. 確認後、動画を削除してください')
        print()
        print('チャンネル名を確認して教えてください')
        
    except Exception as e:
        print(f'エラー: {e}')
        if 'quotaExceeded' in str(e):
            print('YouTube APIの制限に達しました。後でお試しください。')

if __name__ == '__main__':
    test_upload()
