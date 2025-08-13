# CLAUDE.md - プロジェクトコンテキスト

最終更新: 2025-08-13

## 📋 プロジェクト概要

### システムの目的
Google Adsで不承認となった広告を自動的に検出し、新しい動画で広告を差し替えるシステム

### アーキテクチャ
```
承認ステータス監視 → Python処理 → キューシート → GAS実行 → Google Ads更新
```

## ✅ 現在の実装状況

### 完成している機能
1. **不承認広告検出** (`automation/approval_status_reader.py`)
   - スプレッドシートID: `1yxEYTX-9e9PkIPCh62uJTvAigzyDHv_sSjTfv3qU9M0`
   - 広告グループ名から案件名と動画名を正しく解析
   - ハードコーディングを完全に排除（重要）

2. **動画処理** (`production_disapproval_handler.py`)
   - Google Driveから動画を検索・ダウンロード
   - AI背景生成（Replicate API使用）
   - 免責事項テキスト追加
   - 完全に汎用的な実装（動画名のハードコーディングなし）

3. **YouTubeアップロード**
   - 案件別チャンネルへのアップロード機能
   - NBチャンネルは動作確認済み
   - OM/SBCチャンネルは認証待ち

4. **キュー管理** (`automation/simple_queue_manager.py`)
   - スプレッドシートID: `1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U`
   - 「広告キュー」シートで統一
   - 広告グループ名とアカウントIDを正しく記録

5. **GAS連携** (`/Users/shingo/Desktop/アプリ開発/google-ads-auto-replacer/キュー処理システムv2.js`)
   - キューシートからの読み取り
   - Google Ads APIコール
   - テストモード実装済み

## 🚨 重要な決定事項

### 絶対に守るべきルール
1. **動画名のハードコーディング禁止**
   - ユーザーから極めて強い警告を受けた
   - 「NB_7Step別素材02」のような固定値は絶対に使わない
   - 常に`approval_status_reader`が解析した動画名を使用

2. **システムの汎用性**
   - 全案件（NB、OM、SBC、RL）で動作する設計
   - 案件固有のロジックは最小限に

3. **旧システムとの互換性**
   - GAS側のAPIリクエスト部分は変更しない
   - 既存の処理フローを壊さない

## ⚠️ 現在の問題・懸念事項

### 1. YouTube認証問題（最優先）
**問題**: 取得したトークンが期待したチャンネルのものではない
- 現象：動画はアップロードされるが、OM/SBCチャンネルに表示されない
- 原因：チャンネル所有者が認証時に個人チャンネルで認証した可能性
- 影響：OM/SBC案件の広告差し替えができない

**対策**:
- GitHubでコードを共有済み（`idealjapan/video-merger`）
- `YOUTUBE_AUTH_GUIDE.md`を作成
- チャンネル所有者にClaude Codeで認証してもらう予定

### 2. アカウントID管理
**現状**: 
- NBのアカウントID: `7042358345`
- 他案件のアカウントIDは未確認
- スプレッドシートのZ列から自動取得する仕組みは実装済み

### 3. 処理時間の問題
**懸念**: YouTubeアップロードが「保留中」になることがある
- 1時間以上保留が続く場合がある
- 頻繁なアップロードによる制限の可能性

## 📝 今後のタスク

### 緊急度：高
1. **OM/SBCチャンネル認証**
   - チャンネル所有者による正しいチャンネルでの認証
   - 認証後のテスト実行

2. **本番フローの完全テスト**
   - 実際の不承認広告での動作確認
   - GAS側の処理確認

### 緊急度：中
1. **RLチャンネル対応**
   - トークン取得
   - 動作確認

2. **エラーハンドリング強化**
   - 動画が見つからない場合の処理
   - YouTube APIエラーの対処

3. **処理速度改善**
   - 背景生成の高速化検討
   - 並列処理の実装

### 緊急度：低
1. **監視自動化**
   - 定期的な不承認チェック
   - 自動実行の実装

2. **ログ機能強化**
   - 処理履歴の記録
   - エラーログの改善

## 🔧 環境情報

### 必要な認証情報
```
credentials/
├── google_service_account.json  # Sheets/Drive API用
├── client_secrets.json          # YouTube OAuth用
├── token_NB.pickle             # NBチャンネル（取得済み）
├── token_OM.pickle             # OMチャンネル（要再取得）
└── token_SBC.pickle            # SBCチャンネル（要再取得）
```

### API Keys
- Replicate API Token: `r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio`

### スプレッドシートID
- 承認ステータス: `1yxEYTX-9e9PkIPCh62uJTvAigzyDHv_sSjTfv3qU9M0`
- 広告キュー: `1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U`

## 💡 実装予定の機能

1. **マルチチャンネル完全対応**
   - 全チャンネルの認証完了
   - 自動振り分け機能

2. **完全自動化**
   - GitHub Actions統合
   - 定期実行設定

3. **通知機能**
   - 処理完了通知
   - エラー通知

## 📌 次回再開時の確認事項

1. **YouTube認証状態の確認**
   ```bash
   python test_om_sbc_upload.py
   ```

2. **不承認広告の確認**
   ```bash
   python -c "from automation.approval_status_reader import ApprovalStatusReader; reader = ApprovalStatusReader(); print(reader.get_disapproved_ads())"
   ```

3. **キューステータスの確認**
   ```bash
   python -c "from automation.simple_queue_manager import SimpleQueueManager; queue = SimpleQueueManager(); print(queue.get_queue_status())"
   ```

4. **本番実行（準備ができたら）**
   ```bash
   python production_disapproval_handler.py
   ```

## ⚠️ 絶対に忘れてはいけないこと

1. **動画名をハードコーディングしない**
   - 「NB_7Step別素材02」のような固定値は使わない
   - 必ず`approval_status_reader`の解析結果を使う

2. **広告グループ名の解析ロジック**
   - 形式: `YT_[案件名]_[動画名]_MCC[その他]`
   - 例: `YT_NB_7stepパク応援特典8選_MCC02運用02_28_01`
   - 解析結果: 案件名=`NB`、動画名=`NB_7stepパク応援特典8選`

3. **チャンネル認証の注意点**
   - 個人チャンネルではなくビジネスチャンネルで認証
   - OM: @yuki_om
   - SBC: @SBC-fp9zq

## 🔗 関連リソース

- GitHubリポジトリ: https://github.com/idealjapan/video-merger
- GASプロジェクト: `/Users/shingo/Desktop/アプリ開発/google-ads-auto-replacer/`
- 動画保存先: Google Drive（共有ドライブ）

---

このファイルは次回のセッション開始時に必ず参照してください。