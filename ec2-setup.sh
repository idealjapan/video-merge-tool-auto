#!/bin/bash

# EC2 Amazon Linux 2 セットアップスクリプト

echo "=== EC2セットアップ開始 ==="

# システムアップデート
echo "1. システムアップデート中..."
sudo yum update -y

# Dockerインストール
echo "2. Dockerをインストール中..."
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Docker Composeインストール
echo "3. Docker Composeをインストール中..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Gitインストール
echo "4. Gitをインストール中..."
sudo yum install git -y

# アプリケーションディレクトリ作成
echo "5. アプリケーションディレクトリを作成中..."
mkdir -p ~/video-merger-tool
cd ~/video-merger-tool

# 環境変数ファイルのテンプレート作成
echo "6. 環境変数テンプレートを作成中..."
cat > .env.template << EOF
# AWS設定
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=ap-northeast-1
USE_S3=true

# アプリケーション設定
FLASK_ENV=production
MAX_FILE_SIZE=500000000
EOF

# systemdサービスファイル作成
echo "7. systemdサービスを設定中..."
sudo tee /etc/systemd/system/video-merger.service > /dev/null << EOF
[Unit]
Description=Video Merger Tool
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/video-merger-tool
ExecStart=/usr/local/bin/docker-compose up
ExecStop=/usr/local/bin/docker-compose down
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Nginxインストール（オプション）
echo "8. Nginxをインストール中..."
sudo amazon-linux-extras install nginx1 -y

# Nginx設定
sudo tee /etc/nginx/conf.d/video-merger.conf > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

# S3バケット作成スクリプト
echo "9. S3セットアップスクリプトを作成中..."
cat > setup-s3.sh << 'EOF'
#!/bin/bash

# S3バケット名を引数から取得
BUCKET_NAME=$1

if [ -z "$BUCKET_NAME" ]; then
    echo "Usage: ./setup-s3.sh <bucket-name>"
    exit 1
fi

# バケット作成
aws s3 mb s3://$BUCKET_NAME --region ap-northeast-1

# CORS設定
cat > cors.json << CORS_EOF
{
    "CORSRules": [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": []
        }
    ]
}
CORS_EOF

aws s3api put-bucket-cors --bucket $BUCKET_NAME --cors-configuration file://cors.json

# ライフサイクルポリシー（24時間で削除）
cat > lifecycle.json << LIFECYCLE_EOF
{
    "Rules": [
        {
            "Id": "DeleteOldVideos",
            "Status": "Enabled",
            "Prefix": "uploads/",
            "Expiration": {
                "Days": 1
            }
        },
        {
            "Id": "DeleteOldOutputs",
            "Status": "Enabled",
            "Prefix": "outputs/",
            "Expiration": {
                "Days": 1
            }
        }
    ]
}
LIFECYCLE_EOF

aws s3api put-bucket-lifecycle-configuration --bucket $BUCKET_NAME --lifecycle-configuration file://lifecycle.json

echo "S3バケット '$BUCKET_NAME' のセットアップが完了しました"
rm cors.json lifecycle.json
EOF

chmod +x setup-s3.sh

echo "=== セットアップ完了 ==="
echo ""
echo "次の手順:"
echo "1. 再ログインして、Dockerグループを有効化:"
echo "   exit"
echo "   ssh ec2-user@<your-ip>"
echo ""
echo "2. リポジトリをクローン:"
echo "   git clone <your-repo-url> ."
echo ""
echo "3. 環境変数を設定:"
echo "   cp .env.template .env"
echo "   nano .env  # AWS認証情報を入力"
echo ""
echo "4. S3バケットをセットアップ:"
echo "   ./setup-s3.sh your-bucket-name"
echo ""
echo "5. アプリケーションを起動:"
echo "   docker-compose up -d"
echo ""
echo "6. サービスを有効化（自動起動）:"
echo "   sudo systemctl enable video-merger"
echo "   sudo systemctl start video-merger"