# 🎯 最終チェックリスト - 完璧な状態へ

## 現在の状態

### ✅ 完了済み
- [x] Google Drive API接続
- [x] スプレッドシート連携
- [x] 動画検索・ダウンロード機能
- [x] 背景合成エンジン
- [x] キューシステム
- [x] テストツール一式

### ⏳ 残りのタスク

## 1️⃣ YouTube認証（オフィスで実施）
```bash
# 準備したファイル
youtube_auth_setup.zip
```
広告担当者のPCで5分で完了

## 2️⃣ GAS側の設定（5分）

### やること：
1. スプレッドシートを開く
2. 拡張機能 → Apps Script
3. `キュー処理システム.js`をコピペ
4. トリガー設定（5分ごと）

## 3️⃣ 最終動作テスト

### A. 単体テスト（各機能）
```bash
# 1. システム診断
python3 test_full_system.py

# 2. セーフモード（シミュレーション）
python3 safe_test_mode.py

# 3. Google Drive確認
python3 test_google_drive_video.py
```

### B. 統合テスト（全体フロー）
```bash
# キュー連携テスト
python3 test_gas_integration.py
```

### C. 実データテスト（1件のみ）
```bash
# 最小限のテスト
python3 minimal_real_test.py
```

## 🔄 処理フローの確認

### 通常モード（フル機能）
1. スプレッドシート「処理待ち」から広告リスト取得
2. Google Driveから動画検索
3. 動画ダウンロード
4. 背景合成処理
5. YouTubeアップロード
6. スプレッドシート更新
7. Google Ads連携キューに追加
8. GAS側で5分ごとに処理

### 軽量モード（ダウンロードなし）
```bash
python3 config_no_download.py
```
1. Google Driveで動画検索
2. URLのみ記録
3. スプレッドシート更新
4. キューに追加

## 📊 運用開始の判断基準

### 必須項目（これがないと動かない）
- [ ] YouTube認証完了
- [ ] GASトリガー設定
- [ ] テストデータで1回成功

### 推奨項目（あると安心）
- [ ] エラー時の通知設定（Lark/Slack）
- [ ] バックアップ設定
- [ ] 処理ログの確認方法理解

## 🚨 トラブルシューティング

### よくある問題と対処

1. **「認証エラー」**
   → credentials/フォルダの権限確認

2. **「動画が見つからない」**
   → Google Driveの共有設定確認

3. **「キューが処理されない」**
   → GASトリガーの確認

4. **「YouTube認証失敗」**
   → 所有者アカウントで再認証

## 📅 運用開始までのステップ

### 今日やること
1. ✅ システムテスト完了
2. ⬜ GAS設定（5分）

### 明日（オフィス）
1. ⬜ YouTube認証（5分）
2. ⬜ 実データテスト（10分）

### 運用開始
1. ⬜ 少量データで試運転（1日）
2. ⬜ 問題なければ本格運用

## 💡 Tips

### デバッグモード
```bash
# 詳細ログを出力
export DEBUG=1
python3 automation/ad_processor.py
```

### ドライラン
```bash
# 実際の処理をせずにログだけ
export DRY_RUN=1
python3 automation/ad_processor.py
```

### 特定の広告だけ処理
```python
# ad_processor.pyを編集
if ad_name.startswith('TEST_'):
    # TEST_で始まるものだけ処理
```

## ✨ 完璧な状態 = 

1. **YouTube認証済み**
2. **GASトリガー設定済み**
3. **テストで1回成功**

この3つが揃えば完璧です！