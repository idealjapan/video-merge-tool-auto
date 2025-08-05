# 🚀 動画合成ツール デプロイ成功ガイド

このガイドは、2025年8月5日に成功したデプロイ手順を記録したものです。

## ✅ 成功したデプロイルート

### 1. ローカル環境での準備

#### 1.1 環境変数の設定
```bash
# .env ファイルを作成
cp .env.example .env
# 編集して以下を設定:
# REPLICATE_API_TOKEN=r8_xxxxx（実際のトークン）
```

#### 1.2 ローカルでのテスト（ポート8081使用）
```bash
# Basic認証を一時的に無効化（web_app_auto.pyの@requires_authをコメントアウト）
docker-compose down
docker-compose build --no-cache
docker-compose up -d
# http://localhost:8081 でアクセスして動作確認
```

### 2. AWS デプロイ前の準備

#### 2.1 Basic認証を有効化
web_app_auto.pyの全ての@requires_authのコメントを外す

#### 2.2 ポート設定を本番用に変更
docker-compose.ymlのポートを8080:8080に設定

### 3. AWS EC2 へのデプロイ

#### 3.1 EC2環境のリセット（オプション）
```bash
ssh -i ~/.ssh/video-merger-key.pem ec2-user@13.231.254.159
docker-compose down
docker system prune -a -f --volumes
exit
```

#### 3.2 デプロイ実行（3分で完了）
```bash
./deploy/deploy.sh
```

## 📋 確認済みの設定

### EC2 インスタンス
- IP: 13.231.254.159
- インスタンスタイプ: t2.micro
- リージョン: ap-northeast-1
- セキュリティグループ: ポート8080を開放

### アクセス情報
- URL: http://13.231.254.159:8080
- ユーザー名: videomerger
- パスワード: SecurePass2025!

### 使用するファイル
- `web_app_auto.py` - メインのFlaskアプリケーション
- `video_merger_auto_bg.py` - 動画処理エンジン
- `background_prompts.py` - 背景生成プロンプト
- `config.py` - 設定ファイル
- `templates/index_auto_simple.html` - フロントエンド

## 🔧 トラブルシューティング

### よくある問題と解決方法

1. **認証エラー（401）が出る場合**
   - .envファイルのREPLICATE_API_TOKENが正しいか確認
   - docker-compose downして再度upする

2. **ポートが使用中の場合**
   - ローカル: docker-compose.ymlで別のポート（8081など）を使用
   - AWS: 必ず8080を使用

3. **デプロイが遅い場合**
   - EC2上で`docker system prune -a -f`を実行してクリーンアップ

## 📝 注意事項

- マルチパターン生成機能は削除済み（シングル動画生成のみ）
- 縦型動画の背景回転問題は修正済み
- deployフォルダ内の`deploy.sh`のみを使用（他のスクリプトは使用しない）

## 🚫 使用しないファイル

以下のファイルは古いか重複しているため使用しません：
- `deploy/deploy-to-ec2.sh` - deploy.shに統合済み
- `deploy/create-new-ec2.sh` - 新規EC2作成は不要
- `ec2-setup.sh` - 初期セットアップ済み
- その他のデプロイスクリプト

## 📊 パフォーマンス

- デプロイ時間: 約3分
- 動画生成時間: 5秒動画で約30秒
- メモリ使用量: 1GB以下（t2.micro対応）