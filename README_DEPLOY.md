# 🎬 動画合成ツール - クイックスタートガイド

## 最速デプロイ方法（5分で完了！）

### 🚀 Render.comで今すぐデプロイ

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. 上のボタンをクリック
2. GitHubアカウントでログイン
3. リポジトリをフォーク（自動）
4. デプロイ完了！

URL例: `https://your-app.onrender.com`

## 💻 ローカルで試す

```bash
# 1. クローン
git clone <repository-url>
cd video-merger-tool

# 2. Docker起動（推奨）
docker-compose up

# または Python直接
pip install -r requirements.txt
python web_app.py

# 3. ブラウザでアクセス
http://localhost:5000
```

## 🎯 使い方（3ステップ）

1. **動画をアップロード**
   - メイン動画：商品紹介など
   - 背景動画：ループ動画

2. **設定を選択**
   - サイズ：YouTube、Instagram等
   - スケール：メイン動画の大きさ
   - テキスト：注意書き（オプション）

3. **ダウンロード**
   - 処理完了後、ダウンロードボタンが表示

## 📱 対応デバイス

- ✅ PC（Chrome, Firefox, Safari）
- ✅ スマートフォン
- ✅ タブレット

## ⚡ 特徴

- **簡単**: ドラッグ&ドロップ対応
- **高速**: 並列処理で高速変換
- **無料**: 基本機能は完全無料
- **安全**: 24時間で自動削除

## 🛠 カスタマイズしたい場合

### デザイン変更
`templates/index.html`を編集

### 機能追加
`web_app.py`を編集

### 設定変更
環境変数で調整可能

## 📞 ヘルプ

- [詳細なドキュメント](./CLOUD_DEPLOYMENT.md)
- [セットアップガイド](./SETUP.md)
- [使用例](./examples.md)

---

**今すぐ始める**: 上の「Deploy to Render」ボタンをクリック！🚀