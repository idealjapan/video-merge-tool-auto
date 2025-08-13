# 広告動画自動処理システム セットアップガイド

## 概要
このシステムは、Google スプレッドシートから不承認広告を検出し、自動で背景合成処理を行い、YouTubeにアップロードします。

## システム構成
- **Google Sheets**: 広告管理データベース
- **Python (EC2)**: 処理エンジン
- **YouTube API**: 動画アップロード
- **cron**: 定期実行（5分ごと）

## セットアップ手順

### 1. Google Cloud Console設定

#### Service Account作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新規プロジェクトを作成または既存プロジェクトを選択
3. 「APIとサービス」→「認証情報」
4. 「認証情報を作成」→「サービスアカウント」
5. 必要事項を入力して作成
6. 作成したサービスアカウントをクリック
7. 「キー」タブ→「鍵を追加」→「新しい鍵を作成」→「JSON」
8. ダウンロードしたJSONを `credentials/google_service_account.json` として保存

#### Google Sheets API有効化
1. 「APIとサービス」→「ライブラリ」
2. 「Google Sheets API」を検索して有効化
3. 「Google Drive API」も同様に有効化

#### YouTube API設定
1. 「YouTube Data API v3」を検索して有効化
2. 「認証情報を作成」→「OAuth クライアント ID」
3. アプリケーションの種類：「デスクトップアプリ」
4. 作成後、JSONをダウンロード
5. `credentials/youtube_client_secrets.json` として保存

### 2. スプレッドシート準備

#### スプレッドシート構成
```
シート1: 不承認広告
| 広告名 | キャンペーン | ステータス | 処理済み | 処理日時 | 不承認理由 |
|--------|------------|-----------|---------|---------|-----------|
| 広告A  | 春セール    | 不承認     | FALSE   |         | ポリシー違反 |

シート2: 動画ストック  
| 広告名 | 元動画URL | 背景スタイル | 合成済みURL | 更新日時 | タイトル |
|--------|----------|------------|------------|---------|---------|
| 広告A  | https://... | nature   |            |         | 春の新商品 |
```

#### アクセス権限設定
1. スプレッドシートを開く
2. 「共有」ボタンをクリック
3. サービスアカウントのメールアドレスを追加（JSONファイル内のclient_email）
4. 「編集者」権限を付与

### 3. EC2環境設定

```bash
# リポジトリに移動
cd /home/ec2-user/video-merger-tool

# セットアップスクリプト実行
./setup_automation.sh

# 設定ファイル編集
nano automation/config.py
# SPREADSHEET_NAME を実際の名前に変更

# 初回のYouTube認証（ローカルで実行推奨）
python3 -c "from automation.youtube_uploader import YouTubeUploader; YouTubeUploader()"
# ブラウザが開くので認証を完了
```

### 4. cron設定

```bash
# crontab編集
crontab -e

# 以下を追加（5分ごとに実行）
*/5 * * * * cd /home/ec2-user/video-merger-tool && /usr/bin/python3 automation/ad_processor.py >> logs/cron.log 2>&1
```

### 5. 動作確認

```bash
# 手動実行テスト
python3 automation/ad_processor.py

# ログ確認
tail -f logs/ad_processor_*.log

# cronログ確認
tail -f logs/cron.log
```

## トラブルシューティング

### Google Sheets接続エラー
- Service Account JSONが正しい場所にあるか確認
- スプレッドシートの共有設定を確認
- API有効化を確認

### YouTube アップロードエラー
- OAuth認証が完了しているか確認
- APIクォータ制限に達していないか確認
- 動画ファイルが正しく生成されているか確認

### 背景合成エラー
- Replicate API トークンが設定されているか確認
- 元動画のURLが有効か確認
- ディスク容量を確認

## 監視とメンテナンス

### ログローテーション設定
```bash
# /etc/logrotate.d/ad_processor
/home/ec2-user/video-merger-tool/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### 処理状況の確認方法
1. スプレッドシートの「処理済み」列を確認
2. 「エラーログ」シートでエラーを確認
3. EC2のログファイルで詳細を確認

## セキュリティ注意事項
- 認証情報ファイルは絶対にGitにコミットしない
- `.gitignore`に以下を追加：
  ```
  credentials/
  *.json
  youtube_oauth_token.json
  ```
- EC2のセキュリティグループは必要最小限に

## サポート
問題が発生した場合は、以下を確認してください：
1. `logs/ad_processor_*.log` の最新エラー
2. スプレッドシートの「エラーログ」シート
3. YouTube APIのクォータ状況