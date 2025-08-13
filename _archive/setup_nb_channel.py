#!/usr/bin/env python3
"""
NBチャンネルの再設定（正しいアカウントで認証）
"""
import os
from pathlib import Path

# 既存のトークンをクリア
token_path = Path("credentials/youtube_nb_token.pickle")
if token_path.exists():
    os.remove(token_path)
    print("既存のトークンを削除しました")

print("=" * 60)
print("NBチャンネルの再設定")
print("=" * 60)
print("\n重要: 次の認証画面では、")
print("**NBチャンネルを所有しているGoogleアカウント**")
print("を選択してください。")
print("\n複数のチャンネルがある場合は、")
print("NBチャンネルがあるアカウントを選んでください。")
print("=" * 60)

input("\nEnterキーを押して続行...")

# テストアップロードを実行
import sys
sys.path.append(str(Path(__file__).parent))
from test_youtube_nb import test_nb_upload

test_nb_upload()