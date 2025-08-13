# Video Merger Tool Auto

不承認Google広告の自動差し替えシステム

## 🎯 概要
Google Adsで不承認となった広告を自動的に検出し、新しい動画で広告を差し替えるシステムです。

## 🏗️ システム構成

### アーキテクチャ
```
承認ステータス監視 → Python処理 → キューシート → GAS実行 → Google Ads更新
```

### 主要コンポーネント
1. **Python側**（このリポジトリ）
   - 不承認広告の検出
   - Google Driveから動画取得
   - 背景合成処理
   - YouTubeアップロード
   - キュー管理

2. **GAS側**（Google Apps Script）
   - キューシートの処理
   - Google Ads APIコール
   - 広告の作成/更新

## 📦 必要な依存関係

```bash
pip install -r requirements.txt
```

主要ライブラリ：
- gspread（Google Sheets連携）
- google-api-python-client（YouTube/Drive API）
- replicate（AI背景生成）
- ffmpeg-python（動画処理）

## 🔐 認証設定

### 1. サービスアカウント（Google Sheets/Drive用）
`credentials/google_service_account.json`を配置

### 2. YouTube認証
各チャンネル用のトークンが必要：
- NB: `credentials/token_NB.pickle`
- OM: `credentials/token_OM.pickle`
- SBC: `credentials/token_SBC.pickle`

**重要**: チャンネル認証については `YOUTUBE_AUTH_GUIDE.md` を参照

### 3. Replicate API
環境変数またはコード内で設定：
```bash
export REPLICATE_API_TOKEN=your_token_here
```

## 🚀 使用方法

### 1. 不承認広告の処理（本番）
```bash
python production_disapproval_handler.py
```

### 2. テスト実行
```bash
# 不承認広告の確認
python -c "from automation.approval_status_reader import ApprovalStatusReader; reader = ApprovalStatusReader(); print(reader.get_disapproved_ads())"

# キューステータス確認
python -c "from automation.simple_queue_manager import SimpleQueueManager; queue = SimpleQueueManager(); print(queue.get_queue_status())"
```

## 📂 ディレクトリ構成

```
video-merger-tool-Auto/
├── automation/              # 自動化モジュール
│   ├── approval_status_reader.py  # 承認ステータス読み取り
│   ├── google_drive_finder.py     # Drive動画検索
│   └── simple_queue_manager.py    # キュー管理
├── credentials/            # 認証情報（gitignore）
├── ad-videos/             # 処理済み広告動画
├── production_disapproval_handler.py  # メイン処理
└── video_merger_auto_bg.py           # 背景合成処理
```

## ⚙️ 処理フロー

1. **不承認広告検出**
   - スプレッドシートから承認ステータスを読み取り
   - 広告グループ名から案件名と動画名を解析

2. **動画処理**
   - Google Driveから元動画を検索・ダウンロード
   - AI背景生成と合成処理
   - 免責事項テキスト追加

3. **YouTubeアップロード**
   - 案件別チャンネルに限定公開でアップロード
   - 動画URLを取得

4. **キュー登録**
   - 広告キューシートに情報を追加
   - GAS処理を待機

5. **GAS処理**（手動実行）
   - キューシートから情報取得
   - Google Ads APIで新広告作成

## 🔍 トラブルシューティング

### YouTube認証の問題
- チャンネル選択画面が出ない → デフォルトチャンネルで認証される
- 動画が別チャンネルにアップロードされる → 正しいチャンネルで再認証が必要

### 動画が見つからない
- Google Driveに動画がアップロードされているか確認
- ファイル名が広告グループ名と一致しているか確認

### キュー処理が進まない
- GASで `processQueueFromSheets()` を実行
- エラーログを確認

## 📝 注意事項

- **ハードコーディング禁止**: 動画名や広告名を固定値で書かない
- **汎用性重視**: 全案件で動作するよう設計
- **セキュリティ**: 認証情報は絶対にコミットしない

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成
3. 変更をコミット
4. プルリクエストを送信

## 📄 ライセンス

Proprietary - All rights reserved