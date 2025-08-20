#!/usr/bin/env python3
"""
GitHub Actions環境でのフォント検証スクリプト
"""
import os
import platform
import subprocess

def check_fonts():
    """利用可能なフォントを確認"""
    print("=" * 60)
    print("Font Check for GitHub Actions")
    print("=" * 60)
    print(f"Platform: {platform.system()}")
    print(f"Platform details: {platform.platform()}")
    
    # Noto CJKフォントのパス
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
        "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    ]
    
    print("\n📁 Checking font files:")
    found_fonts = []
    for font_path in font_paths:
        if os.path.exists(font_path):
            size = os.path.getsize(font_path) / (1024 * 1024)  # MB
            print(f"  ✅ {font_path} ({size:.1f} MB)")
            found_fonts.append(font_path)
        else:
            print(f"  ❌ {font_path}")
    
    # fonts-noto-cjkパッケージの内容を確認
    print("\n📦 Checking installed font packages:")
    try:
        result = subprocess.run(
            ["dpkg", "-L", "fonts-noto-cjk"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("  fonts-noto-cjk package files:")
            for line in result.stdout.split('\n'):
                if '.ttc' in line or '.otf' in line or '.ttf' in line:
                    print(f"    - {line}")
    except Exception as e:
        print(f"  Could not check package: {e}")
    
    # ffmpegで利用可能なフォントを確認
    print("\n🎬 Checking ffmpeg font access:")
    try:
        # テスト用の小さな動画を作成
        test_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "color=c=blue:s=320x240:d=1",
            "-vf", "drawtext=text='テスト':fontsize=24:fontcolor=white:x=10:y=10",
            "-f", "null",
            "-"
        ]
        
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ FFmpeg can render text without font file")
        else:
            print("  ❌ FFmpeg needs explicit font file")
            print(f"  Error: {result.stderr[:200]}")
            
        # フォントファイルを指定してテスト
        if found_fonts:
            test_cmd_with_font = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", "color=c=blue:s=320x240:d=1",
                "-vf", f"drawtext=fontfile='{found_fonts[0]}':text='日本語テスト':fontsize=24:fontcolor=white:x=10:y=10",
                "-f", "null",
                "-"
            ]
            
            result = subprocess.run(test_cmd_with_font, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ FFmpeg can render Japanese with: {found_fonts[0]}")
            else:
                print(f"  ❌ FFmpeg error with font file")
                
    except Exception as e:
        print(f"  FFmpeg test failed: {e}")
    
    print("\n" + "=" * 60)
    if found_fonts:
        print(f"✅ Found {len(found_fonts)} Japanese fonts")
        print(f"Recommended font: {found_fonts[0]}")
    else:
        print("❌ No Japanese fonts found!")
        print("Install with: sudo apt-get install fonts-noto-cjk")
    print("=" * 60)

if __name__ == "__main__":
    check_fonts()