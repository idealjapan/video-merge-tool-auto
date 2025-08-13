#!/usr/bin/env python3
"""
NBチャンネルへのYouTubeアップロードテスト
"""
import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from automation.youtube_uploader_unified import YouTubeUploaderUnified

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_nb_upload():
    """NBチャンネルへのテストアップロード"""
    
    print("=" * 60)
    print("NBチャンネル YouTubeアップロードテスト")
    print("=" * 60)
    
    # 既存のテスト動画を使用
    test_video = Path("test_output")
    if test_video.exists():
        videos = list(test_video.glob("*.mp4"))
        if videos:
            video_path = videos[0]  # 最初の動画を使用
            print(f"\nテスト動画: {video_path}")
        else:
            print("❌ test_outputフォルダに動画がありません")
            return
    else:
        print("❌ test_outputフォルダがありません")
        return
    
    # アップローダー初期化
    uploader = YouTubeUploaderUnified()
    
    # NBチャンネルにアップロード
    ad_name = "NB_テスト広告動画"
    
    print(f"\n広告名: {ad_name}")
    print("アップロード先: NBチャンネル")
    print("\n認証が必要な場合はブラウザが開きます。")
    print("NBチャンネルのGoogleアカウントでログインしてください。\n")
    
    try:
        youtube_url = uploader.upload_video(
            ad_name=ad_name,
            video_path=str(video_path),
            description="自動アップロードテスト（NBチャンネル）",
            tags=["テスト", "NB", "自動アップロード"],
            privacy_status="unlisted"  # 限定公開（URLを知っている人だけ視聴可能）
        )
        
        if youtube_url:
            print("\n" + "=" * 60)
            print("✅ アップロード成功！")
            print(f"URL: {youtube_url}")
            print("=" * 60)
        else:
            print("\n❌ アップロード失敗")
            
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nb_upload()