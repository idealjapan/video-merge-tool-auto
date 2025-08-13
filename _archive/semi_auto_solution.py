#!/usr/bin/env python3
"""
半自動ソリューション
動画を生成してフォルダに保存 → 手動でYouTube Studioからアップロード
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

class SemiAutoUploader:
    """半自動アップロードヘルパー"""
    
    def __init__(self):
        # アップロード待ちフォルダを作成
        self.upload_folder = Path("ready_to_upload")
        self.upload_folder.mkdir(exist_ok=True)
        
        # メタデータフォルダ
        self.metadata_folder = Path("upload_metadata")
        self.metadata_folder.mkdir(exist_ok=True)
    
    def prepare_video(self, video_path: str, title: str, description: str):
        """
        動画をアップロード準備
        
        Args:
            video_path: 動画ファイルパス
            title: 動画タイトル
            description: 動画説明
        """
        # ファイル名を分かりやすく
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        new_filename = f"{timestamp}_{safe_title[:50]}.mp4"
        
        # 動画をコピー
        dest_path = self.upload_folder / new_filename
        shutil.copy2(video_path, dest_path)
        
        # メタデータを保存
        metadata_file = self.metadata_folder / f"{timestamp}_{safe_title[:50]}.txt"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(f"タイトル:\n{title}\n\n")
            f.write(f"説明:\n{description}\n\n")
            f.write(f"ファイル: {new_filename}\n")
            f.write(f"準備完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"\n✅ アップロード準備完了！")
        print(f"📁 動画: {dest_path}")
        print(f"📝 情報: {metadata_file}")
        
        return str(dest_path)
    
    def show_upload_instructions(self):
        """アップロード手順を表示"""
        print("\n" + "="*60)
        print("📤 YouTube Studioでアップロードする手順")
        print("="*60)
        print("\n1. YouTube Studioを開く:")
        print("   https://studio.youtube.com/")
        print("\n2. 右上の「作成」→「動画をアップロード」")
        print("\n3. ready_to_upload フォルダから動画を選択")
        print("\n4. upload_metadata フォルダからタイトルと説明をコピペ")
        print("\n5. 「次へ」を3回クリックして公開")
        print("\n" + "="*60)
    
    def list_pending_uploads(self):
        """アップロード待ちの動画一覧"""
        videos = list(self.upload_folder.glob("*.mp4"))
        
        if not videos:
            print("📭 アップロード待ちの動画はありません")
            return
        
        print(f"\n📦 アップロード待ち: {len(videos)}件")
        print("-" * 40)
        
        for video in sorted(videos):
            # 対応するメタデータを探す
            base_name = video.stem
            metadata_file = self.metadata_folder / f"{base_name}.txt"
            
            print(f"\n📹 {video.name}")
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[:2]:  # タイトル行のみ表示
                        if line.strip() and not line.startswith('タイトル:'):
                            print(f"   → {line.strip()}")
    
    def cleanup_uploaded(self, video_filename: str):
        """アップロード済みファイルをクリーンアップ"""
        video_path = self.upload_folder / video_filename
        if video_path.exists():
            video_path.unlink()
            print(f"✅ 削除: {video_filename}")
        
        # メタデータも削除
        metadata_path = self.metadata_folder / f"{video_path.stem}.txt"
        if metadata_path.exists():
            metadata_path.unlink()


# メイン処理
if __name__ == "__main__":
    helper = SemiAutoUploader()
    
    while True:
        print("\n" + "="*60)
        print("🎬 半自動YouTubeアップロードヘルパー")
        print("="*60)
        print("\n1. アップロード待ち一覧")
        print("2. アップロード手順を表示")
        print("3. アップロード済みをクリーンアップ")
        print("4. 終了")
        
        choice = input("\n選択 (1-4): ").strip()
        
        if choice == '1':
            helper.list_pending_uploads()
        elif choice == '2':
            helper.show_upload_instructions()
        elif choice == '3':
            helper.list_pending_uploads()
            filename = input("\n削除するファイル名: ").strip()
            if filename:
                helper.cleanup_uploaded(filename)
        elif choice == '4':
            break