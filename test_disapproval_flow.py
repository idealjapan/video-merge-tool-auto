#!/usr/bin/env python3
"""
不承認（審査落ち）広告のフルフローテスト
NB_7StepパクCR冒頭Cが不承認になったという想定
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

from automation.google_drive_finder import GoogleDriveFinder
from automation.simple_queue_manager import SimpleQueueManager
from automation.sheets_manager import SheetsManager
from video_merger_auto_bg import VideoMergerWithAutoBG

def test_disapproval_flow():
    """不承認広告のフルフローテスト"""
    print("=" * 80)
    print("🚨 不承認広告フルフローテスト")
    print("=" * 80)
    
    # 1. スプレッドシートに不承認データを追加
    print("\n1️⃣ 処理待ちシートに不承認データを追加...")
    sheets_manager = SheetsManager()
    
    # 処理待ちシートを取得または作成
    try:
        worksheet = sheets_manager.spreadsheet.worksheet("処理待ち")
    except:
        worksheet = sheets_manager.spreadsheet.add_worksheet("処理待ち", 100, 20)
        # ヘッダー追加
        worksheet.update('A1:E1', [['作成日時', 'プロジェクト名', '広告名', 'ステータス', '備考']])
    
    # 不承認データを追加
    # 審査落ちした広告名（実際はYouTubeやスプレッドシートから取得）
    disapproval_ad_name = "YT_NB_800文字_和風"  # YouTubeからの不承認通知
    
    # YT_プレフィックスを除去
    if disapproval_ad_name.startswith('YT_'):
        base_name = disapproval_ad_name[3:]  # "YT_"を除去
    else:
        base_name = disapproval_ad_name
    
    print(f"   不承認広告: {disapproval_ad_name}")
    print(f"   検索用ベース名: {base_name}")
    
    # 案件名: NB_で始まる場合は「NB」にする
    disapproval_data = [
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "NB",  # NB_で始まるので「NB」に統一
        base_name,  # YT_を除去した広告名
        "未処理",
        "審査落ちのため再作成"
    ]
    
    worksheet.append_row(disapproval_data)
    print(f"✅ 不承認データ追加: {disapproval_data[2]}")
    
    # 2. Google Driveから動画を検索
    print("\n2️⃣ Google Driveから動画を検索...")
    finder = GoogleDriveFinder()  # デフォルトフォルダを使用
    
    # 対象動画を検索
    videos = finder.list_videos(limit=50)
    target_video = None
    print(f"   検索中... (全{len(videos)}件)")
    
    # 広告名から番号を除去してベース名を取得（例: "NB_800文字_和風 05" → "NB_800文字_和風"）
    search_name = base_name.split(' ')[0] if ' ' in base_name else base_name
    print(f"   検索対象: {search_name}")
    
    # 動画リストから探す（同じ名前の動画を探す）
    for video in videos:
        video_name_without_ext = video['name'].replace('.mp4', '')
        # 検索名と一致する動画を探す
        if video_name_without_ext == search_name:
            target_video = video
            print(f"   → 発見: {video['name']}")
            break
    
    if not target_video:
        print("❌ 対象動画が見つかりません")
        return False
    
    print(f"✅ 動画発見: {target_video['name']}")
    
    # 3. 動画をダウンロード
    print("\n3️⃣ 動画ダウンロード...")
    video_path = finder.find_and_download(target_video['name'].replace('.mp4', ''))
    
    if not video_path:
        print("❌ ダウンロード失敗")
        return False
    
    print(f"✅ ダウンロード完了: {video_path}")
    print(f"   サイズ: {os.path.getsize(video_path) / 1024 / 1024:.1f} MB")
    
    # 4. 背景合成処理
    print("\n4️⃣ 背景合成処理...")
    merger = VideoMergerWithAutoBG()
    
    output_dir = project_root / 'test_output'
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f"NB_再審査_{timestamp}.mp4"
    
    print("   背景生成中... (1-2分かかります)")
    success = merger.process_with_auto_background(
        str(video_path),
        str(output_path),
        main_scale=0.8,
        disclaimer_text="※結果には個人差があり成果を保証するものではありません"
    )
    
    if not success or not output_path.exists():
        print("⚠️ 背景合成失敗、元動画を使用")
        upload_path = video_path
    else:
        print(f"✅ 背景合成完了: {output_path}")
        print(f"   出力サイズ: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
        upload_path = output_path
    
    # 5. YouTubeアップロード（NBチャンネル）
    print("\n5️⃣ YouTubeアップロード...")
    
    token_file = project_root / 'credentials' / 'token_NB.pickle'
    if not token_file.exists():
        print("❌ NBトークンがありません")
        return False
    
    with open(token_file, 'rb') as token:
        creds = pickle.load(token)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    # タイトルは元の動画名と同じ
    title = target_video['name'].replace('.mp4', '')
    description = ""  # 説明文は空に
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['再審査', 'NB', '背景合成'],
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
    
    print(f"📤 アップロード中...")
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
        
        print(f"✅ アップロード成功!")
        print(f"   URL: {youtube_url}")
        
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        return False
    
    # 6. スプレッドシート更新（YT動画URL）
    print("\n6️⃣ スプレッドシート更新...")
    
    try:
        # YT動画URLシートを取得または作成
        try:
            yt_worksheet = sheets_manager.spreadsheet.worksheet("YT動画URL")
        except:
            yt_worksheet = sheets_manager.spreadsheet.add_worksheet("YT動画URL", 100, 20)
            yt_worksheet.update('A1:F1', [['投稿日時', 'プロジェクト', '広告名', 'YouTube URL', 'ステータス', '備考']])
        
        yt_data = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "NB",  # プロジェクト名を統一
            title,
            youtube_url,
            "再審査版",
            "審査落ち対応で再作成"
        ]
        
        yt_worksheet.append_row(yt_data)
        print("✅ YT動画URLシート更新")
        
    except Exception as e:
        print(f"⚠️ スプレッドシート更新エラー: {e}")
    
    # 7. Google Ads連携キューに追加
    print("\n7️⃣ Google Ads連携キューに追加...")
    queue_manager = SimpleQueueManager()
    
    process_id = queue_manager.add_to_queue(
        video_url=youtube_url,
        project_name="NB",  # プロジェクト名を統一
        ad_name=f"NB_再審査_{timestamp}",
        video_name=title,
        metadata={
            "original_ad": disapproval_ad_name,
            "reason": "審査落ち",
            "background_processed": upload_path == output_path
        }
    )
    
    print(f"✅ キュー追加: {process_id}")
    
    # 8. 処理待ちシートのステータス更新
    print("\n8️⃣ 処理待ちステータス更新...")
    try:
        # 最後の行を更新
        last_row = len(worksheet.get_all_values())
        worksheet.update(f'D{last_row}', [['処理済']])
        worksheet.update(f'E{last_row}', [[f'YouTube: {youtube_url}']])
        print("✅ ステータスを「処理済」に更新")
    except Exception as e:
        print(f"⚠️ ステータス更新エラー: {e}")
    
    # 9. キューステータス確認
    print("\n9️⃣ 現在のキューステータス...")
    status = queue_manager.get_queue_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 80)
    print("🎉 不承認広告フルフローテスト完了！")
    print(f"\n📊 結果サマリー:")
    print(f"   元広告: NB_7StepパクCR冒頭C（審査落ち）")
    print(f"   新動画: {title}")
    print(f"   YouTube: {youtube_url}")
    print(f"   背景合成: {'成功' if upload_path == output_path else 'スキップ'}")
    print(f"   キュー: 登録済み（GAS処理待ち）")
    print("\n⚠️ GASで5分ごとにキューが処理されます")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_disapproval_flow()
    sys.exit(0 if success else 1)