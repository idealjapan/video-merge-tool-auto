#!/bin/bash

# AWS EC2への最新コードデプロイスクリプト

set -e

# 設定
INSTANCE_IP="13.231.254.159"
KEY_PATH="$HOME/.ssh/video-merger-key.pem"
REMOTE_USER="ec2-user"
APP_DIR="/home/ec2-user/video-merger-tool"

echo "🚀 AWS EC2へのデプロイを開始します..."

# 1. SSHキーの権限確認
if [ ! -f "$KEY_PATH" ]; then
    echo "❌ SSHキーが見つかりません: $KEY_PATH"
    exit 1
fi
chmod 600 "$KEY_PATH"

# 2. SSH接続テスト
echo "📡 SSH接続を確認中..."
if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no -i "$KEY_PATH" "$REMOTE_USER@$INSTANCE_IP" "echo 'SSH接続成功'" 2>/dev/null; then
    echo "❌ SSH接続に失敗しました"
    echo "IP: $INSTANCE_IP"
    exit 1
fi

# 3. アプリケーションディレクトリの確認
echo "📁 ディレクトリ構造を確認中..."
ssh -i "$KEY_PATH" "$REMOTE_USER@$INSTANCE_IP" "mkdir -p $APP_DIR"

# 4. 必要なファイルをアップロード
echo "📤 ファイルをアップロード中..."

# 個別にファイルをアップロード（エラーチェック付き）
for file in web_app_auto.py video_merger_auto_bg.py background_prompts.py config.py requirements.txt Dockerfile; do
    if [ -f "$file" ]; then
        echo "  - $file をアップロード中..."
        scp -i "$KEY_PATH" "$file" "$REMOTE_USER@$INSTANCE_IP:$APP_DIR/" || {
            echo "❌ $file のアップロードに失敗しました"
            exit 1
        }
    fi
done

# templatesディレクトリをアップロード
if [ -d "templates" ]; then
    echo "  - templates/ をアップロード中..."
    scp -i "$KEY_PATH" -r templates "$REMOTE_USER@$INSTANCE_IP:$APP_DIR/" || {
        echo "❌ templates のアップロードに失敗しました"
        exit 1
    }
fi

# 5. Dockerの再構築とデプロイ
echo "🔧 Dockerイメージを再構築中..."

ssh -i "$KEY_PATH" "$REMOTE_USER@$INSTANCE_IP" << 'EOF'
set -e
cd /home/ec2-user/video-merger-tool

# Docker Composeファイルの確認
if [ ! -f docker-compose.yml ]; then
    echo "⚠️  docker-compose.yml が見つかりません。作成します..."
    cat > docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:8080"
    environment:
      - REPLICATE_API_TOKEN=${REPLICATE_API_TOKEN}
      - FLASK_ENV=production
    volumes:
      - ./videos:/app/videos
      - ./logs:/app/logs
    restart: always
COMPOSE
fi

# 既存のコンテナを停止
echo "🛑 既存のコンテナを停止中..."
docker-compose down || true

# Dockerイメージを再構築
echo "🔨 Dockerイメージを構築中..."
docker-compose build --no-cache

# 環境変数の確認
if [ ! -f .env ]; then
    echo "❌ .envファイルが見つかりません"
    echo "Replicate APIトークンを設定してください"
    exit 1
fi

# Docker Composeを起動
echo "🚀 アプリケーションを起動中..."
docker-compose up -d

# 起動確認
sleep 10
docker-compose ps
docker-compose logs --tail=30
EOF

echo "✅ デプロイが完了しました！"
echo ""
echo "🌐 アクセス情報:"
echo "   URL: http://$INSTANCE_IP"
echo "   ユーザー名: videomerger"
echo "   パスワード: SecurePass2025!"
echo ""
echo "📊 ログを確認: ssh -i $KEY_PATH $REMOTE_USER@$INSTANCE_IP 'cd $APP_DIR && docker-compose logs -f'"