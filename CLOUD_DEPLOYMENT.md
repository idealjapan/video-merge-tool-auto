# クラウドデプロイメントガイド

## 🌐 Web UIについて

シンプルで使いやすいWebインターフェースを作成しました。機能：
- ドラッグ&ドロップでファイルアップロード
- リアルタイム進捗表示
- プリセット設定
- モバイル対応レスポンシブデザイン

## 🚀 推奨デプロイ方法

### オプション1: Render.com（推奨・無料枠あり）

**メリット**: 
- 無料プランあり
- 自動デプロイ
- Docker対応
- SSL証明書自動設定

**デプロイ手順**:
```bash
1. GitHubにリポジトリをプッシュ
2. render.comでアカウント作成
3. "New Web Service"をクリック
4. GitHubリポジトリを接続
5. 自動的にrender.yamlを検出してデプロイ
```

### オプション2: Railway（簡単・$5/月〜）

**メリット**: 
- ワンクリックデプロイ
- 環境変数の管理が簡単
- 自動スケーリング

**デプロイ手順**:
```bash
1. railway.appでアカウント作成
2. "New Project" → "Deploy from GitHub"
3. リポジトリを選択
4. railway.jsonを自動検出してデプロイ
```

### オプション3: Heroku（$5-7/月）

**メリット**: 
- 安定性が高い
- アドオンが豊富
- CI/CD統合

**デプロイ手順**:
```bash
# Heroku CLIをインストール後
heroku create your-app-name
heroku stack:set container
git push heroku main
```

### オプション4: Google Cloud Run（従量課金）

**メリット**: 
- 完全なスケーラビリティ
- 使用分のみ課金
- 高性能

**デプロイ手順**:
```bash
# Google Cloud SDKインストール後
gcloud run deploy video-merger \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300
```

## 📱 ローカルでのテスト

デプロイ前にローカルでテスト：

```bash
# 方法1: Python直接実行
pip install -r requirements.txt
python web_app.py

# 方法2: Docker使用
docker build -t video-merger .
docker run -p 5000:5000 video-merger

# ブラウザで http://localhost:5000 にアクセス
```

## ⚙️ 環境変数設定

各クラウドサービスで以下の環境変数を設定：

```env
FLASK_ENV=production
MAX_FILE_SIZE=500000000  # 500MB
PORT=5000  # 一部のサービスでは自動設定
```

## 🔒 セキュリティ設定

### 1. アップロードサイズ制限
```python
# web_app.py内で設定済み
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
```

### 2. ファイルタイプ制限
```python
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
```

### 3. 自動クリーンアップ
24時間経過したファイルは自動削除

## 📊 料金比較

| サービス | 無料枠 | 有料プラン | 特徴 |
|---------|-------|----------|------|
| Render | 750時間/月 | $7/月〜 | Docker対応、自動SSL |
| Railway | $5クレジット | $5/月〜 | 簡単デプロイ |
| Heroku | なし | $5-7/月 | 安定性高い |
| Cloud Run | 200万リクエスト/月 | 従量課金 | スケーラブル |

## 🚨 注意事項

1. **ストレージ**: 
   - 動画ファイルは一時的
   - 24時間で自動削除
   - 永続保存が必要な場合はS3等を追加

2. **処理時間**:
   - 無料プランは処理時間制限あり
   - 大きなファイルは有料プランを推奨

3. **同時接続数**:
   - 無料プランは制限あり
   - 本番環境では有料プラン推奨

## 🔧 カスタマイズ

### ロゴ・デザイン変更
`templates/index.html`を編集

### 機能追加
- S3連携
- データベース保存
- ユーザー認証
- バッチ処理

## 📞 サポート

デプロイで問題が発生した場合：
1. エラーログを確認
2. 環境変数を再確認
3. Dockerイメージのビルドログを確認

---

**次のステップ**: 
1. GitHubにコードをプッシュ
2. 好きなクラウドサービスを選択
3. 上記の手順に従ってデプロイ
4. チームにURLを共有！