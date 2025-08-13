#!/usr/bin/env python3
"""
NBチャンネルで実際にYouTubeアップロードまで行うテスト
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
from video_merger_auto_bg import VideoMergerWithAutoBG

def test_nb_with_upload():
    """NBチャンネルで実際のアップロードテスト"""
    print("=" * 80)
    print("🎬 NBチャンネル 実アップロードテスト")
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
    
    # 4. 背景合成
    print("\n🎨 背景合成処理...")
    merger = VideoMergerWithAutoBG()
    output_dir = project_root / 'test_output'
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"NB_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    # 背景動画の生成と合成
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as bg_file:
        bg_path = bg_file.name
    
    # 背景生成
    merger.generate_background(bg_path, style="style1")
    
    # 動画合成
    success = merger.merge_videos(
        str(video_path),
        bg_path,
        str(output_path)
    )
    
    if not success or not output_path.exists():
        print("❌ 背景合成失敗")
        return False
    
    print(f"✅ 背景合成完了: {output_path}")
    
    # 5. YouTubeアップロード
    print("\n📤 YouTubeアップロード準備...")
    
    # YouTube API初期化
    with open(token_file, 'rb') as token:
        creds = pickle.load(token)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    # アップロード設定
    title = test_video['name'].replace('.mp4', '')  # 動画ファイル名と同じタイトル
    description = "自動アップロードテスト\\n元動画: " + test_video['name']
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['テスト', '自動アップロード'],
            'categoryId': '22'  # People & Blogs
        },
        'status': {
            'privacyStatus': 'unlisted'  # 限定公開でアップロード
        }
    }
    
    # メディアアップロード
    media = MediaFileUpload(
        str(output_path),
        mimetype='video/mp4',
        resumable=True
    )
    
    print(f"📤 アップロード中...")
    print(f"   タイトル: {title}")
    print(f"   プライバシー: 限定公開")
    
    try:
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        response = request.execute()
        
        video_id = response['id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"✅ アップロード成功!")
        print(f"   URL: {youtube_url}")
        
        # 6. キューに追加
        print("\n📝 キューシステムに記録...")
        queue_manager = SimpleQueueManager()
        process_id = queue_manager.add_to_queue(
            video_url=youtube_url,
            project_name="NB_実テスト",
            ad_name=f"NB_実広告_{datetime.now().strftime('%H%M%S')}",
            video_name=test_video['name']
        )
        print(f"✅ キュー追加: {process_id}")
        
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("🎉 NBチャンネル フルテスト成功！")
    print(f"YouTube URL: {youtube_url}")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_nb_with_upload()
    sys.exit(0 if success else 1)