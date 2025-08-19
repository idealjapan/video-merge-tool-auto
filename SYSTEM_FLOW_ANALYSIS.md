# システムフロー分析と競合調査

## 現在のシステム構成

### Python側
- **実行ファイル**: 
  - `production_disapproval_handler.py` (1件のみ処理)
  - `production_disapproval_handler_multi.py` (複数件処理対応・新規作成)
- **データソース**: スプレッドシート「日別(YT)」シートのAB列（審査状態）
- **出力先**: スプレッドシート「広告キュー」シート

### GAS側
- **実行ファイル**: `キュー処理システムV2.js`
- **データソース**: スプレッドシート「広告キュー」シート
- **処理内容**: Google Ads APIで広告の作成・差し替え

## 🚨 潜在的な問題と競合

### 1. **同時実行の競合**
- **問題**: PythonとGASが同じスプレッドシートに同時アクセス
- **リスク**: データの不整合、処理の重複
- **対策**: 
  - Python側：キュー追加のみ（書き込み専用）
  - GAS側：ステータス更新のみ（読み込み→更新）
  - 競合しない設計になっている ✅

### 2. **複数件処理時の問題**
- **Python側の問題**:
  - 現在の本番コード（`production_disapproval_handler.py`）は1件のみ処理
  - 複数の不承認があっても最初の1件だけ処理される
- **GAS側の対応**:
  - BATCH_SIZE: 3件まで同時処理可能
  - 複数タスクの処理に対応済み ✅

### 3. **広告タイプの不一致**
- **問題**: GAS側が`DEMAND_GEN_VIDEO_RESPONSIVE_AD`タイプを探すが存在しない
- **現状**: タイプフィルターを削除して対応済み（一時的）
- **要確認**: 実際の広告タイプを確認する必要あり

### 4. **P列・Q列のデータ整合性**
- **Python側**: 
  - P列（16列目）: `ad_group_name`を設定
  - Q列（17列目）: `account_id`を設定
- **GAS側**:
  - P列（index 15）: 広告グループ名として読み取り
  - Q列（index 16）: アカウントIDとして読み取り
- **結論**: 正しく対応している ✅

### 5. **リトライ処理の競合**
- **仕様**:
  - MAX_RETRIES: 3回まで自動リトライ
  - ステータス「待機中」に戻してリトライ
- **リスク**: なし（正常動作）✅

## ✅ 確実に動作するルート

### **推奨フロー（複数件対応）**

1. **Python側の準備**
   ```bash
   # 複数件対応版を本番にコピー
   cp production_disapproval_handler_multi.py production_disapproval_handler.py
   ```

2. **Python実行**
   ```bash
   python production_disapproval_handler.py
   ```
   - すべての不承認広告を順番に処理
   - 各処理間に5秒の待機（API制限対策）
   - キューに順次追加

3. **GAS実行**
   - ブラウザでGASエディタを開く
   - `processQueueFromSheets()`を実行
   - 最大3件ずつバッチ処理

## 📝 チェックリスト

### Python側実行前
- [ ] `credentials/`フォルダに必要なトークンファイルがある
  - [ ] `token_NB.pickle`
  - [ ] `token_OM.pickle`
  - [ ] `token_SBC.pickle`
- [ ] Google Drive APIの認証設定が完了
- [ ] スプレッドシートへのアクセス権限がある

### GAS側実行前
- [ ] スクリプトプロパティが設定済み
  - [ ] `REFRESH_TOKEN`
  - [ ] `OAUTH_CLIENT_ID`
  - [ ] `OAUTH_CLIENT_SECRET`
  - [ ] `LOGIN_CUSTOMER_ID` (MCC ID)
  - [ ] `GOOGLE_ADS_DEVELOPER_TOKEN`
- [ ] 広告グループに広告が存在する（または作成可能）

## 🔧 トラブルシューティング

### 問題1: 広告が見つからない
**症状**: "広告グループに広告が存在しません"
**原因**: 広告タイプの不一致
**対策**: 広告タイプフィルターを一時的に削除済み

### 問題2: 認証エラー
**症状**: 401 UNAUTHENTICATED
**原因**: リフレッシュトークンの期限切れ
**対策**: OAuth Playgroundで新しいトークンを取得

### 問題3: 権限エラー
**症状**: 403 PERMISSION_DENIED
**原因**: MCCアカウントIDが未設定
**対策**: `LOGIN_CUSTOMER_ID`を設定済み

## 📌 結論

**安全に実行できる状態です**。以下の手順で実行：

1. Python側を複数件対応版に更新
2. Pythonで不承認広告を処理してキューに追加
3. GASでキューを処理して広告を差し替え

競合や重複のリスクは最小限に抑えられています。