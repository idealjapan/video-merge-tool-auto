# 動画合成ツール

動画に自動で自然・動物の背景を追加するツール。Replicate APIを使用して背景を生成します。

## 特徴

- 🎬 動画の向き（縦/横）を自動検出
- 🌿 Replicate APIで自然・動物の背景を自動生成
- 📝 日本語の注意書きテキストを自動追加
- 🔧 シンプルなWebインターフェース
- 🐳 Dockerで簡単デプロイ

## デプロイ方法

```bash
./deploy/deploy.sh
```

これだけです！スクリプトが自動的に：
1. ファイルをEC2にアップロード
2. Dockerイメージをビルド
3. コンテナを起動

## ファイル構成

```
.
├── web_app_auto.py          # Flaskアプリケーション
├── video_merger_auto_bg.py  # 動画処理ロジック  
├── background_prompts.py    # 背景プロンプト生成
├── config.py               # 設定（フォントパス等）
├── requirements.txt        # Python依存関係
├── Dockerfile              # Dockerイメージ定義
├── docker-compose.yml      # Docker Compose設定
├── templates/
│   └── index_auto_simple.html  # WebUI
└── deploy/
    ├── deploy.sh           # メインデプロイスクリプト
    └── manual_deploy_steps.md  # 手動デプロイ手順
```

## 必要な環境変数

`.env`ファイルを作成：
```
REPLICATE_API_TOKEN=your_token_here
```

## ローカルでの起動

```bash
docker-compose up -d
```

http://localhost:8080 でアクセス可能

## 本番環境

- URL: http://13.231.254.159
- ユーザー名: videomerger
- パスワード: SecurePass2025!

## 技術仕様

- Python 3.9 + Flask
- FFmpeg（動画処理）
- Replicate API（背景生成）
- Docker + Gunicorn（本番環境）
- Basic認証（セキュリティ）

## トラブルシューティング

### デプロイが失敗する場合

1. EC2インスタンスが起動しているか確認
2. Dockerサービスが動作しているか確認
3. `.env`ファイルが存在するか確認

### ログの確認

```bash
ssh -i ~/.ssh/video-merger-key.pem ec2-user@13.231.254.159 \
  'cd /home/ec2-user/video-merger-tool && docker-compose logs -f'
```