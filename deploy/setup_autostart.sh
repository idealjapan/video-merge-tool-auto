#!/bin/bash

# EC2自動起動設定スクリプト
# これを実行すると、EC2が再起動してもDockerコンテナが自動で立ち上がります

echo "🚀 EC2自動起動設定を開始します..."

# systemdサービスファイルの内容
cat << 'EOF' > /tmp/video-merger.service
[Unit]
Description=Video Merger Tool Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ec2-user/video-merger-tool
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ec2-user
Group=ec2-user

[Install]
WantedBy=multi-user.target
EOF

echo "📝 systemdサービスファイルを作成しました"

# サービスファイルを適切な場所にコピー（sudo権限が必要）
sudo cp /tmp/video-merger.service /etc/systemd/system/

# サービスを有効化
sudo systemctl daemon-reload
sudo systemctl enable video-merger.service
sudo systemctl start video-merger.service

echo "✅ 自動起動設定が完了しました！"
echo ""
echo "📊 確認方法:"
echo "  sudo systemctl status video-merger"
echo ""
echo "🔄 これで以下の時でも自動起動します:"
echo "  - EC2インスタンスの再起動"
echo "  - AWSメンテナンス後の再起動"
echo "  - 予期しない停止からの復旧"