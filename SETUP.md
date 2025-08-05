# 動画合成ツール セットアップガイド

## 目次
1. [個人での使用](#個人での使用)
2. [チームでの使用（Docker版）](#チームでの使用docker版)
3. [YouTube自動アップロード設定](#youtube自動アップロード設定)
4. [トラブルシューティング](#トラブルシューティング)

## 個人での使用

### 1. 必要な環境
- Python 3.6以上
- FFmpeg

### 2. インストール手順

```bash
# リポジトリのクローン（またはZIPダウンロード）
git clone <repository-url>
cd video-merger-tool

# FFmpegのインストール
# Mac
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# Windows
# https://ffmpeg.org/download.html からダウンロード

# Python依存関係のインストール（YouTube機能を使う場合）
pip3 install -r requirements.txt
```

### 3. 基本的な使用

```bash
# 動画合成のみ
python3 video_merger_advanced.py main.mp4 background.mp4 output.mp4

# オプション付き
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 \
  --size 1920x1080 \
  --main-scale 0.7 \
  --text "※個人差があります"
```

## チームでの使用（Docker版）

### 1. 必要な環境
- Docker
- Docker Compose

### 2. セットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd video-merger-tool

# Dockerイメージのビルド
docker-compose build

# フォルダ構造の準備
mkdir -p input output credentials
```

### 3. 使用方法

#### 方法1: Docker Composeを使用

```bash
# 動画ファイルを input/ フォルダに配置
cp /path/to/main.mp4 input/
cp /path/to/background.mp4 input/

# 動画合成を実行
docker-compose run --rm video-merger python3 video_merger_advanced.py \
  /app/input/main.mp4 \
  /app/input/background.mp4 \
  /app/output/result.mp4 \
  --size 1920x1080 \
  --main-scale 0.7 \
  --text "※個人差があります"

# 結果は output/ フォルダに保存されます
```

#### 方法2: Dockerコマンドを直接使用

```bash
# イメージのビルド
docker build -t video-merger-tool .

# 実行
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  video-merger-tool \
  python3 video_merger_advanced.py \
  /app/input/main.mp4 \
  /app/input/background.mp4 \
  /app/output/result.mp4
```

### 4. エイリアスの設定（オプション）

```bash
# ~/.bashrc または ~/.zshrc に追加
alias video-merge='docker-compose run --rm video-merger python3 video_merger_advanced.py'

# 使用例
video-merge /app/input/main.mp4 /app/input/bg.mp4 /app/output/result.mp4
```

## YouTube自動アップロード設定

### 1. YouTube Data API v3の有効化

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）
3. 「APIとサービス」→「ライブラリ」を選択
4. 「YouTube Data API v3」を検索して有効化

### 2. OAuth 2.0認証情報の作成

1. 「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuth クライアント ID」を選択
3. アプリケーションの種類: 「デスクトップアプリ」を選択
4. 名前を入力（例: "Video Merger Tool"）
5. 作成された認証情報をダウンロード
6. ファイル名を `youtube_credentials.json` に変更
7. `credentials/` フォルダに配置

### 3. 初回認証

```bash
# ローカル環境の場合
python3 youtube_uploader.py test_video.mp4 "テスト動画"

# Docker環境の場合
docker-compose run --rm video-merger python3 youtube_uploader.py \
  /app/input/test_video.mp4 "テスト動画"
```

初回実行時はブラウザが開き、Googleアカウントでの認証が求められます。

### 4. 動画合成＋自動アップロード

```bash
# ローカル環境
python3 merge_and_upload.py main.mp4 bg.mp4 "動画タイトル" \
  --size 1920x1080 \
  --text "※個人差があります" \
  --description "動画の説明" \
  --tags "タグ1,タグ2" \
  --privacy unlisted

# Docker環境
docker-compose run --rm video-merger python3 merge_and_upload.py \
  /app/input/main.mp4 \
  /app/input/bg.mp4 \
  "動画タイトル" \
  --privacy private
```

## フォルダ構造

```
video-merger-tool/
├── input/              # 入力動画を配置
├── output/             # 出力動画が保存される
├── credentials/        # YouTube認証情報
│   └── youtube_credentials.json
├── *.py               # Pythonスクリプト
├── Dockerfile         # Docker設定
├── docker-compose.yml # Docker Compose設定
└── requirements.txt   # Python依存関係
```

## セキュリティに関する注意

1. **認証情報の管理**
   - `youtube_credentials.json` は絶対にGitにコミットしない
   - `.gitignore` に含まれていることを確認
   - チームで共有する場合は、安全な方法で配布

2. **トークンファイル**
   - `token.pickle` も同様に共有しない
   - 各メンバーが個別に認証を行う

3. **Docker使用時**
   - 認証情報は読み取り専用でマウント (`:ro`)
   - コンテナ内に認証情報を含めない

## トラブルシューティング

### FFmpegが見つからない
```bash
# インストール確認
which ffmpeg
ffmpeg -version
```

### 日本語が表示されない
- Dockerを使用することで環境差を解消
- またはシステムに日本語フォントをインストール

### YouTube APIエラー
- API割り当て制限を確認（1日あたりの制限あり）
- 認証情報が正しいか確認
- APIが有効になっているか確認

### Dockerでの権限エラー
```bash
# 出力フォルダの権限を変更
chmod 777 output/
```

## サポート

問題が解決しない場合は、以下の情報を含めて報告してください：
- 使用OS
- エラーメッセージの全文
- 実行したコマンド
- 動画ファイルの形式とサイズ