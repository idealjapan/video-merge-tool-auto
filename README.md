# Google Ads 不承認広告自動差し替えシステム - Python側

## 概要
Google Adsで不承認となった動画広告を検出し、新しい動画を作成してYouTubeにアップロードするPython側のシステムです。処理済みの情報はGoogleスプレッドシートのキューに追加し、GAS側が実際の広告差し替えを行います。

## 役割分担

| 処理 | Python側（このリポジトリ） | GAS側 |
|-----|------------------------|------|
| 不承認広告の検出 | ✅ スプレッドシートから読み取り | - |
| 動画の取得 | ✅ Google Driveから検索・ダウンロード | - |
| 動画の加工 | ✅ AI背景生成・合成・免責事項追加 | - |
| YouTubeアップロード | ✅ 限定公開でアップロード | - |
| キューへの追加 | ✅ スプレッドシートに書き込み | - |
| キューの監視 | - | ✅ 10分ごとにチェック |
| 広告の作成 | - | ✅ Google Ads APIで新広告作成 |
| 広告の削除 | - | ✅ 古い広告を削除 |
| 通知 | - | ✅ Lark通知送信 |

## システムアーキテクチャ

```
[GitHub Actions]
    ↓ (50分ごと)
[Python: 不承認検出]
    ↓
[Python: Google Drive検索]
    ↓
[Python: 動画加工（AI背景）]
    ↓
[Python: YouTubeアップロード]
    ↓
[Google Sheets キュー] ← ここで引き継ぎ
    ↓ (10分ごと)
[GAS: キュー処理]
    ↓
[GAS: Google Ads API]
    ↓
[GAS: Lark通知]
```

## 主要機能（Python側）

### 1. 不承認広告の検出
- Googleスプレッドシート「日別(YT)」から審査ステータスを読み取り
- DemandGenVideoResponsiveAd形式のみ対象
- 特定の広告グループを自動スキップ

### 2. 動画処理
- Google Driveから元動画を検索・ダウンロード
- Replicate APIでAI背景を自動生成
- 免責事項テキストを動画に追加
- 動画のリサイズと合成

### 3. YouTubeアップロード
- 案件別のチャンネルに自動アップロード
- 限定公開設定
- タイトル・説明文の自動生成

### 4. キュー管理
- 処理情報をGoogleスプレッドシートに書き込み
- 広告グループ名、動画URL、アカウントIDを記録

## セットアップ

### 必要な環境
- Python 3.10以上
- ffmpeg
- 日本語フォント（Noto Sans CJK）

### 1. リポジトリのクローン
```bash
git clone https://github.com/idealjapan/video-merge-tool-auto.git
cd video-merger-tool-Auto
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. 認証ファイルの配置
`credentials/`ディレクトリに以下のファイルを配置：
- `google_service_account.json` - Googleサービスアカウント
- `client_secrets.json` - YouTube OAuth2クライアント
- `token_NB.pickle` - NB案件用YouTubeトークン
- `token_OM.pickle` - OM案件用YouTubeトークン
- `token_SBC.pickle` - SBC案件用YouTubeトークン

### 4. 環境変数の設定
```bash
export GOOGLE_APPLICATION_CREDENTIALS=credentials/google_service_account.json
export REPLICATE_API_TOKEN=your_replicate_api_token
```

## 使用方法

### 手動実行
```bash
python production_disapproval_handler.py
```

### GitHub Actions（自動実行）
- 50分ごとに自動実行
- 手動実行：Actions → Run workflow

## ファイル構成

```
video-merger-tool-Auto/
├── production_disapproval_handler.py  # メイン処理
├── video_merger_auto_bg.py            # 動画合成処理
├── background_prompts.py              # AI背景プロンプト生成
├── config.py                          # 設定（フォントパス等）
├── automation/
│   ├── approval_status_reader.py      # 審査ステータス読み取り
│   ├── google_drive_finder.py         # Google Drive検索
│   └── simple_queue_manager.py        # キュー管理
├── credentials/                        # 認証ファイル（.gitignore）
└── .github/workflows/
    └── process-disapproved-ads.yml    # GitHub Actions設定
```

## 処理フロー詳細

### 1. 不承認広告の検出（50分ごと）
```python
# Googleスプレッドシートから読み取り
reader = ApprovalStatusReader()
disapproved_ads = reader.get_disapproved_ads()
```

### 2. 動画の取得と加工
```python
# Google Driveから検索
finder = GoogleDriveFinder()
video_path = finder.find_video_by_ad_group(ad_group_name)

# AI背景と合成
merger = VideoMergerWithAutoBG()
result = merger.process_with_auto_background(video_path, output_path)
```

### 3. YouTubeアップロード
```python
# 案件別チャンネルにアップロード
youtube = build('youtube', 'v3', credentials=creds)
request = youtube.videos().insert(...)
response = request.execute()
youtube_url = f"https://www.youtube.com/watch?v={response['id']}"
```

### 4. キューへの追加
```python
# スプレッドシートに書き込み
queue = SimpleQueueManager()
process_id = queue.add_to_queue(
    video_url=youtube_url,
    ad_group_name=ad_group_name,
    account_id=account_id
)
```

## スキップ対象

以下の広告グループは自動的にスキップされます：
- `YT_NB_7stepパク応援特典8選_MCC02運用02_28_01`（非デマンドジェネレーション）

## トラブルシューティング

### 動画が見つからない
- Google Driveのフォルダ構造を確認
- ファイル名が広告グループ名と一致しているか確認

### YouTube認証エラー
- `token_*.pickle`ファイルの有効期限を確認
- 必要に応じて`youtube_auth_setup/`で再認証

### キューが処理されない
- GAS側のトリガー設定を確認（10分ごと）
- スプレッドシートのアクセス権限を確認

## 関連リポジトリ
- [google-ads-auto-replacer](https://github.com/idealjapan/google-ads-auto-replacer) - GAS側の実装

## ライセンス
© 2025 開発者: Shingo Ishikiriyama

## サポート
問題が発生した場合は、GitHubのIssuesで報告してください。