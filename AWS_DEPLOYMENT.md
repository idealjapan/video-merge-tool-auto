# AWS デプロイメントガイド

## 🎯 AWS無料枠を最大活用する方法

### オプション1: EC2 + S3（最もシンプル）

**無料枠**:
- EC2 t2.micro: 750時間/月（1年間）
- S3: 5GB ストレージ + 20,000 GET + 2,000 PUT
- データ転送: 15GB/月

**構成**:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Route53   │────▶│  EC2 (Web)  │────▶│     S3      │
│  (optional) │     │   Flask UI   │     │  動画保存    │
└─────────────┘     └─────────────┘     └─────────────┘
```

### オプション2: S3静的サイト + API Gateway + Lambda（サーバーレス）

**無料枠**:
- Lambda: 100万リクエスト/月 + 40万GB秒
- API Gateway: 100万リクエスト/月（12ヶ月）
- S3: 上記と同じ

**注意**: Lambdaは15分のタイムアウト制限があるため、大きな動画には不向き

### オプション3: ECS Fargate（コンテナ）

**料金**: 
- 無料枠なし（約$10-20/月〜）
- でも管理が楽

## 📋 推奨構成：EC2 + S3

最もバランスが良く、無料枠を活用できる構成です。

### セットアップ手順

#### 1. EC2インスタンスの作成

```bash
# AWS CLIまたはコンソールから
# 1. Amazon Linux 2 AMIを選択
# 2. t2.microインスタンスタイプ
# 3. セキュリティグループで80, 443, 22ポートを開放
```

#### 2. EC2にDockerをインストール

```bash
# EC2にSSH接続後
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Docker Composeインストール
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. アプリケーションのデプロイ

```bash
# GitHubからクローン
git clone <your-repo-url>
cd video-merger-tool

# 環境変数設定
cat > .env << EOF
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=your-video-bucket
AWS_REGION=ap-northeast-1
EOF

# 起動
docker-compose -f docker-compose.aws.yml up -d
```

#### 4. S3バケットの設定

```bash
# バケット作成
aws s3 mb s3://your-video-bucket --region ap-northeast-1

# ライフサイクルポリシー（24時間で削除）
aws s3api put-bucket-lifecycle-configuration \
  --bucket your-video-bucket \
  --lifecycle-configuration file://s3-lifecycle.json
```

## 📁 AWS用ファイル

### docker-compose.aws.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:5000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}
      - AWS_REGION=${AWS_REGION}
      - USE_S3=true
    volumes:
      - ./temp:/app/temp
    restart: unless-stopped
```

### s3-lifecycle.json
```json
{
  "Rules": [
    {
      "Id": "DeleteOldVideos",
      "Status": "Enabled",
      "Prefix": "videos/",
      "Expiration": {
        "Days": 1
      }
    }
  ]
}
```

## 💰 コスト見積もり

### 無料枠内での運用（1年目）
- EC2 t2.micro: $0
- S3 (5GB以内): $0
- データ転送 (15GB以内): $0
- **合計: $0/月**

### 無料枠終了後
- EC2 t2.micro: 約$10/月
- S3: 約$1-3/月
- データ転送: 使用量次第
- **合計: 約$15/月**

## 🚀 簡易版：S3直接アップロード

UIなしでS3に直接アップロードする場合：

```bash
# CLIツールとして使用
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 \
  --size 1920x1080 \
  --upload-s3

# S3から署名付きURLで共有
aws s3 presign s3://your-bucket/output.mp4 --expires-in 3600
```

## ⚡ Lambda版（軽量動画のみ）

5分以内で処理できる動画の場合：

1. Lambda関数作成（Python 3.9）
2. FFmpegレイヤー追加
3. API Gateway設定
4. S3バケット連携

※ 制限事項：
- 最大実行時間: 15分
- メモリ: 最大10GB
- 一時ストレージ: 512MB

## 🔧 運用のヒント

1. **CloudWatch監視**
   - CPU使用率アラート設定
   - S3容量アラート設定

2. **コスト最適化**
   - 夜間はインスタンス停止
   - S3 Intelligent-Tiering使用

3. **セキュリティ**
   - IAMロールで権限最小化
   - S3バケットポリシー設定
   - CloudFrontでCDN配信

## 📊 他のAWSサービスとの比較

| サービス | 無料枠 | 適している用途 | 注意点 |
|---------|-------|--------------|--------|
| EC2 | 750時間/月 | 汎用的、UI付き | 管理が必要 |
| Lambda | 100万req/月 | 軽量処理 | 15分制限 |
| ECS | なし | 本番環境 | 有料 |
| Batch | Lambda料金 | バッチ処理 | 複雑 |

## 🎯 結論

**おすすめ**: EC2 (t2.micro) + S3
- 無料枠を最大活用
- UIも設置可能
- 制限が少ない
- 1年後も低コスト

S3への直接アップロード機能も追加すれば、より便利に使えます！