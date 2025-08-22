# Google Ads 不承認広告自動差し替えシステム (Python側)

## 概要
Google Adsで不承認となった動画広告を自動的に検出し、新しい動画で差し替えるシステムのPython側実装です。Google Apps Script (GAS) と連携して動作します。

## システム構成

### 全体アーキテクチャ
```
[GitHub Actions] → [Python] → [Google Sheets Queue] → [GAS] → [Google Ads API]
     ↓                ↓              ↑                    ↓
  (50分ごと)    (不承認検出)    (キュー管理)        (広告差し替え)
                      ↓                                  ↓
                [YouTube Upload]                    [Lark通知]
```

### 主要コンポーネント
- **Python側**: 不承認広告の検出、動画処理、YouTubeアップロード、キュー追加
- **GAS側**: キューの処理、Google Ads APIでの広告差し替え
- **連携**: Googleスプレッドシート経由のキューシステム

## 機能

### 1. 不承認広告の自動検出
- Googleスプレッドシートから審査ステータスを読み取り
- DemandGenVideoResponsiveAd形式の広告のみ対象
- 特定の広告グループ（非デマンドジェネレーション）は自動スキップ

### 2. 動画の自動処理
- Google Driveから元動画を検索・ダウンロード
- AIによる背景自動生成（Replicate API使用）
- 免責事項テキストの自動追加
- 動画のリサイズと合成処理

### 3. YouTubeへの自動アップロード
- 案件別のYouTubeチャンネルに自動アップロード
- 限定公開設定
- タイトル・説明文の自動生成

### 4. キューシステム
- 処理済み広告情報をGoogleスプレッドシートのキューに追加
- GAS側が10分ごとにキューをチェックして広告差し替えを実行

## セットアップ

### 必要な環境
- Python 3.10以上
- ffmpeg
- 日本語フォント（Noto Sans CJK）

### 1. リポジトリのクローン
```bash
git clone https://github.com/idealjapan/video-merger-tool-Auto.git
cd video-merger-tool-Auto
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. 認証ファイルの配置
以下のファイルを`credentials/`ディレクトリに配置：
- `google_service_account.json` - Google Cloud サービスアカウント
- `client_secrets.json` - YouTube API用のOAuth2クライアント
- `token_NB.pickle` - NB用YouTubeトークン
- `token_OM.pickle` - OM用YouTubeトークン  
- `token_SBC.pickle` - SBC用YouTubeトークン

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

### GitHub Actions (自動実行)
- 50分ごとに自動実行
- 手動実行も可能（Actions → Run workflow）

## ファイル構成

```
video-merger-tool-Auto/
├── production_disapproval_handler.py  # メイン処理
├── video_merger_auto_bg.py            # 動画合成処理
├── automation/
│   ├── approval_status_reader.py      # 審査ステータス読み取り
│   ├── google_drive_finder.py         # Google Drive検索
│   └── simple_queue_manager.py        # キュー管理
├── credentials/                        # 認証ファイル（.gitignore）
├── ad-videos/                          # 処理済み動画
└── .github/workflows/
    └── process-disapproved-ads.yml    # GitHub Actions設定
```

## 処理フロー

1. **不承認広告の検出** (50分ごと)
   - Googleスプレッドシートから審査ステータスを確認
   - 不承認広告をリストアップ

2. **動画処理**
   - Google Driveから元動画を検索
   - AI背景生成と合成
   - 免責事項追加

3. **YouTubeアップロード**
   - 案件別チャンネルに限定公開でアップロード
   - 動画URLを取得

4. **キュー追加**
   - 広告グループ名、動画URL、アカウントIDをキューに追加
   - GAS側での処理を待機

5. **広告差し替え** (GAS側で10分ごと)
   - キューから処理対象を取得
   - Google Ads APIで新広告作成・旧広告削除
   - Lark通知送信

## 注意事項

### スキップ対象
以下の広告グループは自動的にスキップされます：
- `YT_NB_7stepパク応援特典8選_MCC02運用02_28_01` (デマンドジェネレーション広告ではない)

### API制限
- YouTube API: 1日あたりのクォータ制限あり
- Google Ads API: リクエスト頻度に制限あり
- 処理間隔を適切に設定（5秒待機）

### エラー処理
- 各処理段階でエラーをキャッチ
- 失敗した広告はスキップして次を処理
- エラーログは`logs/`ディレクトリに保存

## トラブルシューティング

### 動画が見つからない場合
- Google Driveの案件フォルダ構造を確認
- 動画ファイル名が広告グループ名と一致しているか確認

### YouTube認証エラー
- `token_*.pickle`ファイルの有効期限を確認
- 必要に応じて再認証

### キューが処理されない
- GASのトリガーが有効か確認
- スプレッドシートのアクセス権限を確認

## 開発者向け情報

### テストモード
```python
# テスト用広告グループ名を使用
ad_name = "TEST_広告名"  # TEST_で始まる名前はテストモードで処理
```

### ログレベル設定
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## ライセンス
© 2025 開発者: Shingo Ishikiriyama

## サポート
問題が発生した場合は、GitHubのIssuesで報告してください。