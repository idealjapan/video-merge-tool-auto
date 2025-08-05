#!/bin/bash

echo "🐳 ローカルでDockerを使ってテスト..."

# .envファイルの確認
if [ ! -f .env ]; then
    echo "❌ .envファイルが見つかりません"
    echo "cp .env.example .env してAPIキーを設定してください"
    exit 1
fi

# Dockerビルドと起動
echo "📦 Dockerイメージをビルド中..."
docker-compose build --no-cache

echo "🚀 コンテナを起動中..."
docker-compose up -d

echo ""
echo "✅ 起動完了！"
echo "🌐 URL: http://localhost:8080"
echo "👤 ユーザー名: videomerger"
echo "🔑 パスワード: SecurePass2025!"
echo ""
echo "📋 ログを見る: docker-compose logs -f"
echo "🛑 停止: docker-compose down"