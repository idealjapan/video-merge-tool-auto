# YouTubeチャンネル認証セットアップガイド

## 概要
複数のYouTubeチャンネルを管理し、案件に応じて適切なチャンネルにアップロードする仕組みです。

## 対応チャンネル
- **メインチャンネル** - デフォルトのアップロード先
- **NBチャンネル** - NB案件専用
- **SBCチャンネル** - SBC案件専用
- **OMチャンネル** - OM案件専用
- **テストチャンネル** - テスト用

## セットアップ手順

### 1. 事前準備

#### 1.1 Google Cloud Console設定
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを作成または選択
3. YouTube Data API v3を有効化
4. OAuth 2.0 クライアントIDを作成
   - アプリケーションの種類: デスクトップ
   - 名前: 任意（例: video-merger-auth）
5. `client_secrets.json`をダウンロード
6. `credentials/`フォルダに配置

### 2. チャンネル認証

#### 2.1 対話的セットアップ（推奨）
```bash
python setup_youtube_channels.py
```

メニューから操作：
```
🎬 YouTube チャンネル認証セットアップツール
============================================================

📝 メニュー:
1. チャンネルを認証する
2. 認証済みチャンネルを確認
3. 認証をリセット
4. 終了

選択してください (1-4): 1
```

#### 2.2 コマンドラインでの認証
```bash
# 認証済みチャンネル一覧
python setup_youtube_channels.py list

# 特定チャンネルの認証
python setup_youtube_channels.py setup 2  # NBチャンネル
python setup_youtube_channels.py setup 3  # SBCチャンネル
```

### 3. 認証フロー

1. **チャンネル選択**
   ```
   🎯 認証するチャンネルを選択:
   1. メインチャンネル
   2. NBチャンネル
   3. SBCチャンネル
   4. OMチャンネル
   5. テストチャンネル
   ```

2. **ブラウザで認証**
   - 自動的にブラウザが開きます
   - **重要**: 該当チャンネルを所有するGoogleアカウントでログイン
   - 権限を許可

3. **認証完了**
   ```
   ✅ トークンを保存しました: credentials/youtube_nb_token.pickle
   
   📺 チャンネル情報:
     名前: あなたのチャンネル名
     ID: UCxxxxxxxxxxxxxx
     登録者数: 1234
     動画数: 56
   ```

### 4. 使用方法

#### 4.1 広告名での自動振り分け
広告名にプレフィックスを付けることで自動的に適切なチャンネルにアップロード：

```
NB_広告名  → NBチャンネル
SBC_広告名 → SBCチャンネル
OM_広告名  → OMチャンネル
```

#### 4.2 Pythonコードでの使用例
```python
from automation.channel_manager import ChannelManager
from automation.youtube_uploader_unified import UnifiedYouTubeUploader

# チャンネルマネージャー初期化
channel_manager = ChannelManager()

# 広告名から適切なチャンネル情報を取得
channel_info = channel_manager.get_channel_info("NB_テスト広告")

# アップロード実行
uploader = UnifiedYouTubeUploader(channel_info['token_path'])
video_url = uploader.upload_video(
    video_path="test.mp4",
    title=channel_info['clean_name'],
    description="テスト動画"
)
```

### 5. トラブルシューティング

#### Q: 「client_secrets.json が見つかりません」
A: Google Cloud ConsoleからOAuth 2.0クライアントIDをダウンロードして`credentials/`に配置

#### Q: 「チャンネル情報を取得できませんでした」
A: 
- 正しいGoogleアカウントでログインしているか確認
- YouTubeチャンネルを作成済みか確認
- API権限が正しく設定されているか確認

#### Q: 複数のチャンネルがあるアカウントの場合
A: ブランドアカウントを使用している場合は、認証時に適切なアカウントを選択

#### Q: トークンの有効期限切れ
A: 自動的に更新されますが、失敗した場合は該当チャンネルを再認証

### 6. 認証ファイル構成

```
credentials/
├── client_secrets.json           # OAuth 2.0 クライアント設定
├── google_service_account.json   # サービスアカウント（スプレッドシート用）
├── youtube_main_token.pickle     # メインチャンネル認証
├── youtube_nb_token.pickle       # NBチャンネル認証
├── youtube_sbc_token.pickle      # SBCチャンネル認証
├── youtube_om_token.pickle       # OMチャンネル認証
└── youtube_test_token.pickle     # テストチャンネル認証
```

### 7. セキュリティ注意事項

- **トークンファイルは秘密情報**
  - Gitにコミットしない（.gitignoreに追加済み）
  - 他人と共有しない

- **定期的な確認**
  ```bash
  # 認証状態の確認
  python setup_youtube_channels.py list
  ```

- **不要なトークンの削除**
  ```bash
  # 対話モードで「3. 認証をリセット」を選択
  python setup_youtube_channels.py
  ```

### 8. 自動化との連携

`ad_processor.py`が自動的に広告名のプレフィックスを認識して適切なチャンネルにアップロード：

1. スプレッドシートの広告名に`NB_`、`SBC_`、`OM_`プレフィックスを付ける
2. `ad_processor.py`を実行
3. 自動的に適切なチャンネルにアップロード

### 9. テスト方法

```bash
# 簡単なテスト
python check_youtube_channel.py

# 特定チャンネルのテスト
python test_youtube_nb.py  # NBチャンネルテスト
```

## まとめ

このセットアップにより：
- ✅ 複数のYouTubeチャンネルを管理
- ✅ 案件に応じて自動振り分け
- ✅ 認証の更新も自動化
- ✅ セキュアなトークン管理