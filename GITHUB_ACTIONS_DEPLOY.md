# GitHub Actions デプロイ手順

## 1. リポジトリの準備

### 現在のリポジトリを確認
```bash
git remote -v
```

### まだリポジトリがない場合
1. GitHubで新しいリポジトリを作成（プライベート推奨）
2. ローカルでプッシュ：
```bash
git init
git add .
git commit -m "GitHub Actions deployment"
git branch -M main
git remote add origin https://github.com/[your-username]/video-merger-tool-auto.git
git push -u origin main
```

## 2. GitHub Secretsの設定

### 設定スクリプトを実行
```bash
cd /Users/shingo/Desktop/アプリ開発/video-merger-tool-Auto
./setup_github_secrets.sh
```

### GitHubで設定
1. リポジトリの Settings → Secrets and variables → Actions
2. "New repository secret" をクリック
3. 以下の6つのSecretsを追加：

| Secret名 | 説明 | 取得方法 |
|---------|------|---------|
| GOOGLE_SERVICE_ACCOUNT_JSON | Google API認証 | スクリプトの出力をコピー |
| REPLICATE_API_TOKEN | AI背景生成API | r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio |
| TOKEN_NB_PICKLE | NBチャンネル認証 | base64エンコード済み |
| TOKEN_OM_PICKLE | OMチャンネル認証 | base64エンコード済み |
| TOKEN_SBC_PICKLE | SBCチャンネル認証 | base64エンコード済み |
| CLIENT_SECRETS_JSON | YouTube OAuth設定 | スクリプトの出力をコピー |

## 3. デプロイ

### ファイルをプッシュ
```bash
git add .
git commit -m "Add GitHub Actions workflow"
git push
```

## 4. 動作確認

### 手動実行でテスト
1. GitHubリポジトリの Actions タブ
2. "Process Disapproved Ads" を選択
3. "Run workflow" → "Run workflow" をクリック
4. 実行ログを確認

### 自動実行の確認
- 2時間ごとに自動実行されます（UTC基準）
- 日本時間: 3時、5時、7時、9時...（+9時間）

## 5. トラブルシューティング

### エラーが発生した場合
- Actions タブでエラーログを確認
- 失敗時は自動的にログがアップロード（7日間保存）

### よくあるエラー
1. **Secrets未設定**: 上記の6つのSecretsが正しく設定されているか確認
2. **権限エラー**: リポジトリのActions権限が有効か確認
3. **タイムアウト**: 通常3分で完了。30分以上かかる場合は異常

## 実行状況の監視

### Slackやメール通知を追加する場合
workflowファイルに以下を追加：
```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: '不承認広告処理でエラーが発生しました'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## 完了！

これで自動化が完成です。2時間ごとに：
1. 不承認広告を自動検出
2. 新しい動画で差し替え
3. YouTubeにアップロード
4. キューシートに登録
5. GASが処理

全て自動で実行されます！