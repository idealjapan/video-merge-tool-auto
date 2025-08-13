import os
from pathlib import Path

# ベースディレクトリ
BASE_DIR = Path(__file__).parent.parent

# Google Sheets設定
SPREADSHEET_NAME = "YT動画URL"  # 既存のスプレッドシートを使用
SPREADSHEET_ID = "1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U"  # YT動画URLスプレッドシート
DISAPPROVED_SHEET_NAME = "不承認広告"
STOCK_SHEET_NAME = "動画ストック"

# 認証情報パス
GOOGLE_SERVICE_ACCOUNT_FILE = BASE_DIR / "credentials" / "google_service_account.json"
YOUTUBE_CLIENT_SECRETS_FILE = BASE_DIR / "credentials" / "youtube_client_secrets.json"
YOUTUBE_CREDENTIALS_FILE = BASE_DIR / "credentials" / "youtube_oauth_token.json"

# 処理設定
VIDEO_TEMP_DIR = BASE_DIR / "temp_videos"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

# 動画処理設定
DEFAULT_BACKGROUND_STYLE = "nature"  # nature, cityscape, abstract, ocean, forest
MAX_PROCESSING_TIME = 600  # 最大処理時間（秒）

# YouTube設定
YOUTUBE_CATEGORY_ID = "22"  # People & Blogs
YOUTUBE_PRIVACY_STATUS = "unlisted"  # private, unlisted, public

# ログ設定
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 既存のEC2環境設定
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

# エラー通知設定（オプション）
ERROR_NOTIFICATION_EMAIL = None  # エラー時に通知するメールアドレス

# 処理間隔設定
PROCESSING_INTERVAL_MINUTES = 5  # cronでの実行間隔