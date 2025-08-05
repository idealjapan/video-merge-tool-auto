# 手動デプロイ手順

EC2インスタンスが応答しない場合の手動デプロイ手順です。

## 1. AWS管理コンソールでEC2を再起動

1. [AWS EC2コンソール](https://ap-northeast-1.console.aws.amazon.com/ec2/home?region=ap-northeast-1#Instances:)にアクセス
2. インスタンス `i-025b510072e4c61be` を選択
3. 「インスタンスの状態」→「再起動」をクリック
4. 再起動完了まで約2-3分待つ

## 2. SSH接続確認

```bash
ssh -i ~/.ssh/video-merger-key.pem ec2-user@13.231.254.159
```

## 3. ファイルアップロード

ローカルから実行：
```bash
# 現在のディレクトリから
cd /Users/shingo/video-merger-tool

# ファイルをアップロード
scp -i ~/.ssh/video-merger-key.pem -r \
    web_app_auto.py \
    video_merger_auto_bg.py \
    background_prompts.py \
    config.py \
    requirements.txt \
    templates \
    Dockerfile \
    ec2-user@13.231.254.159:/home/ec2-user/video-merger-tool/
```

## 4. EC2上でDockerイメージを再構築

EC2にSSH接続後：
```bash
cd /home/ec2-user/video-merger-tool

# 既存のコンテナを停止
docker-compose down

# Dockerイメージを再構築
docker-compose build --no-cache

# コンテナを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

## 5. 動作確認

ブラウザで以下にアクセス：
- URL: http://13.231.254.159
- ユーザー名: videomerger
- パスワード: SecurePass2025!

## トラブルシューティング

### ポート80が開いていない場合
```bash
# セキュリティグループの確認
aws ec2 describe-security-groups --group-names video-merger-sg --region ap-northeast-1
```

### Dockerが起動しない場合
```bash
# Dockerサービスの確認
sudo systemctl status docker

# 必要に応じて再起動
sudo systemctl restart docker
```

### フォントエラーが出る場合
```bash
# 日本語フォントのインストール
sudo yum install -y google-noto-sans-cjk-fonts
```