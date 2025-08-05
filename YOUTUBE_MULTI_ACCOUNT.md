# YouTube API 複数アカウント管理ガイド

## 🎯 結論：アカウントごとに認証が必要

### なぜ個別認証が必要？
- **サービスアカウント非対応**: YouTube APIはサービスアカウントを使えない
- **セキュリティ**: 各チャンネルオーナーの明示的な許可が必要
- **API制限**: アカウントごとにクォータが管理される

## 📋 実装方法

### 1. アカウント設定ファイルの構造

`accounts_config.json`:
```json
{
  "accounts": {
    "client_a_channel": {
      "name": "クライアントA",
      "credentials_file": "credentials/client_a_creds.json",
      "token_file": "tokens/client_a_token.pickle",
      "default_privacy": "private",
      "default_category": "22"
    },
    "client_b_channel": {
      "name": "クライアントB",
      "credentials_file": "credentials/client_b_creds.json",
      "token_file": "tokens/client_b_token.pickle",
      "default_privacy": "unlisted",
      "default_category": "24"
    }
  }
}
```

### 2. 初期セットアップ手順

#### 各チャンネルごとに実施：

1. **Google Cloud Console設定**
   ```
   1. https://console.cloud.google.com/
   2. 新規プロジェクト作成（または既存利用）
   3. YouTube Data API v3を有効化
   4. OAuth 2.0クライアントID作成
   5. 認証情報JSONをダウンロード
   ```

2. **認証情報の配置**
   ```bash
   video-merger-tool/
   ├── credentials/
   │   ├── client_a_creds.json
   │   ├── client_b_creds.json
   │   └── client_c_creds.json
   └── tokens/  # 自動生成されるトークン保存場所
   ```

3. **初回認証の実行**
   ```python
   # 各アカウントで1回だけ実行
   uploader = MultiChannelYouTubeUploader()
   uploader.upload_to_channel("client_a_channel", "test.mp4", "テスト")
   # → ブラウザが開いて認証
   ```

### 3. 実際の使用方法

#### 単一チャンネルへアップロード
```python
from youtube_multi_uploader import MultiChannelYouTubeUploader

uploader = MultiChannelYouTubeUploader()

# クライアントAのチャンネルにアップロード
result = uploader.upload_to_channel(
    account_id="client_a_channel",
    file_path="output.mp4",
    title="広告動画 v2",
    description="修正版です",
    tags=["広告", "商品紹介"],
    privacy_status="private"
)
```

#### 複数チャンネルへ一括アップロード
```python
# 同じ動画を複数チャンネルに配信
results = uploader.upload_to_multiple_channels(
    file_path="campaign_video.mp4",
    channels_config={
        "client_a_channel": {
            "title": "【A社】新商品キャンペーン",
            "description": "A社向けカスタマイズ版",
            "tags": ["A社", "キャンペーン"]
        },
        "client_b_channel": {
            "title": "【B社】期間限定セール",
            "description": "B社向けカスタマイズ版",
            "tags": ["B社", "セール"],
            "privacy_status": "unlisted"
        }
    }
)
```

## 🔧 広告審査落ち自動対応システム

### 全体フロー
```
1. 広告審査落ち通知（Webhook）
   ↓
2. 該当クライアントを特定
   ↓
3. 代替動画を自動生成
   ↓
4. 該当チャンネルにアップロード
   ↓
5. スプレッドシートに記録
```

### 実装例
```python
def handle_ad_rejection(client_id, rejection_reason):
    # 1. 代替動画を生成
    new_video = generate_alternative_video(client_id, rejection_reason)
    
    # 2. 該当チャンネルにアップロード
    result = uploader.upload_to_channel(
        account_id=f"{client_id}_channel",
        file_path=new_video,
        title=f"代替広告動画_{datetime.now().strftime('%Y%m%d')}",
        description=f"審査落ち理由: {rejection_reason}",
        privacy_status="private"
    )
    
    # 3. スプレッドシートに記録
    update_spreadsheet(client_id, result['url'], rejection_reason)
```

## 💡 運用のコツ

### 1. トークン管理
- `tokens/`フォルダをバックアップ（再認証不要に）
- `.gitignore`に追加（セキュリティ）
- 定期的に更新（90日で期限切れ）

### 2. クォータ管理
- 各アカウントは独立したクォータ
- デフォルト: 10,000ユニット/日
- アップロード1回: 約1,600ユニット

### 3. エラーハンドリング
```python
# リトライ機能付きアップロード
def upload_with_retry(account_id, file_path, max_retries=3):
    for i in range(max_retries):
        try:
            return uploader.upload_to_channel(account_id, file_path, ...)
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(60)  # 1分待機
                continue
            raise
```

## 🚨 注意事項

### やってはいけないこと
- ❌ 認証情報の使い回し
- ❌ トークンの共有
- ❌ 同一アカウントでの大量チャンネル作成

### セキュリティ
- ✅ 各クライアントは自分のGoogle アカウントで認証
- ✅ アクセス権限は最小限に
- ✅ トークンは暗号化して保存

## 📊 コスト計算

| 項目 | コスト |
|------|--------|
| YouTube API | 無料 |
| AWS EC2（処理サーバー） | 月2,000円 |
| 追加ストレージ | 必要に応じて |

**結論**: クライアント数が増えても基本コストは変わらない！

## 🎯 まとめ

- アカウントごとの認証は**必須**
- 初期設定は面倒だが、一度設定すれば自動化可能
- 複数クライアント対応も問題なし
- セキュリティも担保される

これで広告審査落ち→自動再生成→各チャンネルアップロードの完全自動化が実現できます！