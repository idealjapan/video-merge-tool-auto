#!/usr/bin/env python3
"""
本番用不承認広告処理
実際の不承認広告を処理してYouTubeアップロード＆キュー追加
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
os.environ['REPLICATE_API_TOKEN'] = 'r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'

from automation.approval_status_reader import ApprovalStatusReader
from automation.google_drive_finder import GoogleDriveFinder
from automation.simple_queue_manager import SimpleQueueManager
from video_merger_auto_bg import VideoMergerWithAutoBG

def process_disapproved_ad():
    """不承認広告を処理"""
    print("=" * 80)
    print("🚨 本番不承認広告処理")
    print("=" * 80)
    
    # 1. 不承認広告を取得
    print("\n1️⃣ 不承認広告を確認...")
    reader = ApprovalStatusReader()
    disapproved_ads = reader.get_disapproved_ads()
    
    if not disapproved_ads:
        print("✅ 不承認広告はありません")
        return True
    
    # 最初の不承認広告を処理
    ad = disapproved_ads[0]
    print(f"   処理対象: {ad['ad_group_name']}")
    print(f"   アカウントID: {ad['account_id']}")
    
    # approval_status_readerが正しく解析した動画名を使用
    ad_group_name = ad['ad_group_name']
    project_name = ad['project_name']
    search_name = ad['video_name']  # これが正しい動画名
    
    print(f"   案件名: {project_name}")
    print(f"   検索動画名: {search_name}")
    print(f"   ※approval_status_readerから取得した動画名: {ad['video_name']}")
    
    # 2. Google Driveから動画を検索
    print("\n2️⃣ Google Driveから動画を検索...")
    finder = GoogleDriveFinder()
    
    # 動画を検索（完全一致を試みる）
    videos = finder.list_videos(limit=100)
    target_video = None
    
    # 完全一致を探す
    for video in videos:
        video_name_without_ext = video['name'].replace('.mp4', '')
        if video_name_without_ext == search_name:
            target_video = video
            print(f"   ✅ 完全一致: {video['name']}")
            break
    
    # 完全一致がない場合は部分一致を探す
    if not target_video:
        # 検索名の各単語が含まれる動画を探す
        search_words = search_name.replace('_', ' ').lower().split()
        best_match = None
        best_score = 0
        
        for video in videos:
            video_name_without_ext = video['name'].replace('.mp4', '').lower()
            # 各単語が含まれるかチェック
            score = sum(1 for word in search_words if word in video_name_without_ext)
            if score > best_score:
                best_score = score
                best_match = video
        
        if best_match and best_score >= len(search_words) * 0.7:  # 70%以上の単語が一致
            target_video = best_match
            print(f"   ⚠️ 部分一致: {best_match['name']} (スコア: {best_score}/{len(search_words)})")
    
    if not target_video:
        print(f"❌ 対象動画が見つかりません: {search_name}")
        print(f"   Google Driveに該当する動画をアップロードしてください")
        return False
    
    # 3. 動画をダウンロード
    print("\n3️⃣ 動画ダウンロード...")
    # 直接ダウンロード（すでにtarget_videoを特定済み）
    video_path = finder._download_file(
        target_video['id'], 
        target_video['name'],
        search_name  # 広告名として使用
    )
    
    if not video_path:
        print("❌ ダウンロード失敗")
        return False
    
    print(f"   ✅ ダウンロード完了: {video_path}")
    print(f"   サイズ: {os.path.getsize(video_path) / 1024 / 1024:.1f} MB")
    
    # 4. 背景合成処理
    print("\n4️⃣ 背景合成処理...")
    merger = VideoMergerWithAutoBG()
    
    output_dir = project_root / 'ad-videos'
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f"{project_name}_再審査_{timestamp}.mp4"
    
    print("   背景生成中... (1-2分かかります)")
    success = merger.process_with_auto_background(
        str(video_path),
        str(output_path),
        main_scale=0.8,
        disclaimer_text="※結果には個人差があり成果を保証するものではありません"
    )
    
    if not success or not output_path.exists():
        print("   ⚠️ 背景合成失敗、元動画を使用")
        upload_path = video_path
    else:
        print(f"   ✅ 背景合成完了: {output_path}")
        print(f"   サイズ: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
        upload_path = output_path
    
    # 5. YouTubeアップロード（案件に応じたチャンネル）
    print("\n5️⃣ YouTubeアップロード...")
    
    # 案件名に応じてトークンファイルを選択
    token_mapping = {
        'NB': 'token_NB.pickle',
        'OM': 'token_OM.pickle',
        'SBC': 'token_SBC.pickle',
        'RL': 'token_RL.pickle'  # RLチャンネル（トークン取得後に使用可能）
    }
    
    token_filename = token_mapping.get(project_name, 'token_NB.pickle')
    token_file = project_root / 'credentials' / token_filename
    
    if not token_file.exists():
        print(f"❌ {project_name}用のトークンファイルがありません: {token_filename}")
        print(f"   利用可能なトークン: {', '.join([f.name for f in (project_root / 'credentials').glob('token_*.pickle')])}")
        return False
    
    print(f"   使用チャンネル: {project_name}")
    
    with open(token_file, 'rb') as token:
        creds = pickle.load(token)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    # タイトルは検索した動画名（広告グループ名から解析した名前）を使用
    title = search_name
    description = ""  # 説明文は空
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': [],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'unlisted',
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(
        str(upload_path),
        mimetype='video/mp4',
        resumable=True,
        chunksize=1024*1024
    )
    
    print(f"   📤 アップロード中...")
    print(f"   タイトル: {title}")
    print(f"   プライバシー: 限定公開")
    
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
        
        print(f"   ✅ アップロード成功!")
        print(f"   URL: {youtube_url}")
        
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        return False
    
    # 6. 広告キューに追加
    print("\n6️⃣ 広告キューに追加...")
    queue_manager = SimpleQueueManager()
    
    process_id = queue_manager.add_to_queue(
        video_url=youtube_url,
        project_name=project_name,
        ad_name="",  # GAS側で元の広告名 + "_copy_" + タイムスタンプが付けられる
        video_name=title,
        ad_group_name=ad_group_name,  # 実際の広告グループ名
        account_id=ad['account_id'],   # 実際のアカウントID
        metadata={
            "original_ad": ad_group_name,
            "reason": "不承認",
            "background_processed": upload_path == output_path,
            "production": True
        }
    )
    
    print(f"   ✅ キュー追加完了: {process_id}")
    print(f"   - 広告グループ名: {ad_group_name}")
    print(f"   - アカウントID: {ad['account_id']}")
    print(f"   - YouTube URL: {youtube_url}")
    
    # 7. キューステータス確認
    print("\n7️⃣ キューステータス確認...")
    status = queue_manager.get_queue_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 80)
    print("🎉 本番不承認処理完了！")
    print(f"\n📊 結果サマリー:")
    print(f"   不承認広告: {ad_group_name}")
    print(f"   新動画: {title}")
    print(f"   YouTube: {youtube_url}")
    print(f"   背景合成: {'成功' if upload_path == output_path else 'スキップ'}")
    print(f"   キュー: 登録済み（GAS処理待ち）")
    print("\n次のステップ:")
    print("1. スプレッドシートの「広告キュー」シートを確認")
    print("2. GASで processQueueFromSheets() を実行")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = process_disapproved_ad()
    sys.exit(0 if success else 1)