#!/usr/bin/env python3
"""
日本語フォントを確実に見つけるヘルパー
"""
import os
import platform
import logging

logger = logging.getLogger(__name__)

def find_japanese_font():
    """
    システムから日本語フォントを探す
    優先順位の高い順にチェックして、最初に見つかったものを返す
    """
    system = platform.system()
    
    # システム別のフォントパス（優先順位順）
    if system == "Darwin":  # macOS
        font_candidates = [
            "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    elif system == "Linux":
        # Ubuntu/Debian系のパス
        font_candidates = [
            # fonts-noto-cjk パッケージ（最優先）
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            # 別の場所の可能性
            "/usr/share/fonts/opentype/noto-cjk/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto-cjk/NotoSansCJK-Regular.ttc",
            # その他の日本語フォント
            "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
            "/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf",
            # フォールバック（ASCII のみ）
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    else:  # Windows
        font_candidates = [
            "C:/Windows/Fonts/msgothic.ttc",
            "C:/Windows/Fonts/YuGothB.ttc",
            "C:/Windows/Fonts/arial.ttf",
        ]
    
    # 存在するフォントを探す
    for font_path in font_candidates:
        if os.path.exists(font_path):
            logger.info(f"Found font: {font_path}")
            return font_path
    
    # 見つからない場合は、動的に探す
    logger.warning("No predefined font found. Searching dynamically...")
    
    # Linuxの場合、fonts-noto-cjkパッケージのファイルを動的に探す
    if system == "Linux":
        search_dirs = [
            "/usr/share/fonts/opentype",
            "/usr/share/fonts/truetype",
            "/usr/share/fonts",
        ]
        
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for root, dirs, files in os.walk(search_dir):
                    for file in files:
                        # NotoSansCJKを優先
                        if 'NotoSansCJK' in file and file.endswith(('.ttc', '.otf', '.ttf')):
                            font_path = os.path.join(root, file)
                            logger.info(f"Found Noto CJK font: {font_path}")
                            return font_path
                        # 他の日本語フォント
                        if ('japan' in file.lower() or 'gothic' in file.lower() or 'mincho' in file.lower()) \
                           and file.endswith(('.ttc', '.otf', '.ttf')):
                            font_path = os.path.join(root, file)
                            logger.info(f"Found Japanese font: {font_path}")
                            return font_path
    
    logger.error("No Japanese font found on the system")
    return None


def test_font():
    """フォント検索をテスト"""
    import subprocess
    
    font = find_japanese_font()
    if font:
        print(f"✅ Found font: {font}")
        
        # FFmpegでテスト
        test_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "color=c=blue:s=320x240:d=1",
            "-vf", f"drawtext=fontfile='{font}':text='日本語テスト':fontsize=24:fontcolor=white:x=10:y=10",
            "-f", "null",
            "-",
            "-v", "error"
        ]
        
        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ FFmpeg can use this font successfully")
            else:
                print(f"❌ FFmpeg error: {result.stderr}")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("❌ No font found")
        print("For Linux, install: sudo apt-get install fonts-noto-cjk")
        print("For macOS, Japanese fonts should be pre-installed")


if __name__ == "__main__":
    test_font()