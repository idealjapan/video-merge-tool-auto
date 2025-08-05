FROM python:3.9-slim

# FFmpegと日本語フォントのインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY *.py ./
COPY *.sh ./
COPY templates/ ./templates/
COPY static/ ./static/
RUN chmod +x *.sh *.py

# ディレクトリ作成
RUN mkdir -p videos logs

# フォントパスの環境変数設定
ENV FONT_PATH="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# Gunicornのインストール（本番環境用）
RUN pip install gunicorn

# ポート公開
EXPOSE 8080

# デフォルトコマンド（自動背景生成版のWeb UIを起動）
CMD ["gunicorn", "web_app_auto:app", "--bind", "0.0.0.0:8080", "--timeout", "600", "--workers", "2"]