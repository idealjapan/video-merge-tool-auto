#!/usr/bin/env python3
"""
動画のエンコード設定を確認
"""

import subprocess
import json
from pathlib import Path

def check_video_info(video_path):
    """動画の詳細情報を取得"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

def main():
    print("=" * 60)
    print("🎥 動画エンコード設定確認")
    print("=" * 60)
    
    # test_outputフォルダの動画を確認
    test_dir = Path("test_output")
    if test_dir.exists():
        videos = list(test_dir.glob("*.mp4"))
        
        for video in videos[:3]:  # 最新3つを確認
            print(f"\n📹 {video.name}")
            info = check_video_info(str(video))
            
            if info:
                # ビデオストリーム情報
                for stream in info.get('streams', []):
                    if stream['codec_type'] == 'video':
                        print(f"   解像度: {stream.get('width')}x{stream.get('height')}")
                        print(f"   コーデック: {stream.get('codec_name')}")
                        print(f"   ビットレート: {stream.get('bit_rate', 'N/A')}")
                        print(f"   フレームレート: {stream.get('r_frame_rate')}")
                
                # ファイル情報
                format_info = info.get('format', {})
                size_mb = int(format_info.get('size', 0)) / (1024 * 1024)
                bitrate = int(format_info.get('bit_rate', 0)) / 1000
                print(f"   ファイルサイズ: {size_mb:.1f} MB")
                print(f"   総ビットレート: {bitrate:.0f} kbps")
                print(f"   長さ: {float(format_info.get('duration', 0)):.1f}秒")
    
    print("\n" + "=" * 60)
    print("💡 推奨設定:")
    print("   - ビットレート: 2000-4000 kbps (縦型動画)")
    print("   - プリセット: faster または fast")
    print("   - 解像度: 1080x1920 (9:16)")
    print("=" * 60)

if __name__ == "__main__":
    main()