#\!/bin/bash

# YouTube認証セットアップスクリプト
# オフィスのMacで実行してください

echo "=========================================="
echo "YouTube認証セットアップを開始します"
echo "=========================================="
echo

# Python3の確認
if \! command -v python3 &> /dev/null; then
    echo "❌ Python3がインストールされていません"
    echo "   Homebrewをインストール後、以下を実行してください:"
    echo "   brew install python3"
    exit 1
fi

# 必要なパッケージをインストール
echo "📦 必要なパッケージをインストール中..."
pip3 install --user google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 認証スクリプトを実行
echo
echo "🔐 認証を開始します..."
python3 office_auth_setup.py

echo
echo "セットアップ完了しました。"
