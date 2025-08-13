#!/bin/bash

echo "==================================="
echo "広告自動処理システムのセットアップ"
echo "==================================="

# 必要なディレクトリを作成
echo "ディレクトリを作成中..."
mkdir -p credentials
mkdir -p temp_videos
mkdir -p logs

# Pythonパッケージのインストール
echo "必要なPythonパッケージをインストール中..."
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 設定ファイルの確認
echo ""
echo "以下の設定ファイルを準備してください："
echo ""
echo "1. credentials/google_service_account.json"
echo "   - Google Cloud ConsoleでService Accountを作成"
echo "   - JSONキーをダウンロードして配置"
echo "   - スプレッドシートへのアクセス権限を付与"
echo ""
echo "2. credentials/youtube_client_secrets.json"
echo "   - Google Cloud ConsoleでOAuth 2.0クライアントIDを作成"
echo "   - JSONをダウンロードして配置"
echo ""
echo "3. automation/config.py を編集"
echo "   - SPREADSHEET_NAME を実際のスプレッドシート名に変更"
echo ""

# cronジョブの設定例を表示
echo "==================================="
echo "cronジョブの設定（5分ごとに実行）"
echo "==================================="
echo ""
echo "以下のコマンドでcrontabを編集："
echo "crontab -e"
echo ""
echo "以下の行を追加："
echo "*/5 * * * * cd $(pwd) && /usr/bin/python3 automation/ad_processor.py >> logs/cron.log 2>&1"
echo ""

# テスト実行の案内
echo "==================================="
echo "テスト実行"
echo "==================================="
echo ""
echo "設定完了後、以下のコマンドでテスト実行できます："
echo "python3 automation/ad_processor.py"
echo ""

# 実行権限を付与
chmod +x automation/ad_processor.py

echo "セットアップ完了！"