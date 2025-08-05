# 動画合成ツール - クイックガイド

## 🎯 これは何？
動画に自動でAI生成背景を追加するツールです。Replicate APIを使用して動的な背景を生成します。

## 🚀 今すぐ使う

### ローカルで試す
```bash
# 環境変数を設定
cp .env.example .env
# .envを編集してREPLICATE_API_TOKENを設定

# 起動
docker-compose up -d

# アクセス
http://localhost:8080
```

### AWSにデプロイ
```bash
./deploy/deploy.sh
# 3分で完了！
```

## 📋 必要なもの
- Docker
- Replicate APIトークン（https://replicate.com で取得）
- AWS EC2（デプロイする場合）

## 🔐 認証情報
- ユーザー名: videomerger
- パスワード: SecurePass2025!

## 📚 詳細ドキュメント
- [デプロイ成功ガイド](DEPLOYMENT_SUCCESS_GUIDE.md) - 確実にデプロイする方法
- [セットアップガイド](SETUP.md) - 初回セットアップ

## ⚠️ 注意
- ポート8080を使用（AWSの場合）
- ローカルで8080が使用中の場合は、docker-compose.ymlで8081に変更可能