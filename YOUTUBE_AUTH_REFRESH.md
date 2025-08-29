# YouTube認証の自動更新について

## 実装した機能（2025年8月29日）

### 問題
- YouTube OAuth2のアクセストークンは**1時間で期限切れ**になる
- 従来のトークンには`refresh_token`が含まれていなかった
- そのため毎回手動で再認証が必要だった

### 解決策
新しい`youtube_auth_manager.py`を実装：
- リフレッシュトークンを使った**自動トークン更新**
- 期限切れを検知して自動的に新しいトークンを取得
- 一度認証すれば、今後は自動更新される

## 認証手順

### 1. 初回認証（リフレッシュトークン付き）

```bash
# NBチャンネル
python3 youtube_auth_manager.py --channel NB --force

# OMチャンネル  
python3 youtube_auth_manager.py --channel OM --force

# SBCチャンネル
python3 youtube_auth_manager.py --channel SBC --force

# RLチャンネル（必要な場合）
python3 youtube_auth_manager.py --channel RL --force
```

**重要**: `--force`オプションを付けることで、リフレッシュトークンを確実に取得します。

### 2. 認証時の注意点

ブラウザが開いたら：
1. **該当チャンネルの所有者アカウント**でログイン
2. 「アカウントの選択」で正しいチャンネルを選択
3. 「許可」をクリック

### 3. 認証状態の確認

```bash
python3 youtube_auth_manager.py --check
```

出力例：
```
NBチャンネル:
  状態: valid
  詳細: 有効なトークンです
  期限: 2025-08-29 15:30:00
  リフレッシュトークン: あり  ← これが重要！
```

## トラブルシューティング

### エラー: Token has been expired or revoked

```bash
# 該当チャンネルを再認証
python3 youtube_auth_manager.py --channel [チャンネル名] --force
```

### エラー: 認証ファイルが見つかりません

`credentials/client_secrets.json`が存在することを確認

### 既存トークンの移行チェック

```bash
python3 youtube_auth_manager.py --migrate
```

## 自動更新の仕組み

1. `production_disapproval_handler.py`実行時
2. トークンの有効性をチェック
3. 期限切れの場合、リフレッシュトークンで自動更新
4. 新しいトークンを保存
5. YouTubeアップロード続行

これにより、**手動での再認証は不要**になります。

## ファイル構成

```
video-merger-tool-Auto/
├── youtube_auth_manager.py      # 新しい認証管理システム
├── token_NB.pickle              # NBチャンネルのトークン
├── token_OM.pickle              # OMチャンネルのトークン  
├── token_SBC.pickle             # SBCチャンネルのトークン
└── credentials/
    └── client_secrets.json      # OAuth2クライアント設定
```

## 今後の運用

1. **初回のみ**: 各チャンネルで`--force`オプション付きで認証
2. **以降**: 自動的にトークンが更新される
3. **監視**: GitHub Actionsのログで認証状態を確認

## 関連ファイル

- `production_disapproval_handler.py`: 本番処理（更新済み）
- `youtube_auth_manager.py`: 認証管理システム（新規作成）