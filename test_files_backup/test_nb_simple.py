#!/usr/bin/env python3
"""
NBチャンネル シンプルアップロードテスト（背景合成なし）
"""

import os
import sys
import pickle
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'google_service_account.json')

from automation.google_drive_finder import GoogleDriveFinder
from automation.simple_queue_manager import SimpleQueueManager

def test_nb_simple():
    """NBチャンネル シンプルテスト"""
    print("=" * 80)
    print("🎬 NBチャンネル シンプルアップロードテスト")
    print("=" * 80)
    
    # 1. NBトークン確認
    token_file = project_root / 'credentials' / 'token_NB.pickle'
    if not token_file.exists():
        print("❌ NBトークンがありません")
        return False
    
    print("✅ NBトークン確認")
    
    # 2. Google DriveからNB動画を取得
    print("\n📹 NB動画を検索...")
    finder = GoogleDriveFinder()
    videos = finder.list_videos(limit=50)
    nb_videos = [v for v in videos if v['name'].startswith('NB_')]
    
    if not nb_videos:
        print("❌ NB動画が見つかりません")
        return False
    
    test_video = nb_videos[0]
    print(f"✅ 使用動画: {test_video['name']}")
    
    # 3. 動画をダウンロード
    print("\n📥 動画ダウンロード中...")
    video_path = finder.find_and_download(test_video['name'].replace('.mp4', ''))
    
    if not video_path:
        print("❌ ダウンロード失敗")
        return False
    
    print(f"✅ ダウンロード完了: {video_path}")
    print(f"   サイズ: {os.path.getsize(video_path) / 1024 / 1024:.1f} MB")
    
    # 4. YouTubeアップロード
    print("\n📤 YouTubeアップロード準備...")
    
    # YouTube API初期化
    with open(token_file, 'rb') as token:
        creds = pickle.load(token)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    # アップロード設定
    title = test_video['name'].replace('.mp4', '')  # 動画ファイル名と同じタイトル
    description = f"""
自動アップロードテスト
元動画: {test_video['name']}
テスト実行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

このビデオは自動処理システムのテストです。
"""
    
    body = {
        'snippet': {
            'title': title,
            'description': description.strip(),
            'tags': ['テスト', '自動アップロード', 'NB'],
            'categoryId': '22'  # People & Blogs
        },
        'status': {
            'privacyStatus': 'unlisted',  # 限定公開
            'selfDeclaredMadeForKids': False
        }
    }
    
    # メディアアップロード
    media = MediaFileUpload(
        str(video_path),
        mimetype='video/mp4',
        resumable=True,
        chunksize=1024*1024  # 1MB chunks
    )
    
    print(f"📤 アップロード中...")
    print(f"   タイトル: {title}")
    print(f"   プライバシー: 限定公開")
    print(f"   ファイル: {video_path.name}")
    
    try:
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   進捗: {int(status.progress() * 100)}%")
        
        video_id = response['id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"\n✅ アップロード成功!")
        print(f"   Video ID: {video_id}")
        print(f"   URL: {youtube_url}")
        
        # 5. キューに追加
        print("\n📝 キューシステムに記録...")
        queue_manager = SimpleQueueManager()
        process_id = queue_manager.add_to_queue(
            video_url=youtube_url,
            project_name="NB_シンプルテスト",
            ad_name=f"NB_テスト_{datetime.now().strftime('%H%M%S')}",
            video_name=test_video['name']
        )
        print(f"✅ キュー追加: {process_id}")
        
        # 6. ステータス確認
        status = queue_manager.get_queue_status()
        print(f"\n📊 キューステータス:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("🎉 NBチャンネル アップロードテスト成功！")
    print(f"YouTube URL: {youtube_url}")
    print("\n⚠️ 動画は限定公開でアップロードされています")
    print("YouTube Studioで確認してください")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_nb_simple()
    sys.exit(0 if success else 1)