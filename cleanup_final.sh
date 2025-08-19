#!/bin/bash

echo "======================================"
echo "本番ルート死守のためのクリーンアップ"
echo "======================================"
echo ""
echo "【削除対象】"
echo ""
echo "1. 紛らわしいテストファイル（全て）"
echo "2. バックアップディレクトリ"
echo "3. 不要なyoutube_uploader.py（本番はproduction_disapproval_handler.pyに統合済み）"
echo "4. テスト用の一時ファイル"
echo ""
echo "【残すファイル】"
echo "  ✅ production_disapproval_handler.py（本番メイン）"
echo "  ✅ video_merger_auto_bg.py（背景合成）"
echo "  ✅ background_prompts.py（AI背景プロンプト）"
echo "  ✅ config.py（設定）"
echo "  ✅ automation/ディレクトリ（コア機能）"
echo "  ✅ credentials/ディレクトリ（認証情報）"
echo "  ✅ youtube_auth_setup/ディレクトリ（認証設定）"
echo ""

read -p "削除を実行しますか？ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "削除を実行します..."
    
    # テストファイルの削除
    rm -f test_*.py
    rm -f add_test_entry.py
    rm -f safe_test.py
    rm -f simulate_gas_processing.py
    
    # 検索・デバッグ用ファイルの削除
    rm -f check_*.py
    rm -f debug_*.py
    rm -f find_*.py
    rm -f search_*.py
    rm -f verify_*.py
    rm -f list_*.py
    rm -f improved_drive_finder.py
    
    # YouTubeアップロード関連の不要ファイル削除
    rm -f youtube_uploader.py  # 本番はproduction_disapproval_handler.pyに統合済み
    rm -f youtube_auth_for_channels.py
    rm -f auth_single_channel.py
    rm -f setup_new_channels.py
    rm -f office_auth_setup.py
    
    # バックアップディレクトリの削除
    rm -rf backup_youtube_uploaders/
    rm -rf test_environment/
    rm -rf test_files_backup/
    
    # _archiveディレクトリも削除（必要なら後で復元可能）
    rm -rf _archive/
    
    # キャッシュの削除
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -type f -name "*.pyc" -delete 2>/dev/null
    
    # 一時ファイルの削除
    rm -f *.mp4 2>/dev/null
    rm -f *.mov 2>/dev/null
    rm -f temp_* 2>/dev/null
    
    echo ""
    echo "✅ クリーンアップ完了！"
    echo ""
    echo "【残った本番ファイル】"
    ls -la *.py 2>/dev/null | grep -v "^total"
    echo ""
    echo "【本番ルート】"
    echo "1. production_disapproval_handler.py が不承認広告を検出"
    echo "2. Google Driveから動画をダウンロード"
    echo "3. video_merger_auto_bg.py で背景合成"
    echo "4. YouTubeにアップロード（統合済み）"
    echo "5. キューシートに登録"
    echo "6. GASが処理"
    echo ""
    echo "このルートは死守されました！"
else
    echo "キャンセルしました"
fi