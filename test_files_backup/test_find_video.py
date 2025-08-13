#!/usr/bin/env python3
"""
特定の広告名で動画を検索・ダウンロードするテスト
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from automation.google_drive_finder import GoogleDriveFinder

def test_find_video(ad_name="変わらない勇気"):
    print("=" * 60)
    print(f"Google Drive 動画検索テスト: 「{ad_name}」")
    print("=" * 60)
    
    try:
        # 1. 接続
        finder = GoogleDriveFinder()
        print("✅ API接続成功")
        
        # 2. 動画一覧を確認
        print("\n📹 現在の動画一覧:")
        videos = finder.list_videos()
        for v in videos:
            print(f"  - {v['name']}: {v['size_mb']:.1f}MB")
        
        # 3. 特定の広告名で検索
        print(f"\n🔍 「{ad_name}」を検索中...")
        video_path = finder.find_and_download(ad_name)
        
        if video_path:
            print(f"\n✅ 動画が見つかりました！")
            print(f"  ダウンロード先: {video_path}")
            print(f"  ファイルサイズ: {video_path.stat().st_size / (1024*1024):.1f}MB")
            print(f"  拡張子: {video_path.suffix}")
            
            # ダウンロードしたファイルの情報を表示
            from video_merger_auto_bg import VideoMergerWithAutoBG
            merger = VideoMergerWithAutoBG()
            video_info = merger.get_video_info(str(video_path))
            print(f"\n📊 動画情報:")
            print(f"  解像度: {video_info['width']}x{video_info['height']}")
            print(f"  長さ: {video_info['duration']:.1f}秒")
            print(f"  向き: {video_info['orientation']}")
            
            # テストファイルを削除
            video_path.unlink()
            print("\n🗑️ テストファイルは削除しました")
        else:
            print(f"\n❌ 「{ad_name}」が見つかりませんでした")
            print("\n考えられる原因:")
            print("  1. ファイル名が異なる")
            print("  2. フォルダの共有設定が正しくない")
            print("  3. まだアップロードが完了していない")
        
        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # コマンドライン引数があればそれを使用
    import sys
    if len(sys.argv) > 1:
        ad_name = sys.argv[1]
    else:
        ad_name = "変わらない勇気"
    
    test_find_video(ad_name)