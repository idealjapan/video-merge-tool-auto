#!/bin/bash

# 統一デプロイスクリプト - シンプルで確実

set -e  # エラーで停止

# 設定
INSTANCE_IP="13.231.254.159"
KEY_PATH="$HOME/.ssh/video-merger-key.pem"
REMOTE_USER="ec2-user"
APP_DIR="/home/ec2-user/video-merger-tool"

echo "🚀 動画合成ツールのデプロイを開始します..."
echo "対象: $INSTANCE_IP"

# 1. SSHキーの確認
if [ ! -f "$KEY_PATH" ]; then
    echo "❌ SSHキーが見つかりません: $KEY_PATH"
    exit 1
fi

# 2. 必要なファイルをアップロード
echo "📤 ファイルをアップロード中..."
scp -i "$KEY_PATH" -r \
    web_app_auto.py \
    video_merger_auto_bg.py \
    background_prompts.py \
    config.py \
    requirements.txt \
    Dockerfile \
    docker-compose.yml \
    templates \
    "$REMOTE_USER@$INSTANCE_IP:$APP_DIR/"

# 3. EC2上でDockerを再ビルド・起動
echo "🐳 Dockerを更新中..."
ssh -i "$KEY_PATH" "$REMOTE_USER@$INSTANCE_IP" << 'EOF'
cd /home/ec2-user/video-merger-tool

# 既存のコンテナを停止
docker-compose down

# イメージを再ビルド（キャッシュなし）
docker-compose build --no-cache

# コンテナを起動
docker-compose up -d

# 状態確認
sleep 5
echo ""
echo "📊 状態:"
docker-compose ps
echo ""
echo "📝 最新のログ:"
docker-compose logs --tail=10
EOF

echo ""
echo "✅ デプロイ完了！"
echo ""
echo "🌐 アクセス情報:"
echo "   URL: http://$INSTANCE_IP"
echo "   ユーザー名: videomerger"
echo "   パスワード: SecurePass2025!"
echo ""
echo "📋 ログを見る: ssh -i $KEY_PATH $REMOTE_USER@$INSTANCE_IP 'cd $APP_DIR && docker-compose logs -f'"