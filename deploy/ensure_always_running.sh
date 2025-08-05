#!/bin/bash

# 常時起動を確実にするスクリプト

echo "🔧 動画合成ツールを24時間365日稼働させる設定..."

# cronジョブを追加（EC2起動時にDockerコンテナを起動）
echo "📝 起動時の自動実行を設定..."
(crontab -l 2>/dev/null; echo "@reboot cd /home/ec2-user/video-merger-tool && /usr/local/bin/docker-compose up -d") | crontab -

# docker-compose.ymlを更新（restart: always）
echo "🐳 Docker再起動ポリシーを「always」に設定..."
cd /home/ec2-user/video-merger-tool
sed -i 's/restart: unless-stopped/restart: always/g' docker-compose.yml

# 現在のコンテナを再起動して設定を反映
echo "🔄 コンテナを再起動して設定を反映..."
docker-compose down
docker-compose up -d

echo "✅ 設定完了！"
echo ""
echo "🎉 これで以下が保証されます:"
echo "  ✓ EC2が再起動しても自動で立ち上がる"
echo "  ✓ Dockerが再起動しても自動で立ち上がる"
echo "  ✓ エラーで停止しても自動で再起動"
echo "  ✓ 24時間365日いつでもアクセス可能"
echo ""
echo "📊 現在の状態:"
docker-compose ps