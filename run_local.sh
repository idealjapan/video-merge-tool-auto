#!/bin/bash

# ローカル環境用起動スクリプト

# .env.localファイルを読み込む
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
else
    echo "Error: .env.local file not found!"
    exit 1
fi

# 必要なディレクトリを作成
mkdir -p uploads outputs

# Flaskアプリケーションを起動
echo "Starting Video Merger Tool on http://localhost:5555"
python3 web_app_auto.py