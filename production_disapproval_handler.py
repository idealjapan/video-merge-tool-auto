#!/usr/bin/env python3
"""
本番用不承認広告処理（複数件対応版）
複数の不承認広告を順番に処理してYouTubeアップロード＆キュー追加
"""

import os
import sys
import pickle
import time
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
from youtube_auth_manager import YouTubeAuthManager

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# .envファイルから環境変数を読み込み
load_dotenv()

# 環境変数が設定されていない場合のみデフォルト値を設定
if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(project_root / 'credentials' / 'google_service_account.json')

from automation.approval_status_reader import ApprovalStatusReader
from automation.google_drive_finder import GoogleDriveFinder
from automation.simple_queue_manager import SimpleQueueManager
from video_merger_auto_bg import VideoMergerWithAutoBG

def process_single_ad(ad, index, total):
    """単一の不承認広告を処理"""
    print(f"\n{'='*40}")
    print(f"📍 処理中: {index}/{total}")
    print(f"   広告グループ: {ad['ad_group_name']}")
    print(f"   アカウントID: {ad['account_id']}")
    print(f"{'='*40}")
    
    # 広告グループ名から案件と動画情報を取得
    ad_group_name = ad['ad_group_name']
    
    # 特定の広告グループをスキップ（デマンドジェネレーション以外）
    if 'YT_NB_7stepパク応援特典8選_MCC02運用02_28_01' in ad_group_name:
        print(f"   ⚠️ スキップ: この広告グループはデマンドジェネレーション広告ではありません")
        return False
    
    # 2. Google Driveから動画を検索
    print("\n2️⃣ Google Driveから動画を検索...")
    finder = GoogleDriveFinder()
    
    video_path = finder.find_video_by_ad_group(ad_group_name)
    
    if not video_path:
        parsed = finder.parse_ad_group_name(ad_group_name)
        print(f"❌ 対象動画が見つかりません")
        print(f"   案件: {parsed['project']}")
        print(f"   動画名: {parsed['video_name']}")
        if not parsed.get('has_mcc', True):
            print(f"   ⚠️ 注意: MCC記載が欠けている可能性があります")
        print(f"   Google Driveの案件フォルダに該当する動画をアップロードしてください")
        return False
    
    print(f"   ✅ ダウンロード完了: {video_path}")
    print(f"   サイズ: {os.path.getsize(video_path) / 1024 / 1024:.1f} MB")
    
    # 3. 背景合成処理
    print("\n3️⃣ 背景合成処理...")
    merger = VideoMergerWithAutoBG()
    
    output_dir = project_root / 'ad-videos'
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 解析情報を取得
    parsed = finder.parse_ad_group_name(ad_group_name)
    project_name = parsed['project']
    search_name = parsed['video_name']
    
    output_path = output_dir / f"{project_name}_再審査_{timestamp}.mp4"
    
    print("   背景生成中... (1-2分かかります)")
    result = merger.process_with_auto_background(
        str(video_path),
        str(output_path),
        main_scale=0.8,
        disclaimer_text="※結果には個人差があり成果を保証するものではありません"
    )
    
    if result and isinstance(result, dict):
        output_path = Path(result['output_path'])
        print(f"   ✅ 背景合成完了: {output_path}")
        print(f"   サイズ: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
        upload_path = output_path
    else:
        print("   ⚠️ 背景合成失敗、元動画を使用")
        upload_path = video_path
    
    # 4. YouTubeアップロード
    print("\n4️⃣ YouTubeアップロード...")
    
    print(f"   使用チャンネル: {project_name}")
    
    # 新しい認証マネージャーを使用（自動リフレッシュ機能付き）
    auth_manager = YouTubeAuthManager(project_name)
    
    try:
        youtube = auth_manager.get_authenticated_service()
    except FileNotFoundError as e:
        print(f"❌ {project_name}チャンネルの認証ファイルが見つかりません")
        print(f"   python youtube_auth_manager.py --channel {project_name} を実行してください")
        return False
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        return False
    
    title = search_name
    description = ""
    
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
        
        print()
        video_id = response['id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"   ✅ アップロード成功!")
        print(f"   URL: {youtube_url}")
        
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        return False
    
    # 5. 広告キューに追加
    print("\n5️⃣ 広告キューに追加...")
    queue_manager = SimpleQueueManager()
    
    process_id = queue_manager.add_to_queue(
        video_url=youtube_url,
        project_name=project_name,
        ad_name="",
        video_name=title,
        ad_group_name=ad_group_name,
        account_id=ad['account_id'],
        metadata={
            "original_ad": ad_group_name,
            "reason": "不承認",
            "background_processed": str(upload_path) == str(output_path),
            "production": True
        }
    )
    
    print(f"   ✅ キュー追加完了: {process_id}")
    print(f"   - 広告グループ名: {ad_group_name}")
    print(f"   - アカウントID: {ad['account_id']}")
    print(f"   - YouTube URL: {youtube_url}")
    
    return True

def process_disapproved_ads():
    """複数の不承認広告を処理"""
    print("=" * 80)
    print("🚨 本番不承認広告処理（複数件対応版）")
    print("=" * 80)
    
    # 必要なディレクトリを作成
    Path("logs").mkdir(exist_ok=True)
    Path("ad-videos").mkdir(exist_ok=True)
    Path("outputs").mkdir(exist_ok=True)
    
    # 1. 不承認広告を取得
    print("\n1️⃣ 不承認広告を確認...")
    reader = ApprovalStatusReader()
    disapproved_ads = reader.get_disapproved_ads()
    
    if not disapproved_ads:
        print("✅ 不承認広告はありません")
        return True
    
    print(f"📊 不承認広告が{len(disapproved_ads)}件見つかりました")
    
    # すべての不承認広告を順番に処理
    processed_count = 0
    failed_count = 0
    results = []
    
    for index, ad in enumerate(disapproved_ads, 1):
        try:
            success = process_single_ad(ad, index, len(disapproved_ads))
            
            if success:
                processed_count += 1
                results.append({
                    'ad_group_name': ad['ad_group_name'],
                    'status': '成功'
                })
                print(f"✅ {index}/{len(disapproved_ads)} 処理成功")
            else:
                # スキップの場合は失敗にカウントしない
                if 'YT_NB_7stepパク応援特典8選_MCC02運用02_28_01' in ad['ad_group_name']:
                    results.append({
                        'ad_group_name': ad['ad_group_name'],
                        'status': 'スキップ（非デマンドジェネレーション）'
                    })
                else:
                    failed_count += 1
                    results.append({
                        'ad_group_name': ad['ad_group_name'],
                        'status': '失敗'
                    })
                    print(f"❌ {index}/{len(disapproved_ads)} 処理失敗")
            
            # 次の処理まで少し待機（API制限対策）
            if index < len(disapproved_ads):
                print(f"\n⏳ 次の処理まで5秒待機...")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ エラー発生: {e}")
            failed_count += 1
            results.append({
                'ad_group_name': ad['ad_group_name'],
                'status': f'エラー: {str(e)}'
            })
    
    # 最終サマリー
    print("\n" + "=" * 80)
    print("🎉 全処理完了！")
    print(f"\n📊 最終結果:")
    print(f"   総数: {len(disapproved_ads)}件")
    print(f"   成功: {processed_count}件")
    print(f"   失敗: {failed_count}件")
    
    print(f"\n📋 詳細:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['ad_group_name']}: {result['status']}")
    
    print("\n次のステップ:")
    print("1. スプレッドシートの「広告キュー」シートを確認")
    print("2. GASで processQueueFromSheets() を実行")
    print("=" * 80)
    
    return processed_count > 0

if __name__ == "__main__":
    success = process_disapproved_ads()
    exit(0 if success else 1)