#!/usr/bin/env python3
"""
NBチャンネル 背景合成付きアップロードテスト
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

def test_nb_with_background():
    """NBチャンネル 背景合成付きテスト"""
    print("=" * 80)
    print("🎬 NBチャンネル 背景合成付きアップロードテスト")
    print("=" * 80)
    
    # 1. NBトークン確認
    token_file = project_root / 'credentials' / 'token_NB.pickle'
    if not token_file.exists():
        print("❌ NBトークンがありません")
        return False
    
    print("✅ NBトークン確認")
    
    # 2. Google DriveからNB動画を取得（短い動画を選択）
    print("\n📹 NB動画を検索...")
    finder = GoogleDriveFinder()
    videos = finder.list_videos(limit=50)
    nb_videos = [v for v in videos if v['name'].startswith('NB_')]
    
    if not nb_videos:
        print("❌ NB動画が見つかりません")
        return False
    
    # 一番短そうな動画を選択
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
    
    # 4. 背景合成処理
    print("\n🎨 背景合成処理...")
    merger = VideoMergerWithAutoBG()
    
    # 出力パス設定
    output_dir = project_root / 'test_output'
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"NB_bg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    try:
        # 背景スタイル設定
        background_style = "style1"  # またはstyle2, style3
        print(f"   背景スタイル: {background_style}")
        print(f"   処理中... (数分かかる場合があります)")
        
        # 背景合成実行（Replicate APIを使用）
        success = merger.process_with_auto_background(
            str(video_path),
            str(output_path),
            main_scale=0.8,  # メイン動画のスケール（80%）
            disclaimer_text="※結果には個人差があり成果を保証するものではありません"  # 注意書きを追加
        )
        
        if not success or not output_path.exists():
            print("❌ 背景合成失敗")
            # 失敗した場合は元動画を使用
            print("⚠️ 元動画を使用してアップロードします")
            upload_path = video_path
        else:
            print(f"✅ 背景合成完了: {output_path}")
            print(f"   出力サイズ: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
            upload_path = output_path
            
    except Exception as e:
        print(f"⚠️ 背景合成エラー: {e}")
        print("元動画を使用してアップロードします")
        upload_path = video_path
    
    # 5. YouTubeアップロード
    print("\n📤 YouTubeアップロード準備...")
    
    # YouTube API初期化
    with open(token_file, 'rb') as token:
        creds = pickle.load(token)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    # アップロード設定
    title = test_video['name'].replace('.mp4', '')  # 動画ファイル名と同じタイトル
    description = ""  # 説明文は空に
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['テスト', '自動アップロード', 'NB', '背景合成'],
            'categoryId': '22'  # People & Blogs
        },
        'status': {
            'privacyStatus': 'unlisted',  # 限定公開
            'selfDeclaredMadeForKids': False
        }
    }
    
    # メディアアップロード
    media = MediaFileUpload(
        str(upload_path),
        mimetype='video/mp4',
        resumable=True,
        chunksize=1024*1024  # 1MB chunks
    )
    
    print(f"📤 アップロード中...")
    print(f"   タイトル: {title}")
    print(f"   プライバシー: 限定公開")
    print(f"   ファイル: {upload_path.name}")
    
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
                print(f"   進捗: {int(status.progress() * 100)}%", end='\r')
        
        print()  # 改行
        video_id = response['id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"\n✅ アップロード成功!")
        print(f"   Video ID: {video_id}")
        print(f"   URL: {youtube_url}")
        
        # 6. キューに追加
        print("\n📝 キューシステムに記録...")
        queue_manager = SimpleQueueManager()
        process_id = queue_manager.add_to_queue(
            video_url=youtube_url,
            project_name="NB_背景合成テスト",
            ad_name=f"NB_BG_{datetime.now().strftime('%H%M%S')}",
            video_name=test_video['name'],
            metadata={
                "background_style": background_style if upload_path == output_path else "none",
                "processed": upload_path == output_path
            }
        )
        print(f"✅ キュー追加: {process_id}")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("🎉 NBチャンネル 背景合成付きアップロードテスト成功！")
    print(f"YouTube URL: {youtube_url}")
    print(f"背景合成: {'成功' if upload_path == output_path else 'スキップ'}")
    print("\n⚠️ 動画は限定公開でアップロードされています")
    print("YouTube Studioで確認してください")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_nb_with_background()
    sys.exit(0 if success else 1)