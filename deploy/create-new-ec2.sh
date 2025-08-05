#!/bin/bash

# 新しいEC2インスタンスを作成してデプロイ

set -e

REGION="ap-northeast-1"
INSTANCE_TYPE="t2.micro"
KEY_NAME="video-merger-key-new"
SECURITY_GROUP_NAME="video-merger-sg-new"

echo "🚀 新しいEC2インスタンスを作成します..."

# 1. キーペアの作成（既存のものがない場合）
if [ ! -f "$HOME/.ssh/${KEY_NAME}.pem" ]; then
    echo "🔑 新しいキーペアを作成中..."
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text \
        --region $REGION > "$HOME/.ssh/${KEY_NAME}.pem"
    chmod 600 "$HOME/.ssh/${KEY_NAME}.pem"
fi

# 2. セキュリティグループの作成
echo "🛡️  セキュリティグループを作成中..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP_NAME \
    --description "Security group for Video Merger Tool" \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
        --group-names $SECURITY_GROUP_NAME \
        --region $REGION \
        --query 'SecurityGroups[0].GroupId' \
        --output text)

# SSH (22) と HTTP (80) を許可
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 22 --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 80 --cidr 0.0.0.0/0 \
    --region $REGION 2>/dev/null || true

# 3. 最新のAmazon Linux 2 AMIを取得
AMI_ID=$(aws ssm get-parameters \
    --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 \
    --region $REGION \
    --query 'Parameters[0].Value' \
    --output text)

# 4. インスタンスを起動
echo "🖥️  EC2インスタンスを起動中..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --region $REGION \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=video-merger-tool-new}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "⏳ インスタンスの起動を待っています..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# パブリックIPを取得
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ インスタンスが起動しました！"
echo "   インスタンスID: $INSTANCE_ID"
echo "   パブリックIP: $PUBLIC_IP"

# 5. 初期セットアップスクリプトを実行
echo "🔧 初期セットアップを実行中..."
sleep 30  # SSHが利用可能になるまで待機

# セットアップコマンドを実行
ssh -o StrictHostKeyChecking=no -i "$HOME/.ssh/${KEY_NAME}.pem" ec2-user@$PUBLIC_IP << 'EOF'
# Dockerのインストール
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo chkconfig docker on

# Docker Composeのインストール
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Nginxのインストール
sudo amazon-linux-extras install nginx1 -y
sudo systemctl start nginx
sudo systemctl enable nginx

# アプリケーションディレクトリの作成
mkdir -p /home/ec2-user/video-merger-tool
EOF

echo "🎉 新しいEC2インスタンスの準備が完了しました！"
echo ""
echo "次のステップ:"
echo "1. ファイルをアップロード:"
echo "   scp -i ~/.ssh/${KEY_NAME}.pem -r * ec2-user@$PUBLIC_IP:/home/ec2-user/video-merger-tool/"
echo ""
echo "2. SSHで接続:"
echo "   ssh -i ~/.ssh/${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""
echo "3. .envファイルを作成してReplicate APIキーを設定"