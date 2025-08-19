#!/bin/bash

echo "=============================================="
echo "重複・不要ファイルの削除スクリプト"
echo "=============================================="
echo ""
echo "以下のファイルは不要です（重複または使用していない）："
echo ""

# 不要なYouTubeアップロード関連ファイル
echo "【YouTubeアップロード関連】"
echo "  - youtube_uploader.py (archiveから復元した不要なコピー)"
echo "  - backup_youtube_uploaders/ (全て不要なバックアップ)"
echo "  - _archive/automation/youtube_uploader.py"
echo "  - _archive/automation/youtube_uploader_unified.py"
echo "  - _archive/automation/youtube_url_logger.py"
echo "  - test_environment/mock_youtube_uploader.py (テスト用モック)"
echo ""

echo "【不要なテストファイル】"
echo "  - test_complete_flow.py (入力待ちバグあり)"
echo "  - test_production_flow.py (入力待ちバグあり)"
echo "  - test_python_full_flow.py (入力待ちバグあり)"
echo ""

echo "【その他の不要ファイル】"
echo "  - youtube_auth_setup.zip (バックアップzip)"
echo "  - test_input_video.mov (テスト動画)"
echo ""

read -p "これらのファイルを削除しますか？ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "削除を実行します..."
    
    # YouTubeアップロード関連の削除
    rm -f youtube_uploader.py
    rm -rf backup_youtube_uploaders/
    rm -f _archive/automation/youtube_uploader.py
    rm -f _archive/automation/youtube_uploader_unified.py
    rm -f _archive/automation/youtube_url_logger.py
    rm -f test_environment/mock_youtube_uploader.py
    
    # 不要なテストファイルの削除
    rm -f test_complete_flow.py
    rm -f test_production_flow.py
    rm -f test_python_full_flow.py
    
    # その他
    rm -f youtube_auth_setup.zip
    rm -f test_input_video.mov
    
    # キャッシュも削除
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    
    echo "✅ 削除完了"
else
    echo "キャンセルしました"
fi