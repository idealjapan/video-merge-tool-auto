#!/usr/bin/env python3
"""
YouTubeチャンネル認証セットアップツール
オフィスのPCでチャンネル所有者が実行してください
"""

import os
import pickle
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_channel(channel_name):
    """YouTubeチャンネルの認証を行う"""
    
    print(f"=== {channel_name}チャンネルの認証セットアップ ===")
    print()
    
    # クライアントシークレットファイルを確認
    client_secret_file = 'client_secret.json'
    if not os.path.exists(client_secret_file):
        print("❌ エラー: client_secret.jsonが見つかりません")
        print("   このファイルと同じフォルダに配置してください")
        input("\nEnterキーを押して終了...")
        return False
    
    try:
        # OAuth2フローを開始
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_file, SCOPES
        )
        
        print("📌 ブラウザが開きます...")
        print("   1. Googleアカウントでログイン")
        print(f"   2. {channel_name}チャンネルの所有者アカウントを選択")
        print("   3. 「許可」をクリック")
        print()
        
        # ブラウザで認証
        creds = flow.run_local_server(port=0)
        
        # 認証情報を保存
        output_file = f'youtube_token_{channel_name}.pickle'
        with open(output_file, 'wb') as token:
            pickle.dump(creds, token)
        
        # 認証テスト
        print("\n認証テスト中...")
        youtube = build('youtube', 'v3', credentials=creds)
        
        # チャンネル情報を取得
        request = youtube.channels().list(
            part="snippet",
            mine=True
        )
        response = request.execute()
        
        if response['items']:
            channel_title = response['items'][0]['snippet']['title']
            print(f"✅ 認証成功！")
            print(f"   チャンネル: {channel_title}")
            print(f"   トークンファイル: {output_file}")
            print()
            print("⚠️ 重要: このファイルを開発者に渡してください")
            print(f"   ファイル名: {output_file}")
            return True
        else:
            print("❌ チャンネル情報を取得できませんでした")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("YouTube自動アップロード - チャンネル認証セットアップ")
    print("=" * 60)
    print()
    print("このツールでYouTubeチャンネルの認証設定を行います。")
    print("所要時間: 約5分")
    print()
    
    # チャンネル選択
    print("認証するチャンネルを選択してください:")
    print("1. NB チャンネル")
    print("2. OM チャンネル")
    print("3. SBC チャンネル")
    print("4. RL チャンネル")
    print()
    
    while True:
        choice = input("番号を入力 (1-4): ").strip()
        
        channel_map = {
            '1': 'NB',
            '2': 'OM',
            '3': 'SBC',
            '4': 'RL'
        }
        
        if choice in channel_map:
            channel_name = channel_map[choice]
            break
        else:
            print("1-4の番号を入力してください")
    
    print()
    success = authenticate_channel(channel_name)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ セットアップ完了！")
        print("=" * 60)
        print()
        print("次のステップ:")
        print(f"1. 生成された「youtube_token_{channel_name}.pickle」を")
        print("   開発者に送ってください")
        print()
        print("2. パスワードなどの機密情報は含まれていません")
        print("   （アクセストークンのみ）")
        print()
    else:
        print("\n認証に失敗しました。もう一度お試しください。")
    
    input("\nEnterキーを押して終了...")

if __name__ == "__main__":
    main()