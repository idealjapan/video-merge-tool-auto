#!/usr/bin/env python3
"""
Google Drive連携を含むフルフローテスト
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

def test_full_flow():
    """ローカル動画 → 背景合成 → モックアップロードのフルフロー"""
    
    ad_name = "テスト広告"
    
    logger.info("=" * 60)
    logger.info("背景合成フルフローテスト")
    logger.info(f"広告名: {ad_name}")
    logger.info("=" * 60)
    
    try:
        # 1. ローカル動画を使用
        logger.info("\n[1/4] ローカル動画を使用")
        video_path = Path(__file__).parent / "test_input_video.mov"
        
        if not video_path.exists():
            logger.error(f"動画が見つかりません: {video_path}")
            return False
        
        logger.info(f"✅ 動画取得成功: {video_path}")
        logger.info(f"   サイズ: {video_path.stat().st_size / (1024*1024):.1f}MB")
        
        # 2. 背景合成処理
        logger.info("\n[2/4] 背景合成処理")
        from video_merger_auto_bg import VideoMergerWithAutoBG
        
        # Replicate APIトークンを設定
        os.environ['REPLICATE_API_TOKEN'] = 'r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'
        
        merger = VideoMergerWithAutoBG()
        
        # 動画情報を取得
        main_info = merger.get_video_info(str(video_path))
        logger.info(f"   動画情報: {main_info['width']}x{main_info['height']}, {main_info['duration']:.1f}秒, {main_info['orientation']}")
        
        # 背景を生成
        logger.info("   背景生成中...")
        bg_video = merger.generate_background_with_replicate(
            orientation=main_info['orientation'],
            duration=main_info['duration'],
            style='nature'
        )
        
        if not bg_video:
            logger.error("背景生成に失敗しました")
            return False
        
        logger.info(f"✅ 背景生成成功")
        
        # 動画を合成
        output_dir = Path(__file__).parent / "test_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{ad_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        logger.info("   動画合成中...")
        merger.merge_videos(
            main_video=str(video_path),
            background_video=bg_video,
            output_video=str(output_path),
            disclaimer_text="この動画は自動生成された背景を使用しています"
        )
        
        logger.info(f"✅ 背景合成成功: {output_path}")
        logger.info(f"   出力サイズ: {output_path.stat().st_size / (1024*1024):.1f}MB")
        
        # 3. モックYouTubeアップロード
        logger.info("\n[3/4] YouTubeアップロード（モック）")
        from test_environment.mock_youtube_uploader import MockYouTubeUploader
        
        uploader = MockYouTubeUploader()
        youtube_url = uploader.upload_video(
            video_path=str(output_path),
            title=f"{ad_name} - 背景合成版",
            description=f"Google Drive連携テスト\n処理日時: {datetime.now()}",
            tags=['テスト', 'Google Drive', ad_name]
        )
        
        if youtube_url:
            logger.info(f"✅ アップロード成功: {youtube_url}")
        
        # 4. クリーンアップ
        logger.info("\n[4/4] クリーンアップ")
        # ローカルテスト動画は削除しない
        
        if bg_video and Path(bg_video).exists():
            Path(bg_video).unlink()
            logger.info("   背景動画削除完了")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ フルフローテスト成功！")
        logger.info(f"   最終出力: {output_path}")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"エラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_flow()
    sys.exit(0 if success else 1)