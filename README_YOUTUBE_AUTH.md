# YouTube認証手順（広告担当者向け）

## 🎯 目的
OM/SBCチャンネルへの自動アップロード用トークンを取得

## 📋 必要なもの
- OM/SBCチャンネルの所有者Googleアカウント
- このリポジトリのクローン

## 🔧 セットアップ手順

### 1. リポジトリをクローン
```bash
git clone [リポジトリURL]
cd video-merger-tool-Auto
```

### 2. 依存関係インストール
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. 認証実行
```bash
python3 youtube_auth_for_channels.py
```

### 4. チャンネル選択
- 「3. 両方」を選択してOM/SBC両方を認証

### 5. ブラウザでの操作
1. Googleアカウントでログイン
2. **重要**: 複数のチャンネルがある場合、必ず広告用チャンネルを選択
   - OM: @yuki_om
   - SBC: @SBC-fp9zq
3. 「許可」をクリック

## ⚠️ よくある問題

### チャンネル選択画面が出ない場合
- そのアカウントのデフォルトチャンネル（個人用）で認証される
- 広告用チャンネルへの切り替えが必要

### 解決方法
1. YouTubeにログイン
2. 右上のアイコンをクリック
3. 「チャンネルを切り替える」
4. 広告用チャンネルに切り替えてから認証を再実行

## 📁 生成されるファイル
- `credentials/token_OM.pickle` - OMチャンネル用
- `credentials/token_SBC.pickle` - SBCチャンネル用

## ✅ 確認方法
```bash
python3 test_om_sbc_upload.py
```
これで各チャンネルにテスト動画がアップロードされれば成功！
