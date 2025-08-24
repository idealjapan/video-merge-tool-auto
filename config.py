import os
import platform

class Config:
    """アプリケーション設定"""
    
    # 基本設定
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'outputs'
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    
    # フォント設定（OS別）
    @staticmethod
    def get_font_paths():
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return [
                "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/Library/Fonts/Arial Unicode.ttf",
                "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
            ]
        elif system == "Linux":
            return [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
                "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf",
                "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
        else:  # Windows
            return [
                "C:/Windows/Fonts/msgothic.ttc",
                "C:/Windows/Fonts/YuGothB.ttc",
                "C:/Windows/Fonts/YuGothic.ttf",
                "C:/Windows/Fonts/arial.ttf"
            ]
    
    @staticmethod
    def get_font_path():
        """最初に見つかった有効なフォントパスを返す"""
        font_paths = Config.get_font_paths()
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        return None
    
    # デフォルトテキスト
    DEFAULT_DISCLAIMER_TEXT = "※結果には個人差があり成果を保証するものではありません"
    
    # 動画処理設定
    DEFAULT_MAIN_SCALE = 0.8
    HORIZONTAL_FONT_SIZE = 32
    VERTICAL_FONT_SIZE = 28
    TEXT_BOX_PADDING = 15
    
    # Replicate API設定
    REPLICATE_MODEL_VERSION = "b6519549e375404f45af5ef2e4b01f651d4014f3b57d3270b430e0523bad9835"
    VIDEO_DURATION = 5  # 秒
    VIDEO_RESOLUTION = "480p"