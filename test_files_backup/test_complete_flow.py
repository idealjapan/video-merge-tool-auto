#!/usr/bin/env python3
"""
完全な処理フローのテスト
Google Drive → 背景合成 → YouTube → スプレッドシート記録
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_complete_flow():
    """完全な処理フローのテスト"""
    
    print("=" * 60)
    print("完全フローテスト")
    print("=" * 60)
    
    # テスト用の広告名（NBチャンネル用）
    ad_name = "NB_フルテスト広告"
    
    print(f"\n広告名: {ad_name}")
    print("処理フロー:")
    print("1. Google Driveから動画取得")
    print("2. AI背景生成・合成")
    print("3. YouTubeアップロード（NBチャンネル）")
    print("4. スプレッドシート記録")
    print("-" * 60)
    
    try:
        # 1. Google Driveから動画を取得
        print("\n[1/5] Google Driveから動画を検索...")
        from automation.google_drive_finder import GoogleDriveFinder
        
        drive_finder = GoogleDriveFinder()
        
        # テスト用に既存の動画を使用（"変わらない勇気"を検索）
        test_video_name = "変わらない勇気"
        video_path = drive_finder.find_and_download(test_video_name)
        
        if not video_path:
            print(f"❌ 動画が見つかりません: {test_video_name}")
            print("テスト用にローカル動画を使用します")
            # ローカルのテスト動画を使用
            video_path = Path("test_input_video.mov")
            if not video_path.exists():
                print("❌ テスト動画がありません")
                return False
        else:
            print(f"✅ 動画取得成功: {video_path}")
            print(f"   サイズ: {video_path.stat().st_size / (1024*1024):.1f}MB")
        
        # 2. 背景合成処理
        print("\n[2/5] AI背景生成・合成処理...")
        from video_merger_auto_bg import VideoMergerWithAutoBG
        
        os.environ['REPLICATE_API_TOKEN'] = 'r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'
        merger = VideoMergerWithAutoBG()
        
        # 動画情報を取得
        main_info = merger.get_video_info(str(video_path))
        print(f"   動画情報: {main_info['width']}x{main_info['height']}, {main_info['duration']:.1f}秒")
        
        # 背景を生成
        print("   背景生成中...")
        bg_video = merger.generate_background_with_replicate(
            orientation=main_info['orientation'],
            duration=main_info['duration'],
            style='nature'
        )
        
        if not bg_video:
            print("❌ 背景生成に失敗")
            return False
        
        print("✅ 背景生成成功")
        
        # 動画を合成
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{ad_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        print("   動画合成中...")
        merger.merge_videos(
            main_video=str(video_path),
            background_video=bg_video,
            output_video=str(output_path),
            disclaimer_text="自動テスト"
        )
        
        print(f"✅ 背景合成成功: {output_path}")
        print(f"   出力サイズ: {output_path.stat().st_size / (1024*1024):.1f}MB")
        
        # 3. YouTubeアップロード
        print("\n[3/5] YouTubeアップロード...")
        from automation.youtube_uploader_unified import YouTubeUploaderUnified
        
        uploader = YouTubeUploaderUnified()
        
        youtube_url = uploader.upload_video(
            ad_name=ad_name,
            video_path=str(output_path),
            description=f"完全フローテスト\\n処理日時: {datetime.now()}",
            tags=['テスト', 'NB', '自動処理'],
            privacy_status="unlisted"  # 限定公開
        )
        
        if not youtube_url:
            print("❌ YouTubeアップロード失敗")
            return False
        
        print(f"✅ アップロード成功: {youtube_url}")
        
        # 4. YouTube URLをスプレッドシートに記録
        print("\n[4/5] スプレッドシート記録...")
        from automation.youtube_url_logger import YouTubeURLLogger
        
        url_logger = YouTubeURLLogger()
        success = url_logger.add_youtube_url(ad_name, youtube_url)
        
        if success:
            print("✅ YouTube URL記録成功")
        else:
            print("⚠️ YouTube URL記録失敗（処理は継続）")
        
        # 5. クリーンアップ
        print("\n[5/5] クリーンアップ...")
        
        # 一時ファイルを削除
        if video_path.name != "test_input_video.mov" and video_path.exists():
            video_path.unlink()
            print("   一時ダウンロードファイル削除")
        
        if bg_video and Path(bg_video).exists():
            Path(bg_video).unlink()
            print("   背景動画削除")
        
        # 処理済み動画も削除（本番では削除）
        # if output_path.exists():
        #     output_path.unlink()
        #     print("   処理済み動画削除")
        
        print("\n" + "=" * 60)
        print("✅ 完全フローテスト成功！")
        print("=" * 60)
        print(f"\n結果:")
        print(f"  広告名: {ad_name}")
        print(f"  YouTube URL: {youtube_url}")
        print(f"  出力ファイル: {output_path} (保持)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)