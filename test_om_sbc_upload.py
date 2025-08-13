#\!/usr/bin/env python3
"""OM/SBCチャンネルへのアップロードテスト"""

import pickle
import sys
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import subprocess

def create_test_video():
    """小さなテスト動画を作成"""
    test_file = Path('test_video_temp.mp4')
    
    # ffmpegで1秒の黒画面動画を作成
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'color=c=black:s=640x360:d=1',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        str(test_file)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return test_file
    except:
        # 既存の小さな動画を探す
        for video in Path('.').glob('*.mp4'):
            if video.stat().st_size < 5 * 1024 * 1024:  # 5MB以下
                return video
        return None

def test_channel_upload(channel_name):
    """指定チャンネルにテストアップロード"""
    
    token_file = Path(f'credentials/token_{channel_name}.pickle')
    
    if not token_file.exists():
        print(f'❌ {channel_name}用トークンファイルがありません')
        return False
    
    try:
        # トークンを読み込み
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        # テスト動画を準備
        test_video = create_test_video()
        if not test_video:
            print('テスト動画を作成できませんでした')
            return False
        
        print(f'\n=== {channel_name}チャンネル テスト ===')
        print(f'動画: {test_video} ({test_video.stat().st_size / 1024:.1f} KB)')
        
        # アップロード設定
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        body = {
            'snippet': {
                'title': f'{channel_name}_テスト_{timestamp}',
                'description': f'{channel_name}チャンネルの動作確認テストです。削除してください。',
                'tags': ['test'],
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': 'unlisted',  # 限定公開
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(
            str(test_video),
            mimetype='video/mp4',
            resumable=True,
            chunksize=256*1024
        )
        
        print(f'📤 アップロード中...')
        
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = request.execute()
        
        video_id = response['id']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        
        print(f'✅ {channel_name}チャンネル: アップロード成功！')
        print(f'   URL: {video_url}')
        print(f'   タイトル: {body["snippet"]["title"]}')
        print(f'   状態: 限定公開')
        
        # テスト動画を削除
        if test_video.name == 'test_video_temp.mp4':
            test_video.unlink()
        
        return True
        
    except Exception as e:
        print(f'❌ {channel_name}チャンネル: エラー')
        print(f'   {e}')
        return False

def main():
    """メイン処理"""
    print('=' * 60)
    print('OM/SBCチャンネル アップロードテスト')
    print('=' * 60)
    
    success_count = 0
    
    # OMチャンネルテスト
    if test_channel_upload('OM'):
        success_count += 1
    
    print()
    
    # SBCチャンネルテスト
    if test_channel_upload('SBC'):
        success_count += 1
    
    print()
    print('=' * 60)
    print(f'結果: {success_count}/2 チャンネル成功')
    
    if success_count == 2:
        print('🎉 全チャンネル正常動作！')
    print('=' * 60)
    
    if success_count > 0:
        print('\n⚠️ 重要：')
        print('YouTubeにテスト動画がアップロードされました。')
        print('確認後、削除してください（非公開設定）。')

if __name__ == '__main__':
    main()
