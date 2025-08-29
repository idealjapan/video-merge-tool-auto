# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

### システムの目的
Google Adsで不承認となった広告を自動的に検出し、新しい動画で広告を差し替えるシステム

### アーキテクチャ
```
承認ステータス監視 → Python処理 → キューシート → GAS実行 → Google Ads更新
```

### システムの主な用途
1. **広告差し替え自動化**: Google Adsで不承認となった広告を自動検出・差し替え
2. **動画背景生成**: Replicate APIを使用した自然・動物の背景自動生成
3. **マルチチャンネル対応**: NB、OM、SBC、RL各案件のYouTubeチャンネル管理

## 開発コマンド

### 依存パッケージのインストール
```bash
pip install flask==3.0.0 flask-cors==4.0.0 requests==2.31.0 python-dotenv==1.0.0
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 gspread replicate moviepy pillow
```

### テスト実行
```bash
# 不承認広告の確認
GOOGLE_APPLICATION_CREDENTIALS=credentials/google_service_account.json \
python -c "from automation.approval_status_reader import ApprovalStatusReader; reader = ApprovalStatusReader(); print(reader.get_disapproved_ads())"

# キューステータスの確認
GOOGLE_APPLICATION_CREDENTIALS=credentials/google_service_account.json \
python -c "from automation.simple_queue_manager import SimpleQueueManager; queue = SimpleQueueManager(); print(queue.get_queue_status())"

# YouTube認証状態の確認
python test_om_sbc_upload.py

# チャンネル別YouTube認証
python youtube_auth_setup/office_auth_setup.py --channel OM  # OMチャンネル用
python youtube_auth_setup/office_auth_setup.py --channel SBC # SBCチャンネル用

# 本番実行（不承認広告の自動処理）
python production_disapproval_handler.py
```

### 環境変数の設定
```bash
export GOOGLE_APPLICATION_CREDENTIALS="credentials/google_service_account.json"
export REPLICATE_API_TOKEN="your_replicate_api_token_here"
```

## コアアーキテクチャ

### メインコンポーネント構成
```
automation/
├── approval_status_reader.py  # 不承認広告検出（スプレッドシートから）
├── google_drive_finder.py     # Google Driveから動画検索
├── simple_queue_manager.py    # キューシート管理
└── sheets_manager.py          # スプレッドシート基本操作

プロセシング:
├── production_disapproval_handler.py  # 本番メイン処理
├── video_merger_auto_bg.py           # 動画加工（背景生成）
└── background_prompts.py             # AI背景プロンプト生成

認証:
├── credentials/
│   ├── google_service_account.json  # Sheets/Drive API
│   ├── client_secrets.json          # YouTube OAuth
│   └── token_*.pickle               # チャンネル別トークン
```

### データフロー
1. **ApprovalStatusReader** が不承認広告を検出（形式: YT_[案件]_[動画名]_MCC...）
2. **GoogleDriveFinder** で動画をDriveから検索・ダウンロード
3. **VideoMergerWithAutoBG** で背景生成・動画加工
4. **YouTube API** でチャンネルにアップロード
5. **SimpleQueueManager** でキューシートに記録
6. **GAS** がキューを読み取りGoogle Ads APIを実行

## 現在の実装状況

### 完成している機能
1. **不承認広告検出** (`automation/approval_status_reader.py`)
   - スプレッドシートID: `1yxEYTX-9e9PkIPCh62uJTvAigzyDHv_sSjTfv3qU9M0`
   - 広告グループ名から案件名と動画名を正しく解析
   - ハードコーディングを完全に排除（重要）

2. **動画処理** (`production_disapproval_handler.py`)
   - 案件別フォルダ（NB_CR、OM_CR、SBC_CR）から動画を検索・ダウンロード
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

## 重要な制約事項

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

## 現在の問題・懸念事項

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

## 既知の問題と対処法

### YouTube認証エラー
- **症状**: OM/SBCチャンネルへのアップロードが失敗
- **原因**: 個人チャンネルで認証された可能性
- **対処**: `youtube_auth_setup/office_auth_setup.py`で再認証

### 動画が見つからない
- **症状**: GoogleDriveFinderが動画を検出できない
- **原因**: 共有ドライブのファイルアクセスにパラメータが不足
- **対処**: `supportsAllDrives=True`と`includeItemsFromAllDrives=True`を追加（修正済み）

### アップロード保留
- **症状**: YouTubeアップロードが1時間以上保留
- **原因**: API制限または大量アップロード
- **対処**: 時間を空けて再実行

## 環境設定

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
- Replicate API Token: GitHub Secretsで管理（REPLICATE_API_TOKEN）

### スプレッドシートID
- 承認ステータス: `1yxEYTX-9e9PkIPCh62uJTvAigzyDHv_sSjTfv3qU9M0`
- 広告キュー: `1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U`

## コーディング規約

1. **動画名のハードコーディング禁止**
   - 「NB_7Step別素材02」のような固定値は絶対に使わない
   - 必ず`approval_status_reader`の解析結果を使う
   - GoogleDriveFinderで動画を検索する際も、approval_status_readerの結果を使用

2. **広告グループ名の解析ロジック**
   - 形式: `YT_[案件名]_[動画名]_MCC[その他]`
   - 例: `YT_NB_7stepパク応援特典8選_MCC02運用02_28_01`
   - 解析結果: 案件名=`NB`、動画名=`NB_7stepパク応援特典8選`

3. **チャンネル認証の注意点**
   - 個人チャンネルではなくビジネスチャンネルで認証
   - OM: @yuki_om
   - SBC: @SBC-fp9zq

4. **エラーハンドリング**
   - 動画が見つからない場合は明確なエラーメッセージを表示
   - YouTube APIエラーは詳細をログに記録
   - リトライ機能を実装（最大3回）

## 外部連携

### Google Apps Script
- 場所: `/Users/shingo/Desktop/アプリ開発/google-ads-auto-replacer/キュー処理システムv2.js`
- 機能: キューシートからGoogle Ads APIを実行
- 注意: APIリクエスト部分は変更禁止（互換性維持）

### スプレッドシート
- 承認ステータス: `1yxEYTX-9e9PkIPCh62uJTvAigzyDHv_sSjTfv3qU9M0`（日別(YT)シート）
- 広告キュー: `1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U`（広告キューシート）

### GitHub
- リポジトリ: https://github.com/idealjapan/video-merge-tool-auto
- 用途: チャンネル所有者への認証ガイド共有

## 2025年8月25日の作業記録と決定事項

### 実装した機能
1. **CP状態によるフィルタリング機能**
   - `approval_status_reader.py`にCP状態（AA列）の判定ロジックを追加
   - CP状態が`removed`または`paused`の広告を自動的にスキップ
   - 不要な広告の処理を防ぎ、システム効率を向上

2. **特定広告のスキップ処理**
   - `YT_NB_7stepパク応援特典8選_MCC02運用02_28_01`をスキップ（非デマンドジェネレーション広告）
   - `production_disapproval_handler.py`と GitHub Actions ワークフローに実装
   - **重要**: DG（デマンドジェネレーション）広告はスキップしない（処理対象）

3. **GitHub Actions実行頻度の最適化**
   - 問題: `'0,50 * * * *'`設定により10分と50分の交互間隔で実行されていた
   - 解決: `'*/50 * * * *'`に変更し、均等な50分間隔に修正
   - 1日約29回の実行頻度を維持しつつ、実行タイミングを均等化

### 現在のフィルタリング条件（重要）
- ✅ CP状態が`removed`または`paused`の広告をスキップ
- ✅ 特定の非デマンド広告（`YT_NB_7stepパク応援特典8選_MCC02運用02_28_01`）をスキップ  
- ✅ DG（デマンドジェネレーション）広告は処理対象（スキップしない）

### 今後解決が必要な課題

#### 1. YouTube認証の完全化（最優先）
- **現状**: NBチャンネルのみ動作確認済み
- **必要な作業**: 
  - OM/SBCチャンネルの認証取得
  - チャンネル所有者による正しいビジネスチャンネルでの認証
  - 各チャンネルのtoken_*.pickleファイル生成

#### 2. Replicate API トークンの設定
- **現状**: .envファイルにプレースホルダーのみ
- **必要な作業**: 本番用のReplicate APIトークンを設定
- **影響**: 背景動画生成機能が動作しない

#### 3. アカウントID管理の拡充
- **現状**: NBのアカウントID（7042358345）のみ確認済み
- **必要な作業**: OM、SBC、RLのアカウントID確認と登録
- **実装済み**: スプレッドシートZ列からの自動取得機能

### 実装予定の機能

1. **エラー通知機能**
   - 処理失敗時のSlack/Email通知
   - エラーログの集約と分析

2. **処理履歴の可視化**
   - 処理成功/失敗の統計ダッシュボード
   - 月次レポート生成機能

3. **動画処理の最適化**
   - 並列処理による高速化
   - キャッシュ機能の実装

### 運用上の注意事項

1. **GitHub Actions の実行頻度**
   - 現在: 50分ごと（1日約29回）
   - 必要に応じて調整可能（コスト vs レスポンス時間のバランス）

2. **スキップ対象の管理**
   - 特定広告のハードコーディングは最小限に
   - 可能な限りスプレッドシートでの管理に移行を検討

3. **監視項目**
   - GitHub Actions の実行履歴（`gh run list`）
   - キューシートの処理状況
   - YouTube アップロードの成功率

### 開発環境の整備状況

- ✅ GitHub CLI インストール済み（v2.78.0）
- ✅ idealjapanアカウントで認証済み
- ✅ 実行履歴の確認が可能

### 次回作業開始時のチェックリスト

1. 不承認広告の確認
```bash
GOOGLE_APPLICATION_CREDENTIALS=credentials/google_service_account.json \
python -c "from automation.approval_status_reader import ApprovalStatusReader; reader = ApprovalStatusReader(); print(f'不承認広告: {len(reader.get_disapproved_ads())}件')"
```

2. GitHub Actions の実行状況確認
```bash
gh run list --workflow=process-disapproved-ads-fast.yml --limit 5 --repo idealjapan/video-merge-tool-auto
```

3. キューの処理状況確認
```bash
GOOGLE_APPLICATION_CREDENTIALS=credentials/google_service_account.json \
python -c "from automation.simple_queue_manager import SimpleQueueManager; queue = SimpleQueueManager(); print(queue.get_queue_status())"
```
