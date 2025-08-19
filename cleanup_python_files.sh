#!/bin/bash

echo "Python側の不要ファイル整理スクリプト"
echo "======================================="

# 1. バックアップディレクトリを作成
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 2. テストファイルをバックアップ
echo "📦 テストファイルをバックアップ..."
mv test_*.py "$BACKUP_DIR/" 2>/dev/null
mv check_*.py "$BACKUP_DIR/" 2>/dev/null

# 3. 古い本番ファイルをバックアップして新しいものに置き換え
echo "🔄 本番ファイルを更新..."
if [ -f "production_disapproval_handler_multi.py" ]; then
    cp production_disapproval_handler.py "$BACKUP_DIR/production_disapproval_handler_old.py"
    cp production_disapproval_handler_multi.py production_disapproval_handler.py
    echo "✅ production_disapproval_handler.py を複数件対応版に更新"
fi

# 4. 出力ファイルの整理（30日以上古いものを削除）
echo "🗑️ 古い出力ファイルを削除..."
find ad-videos -name "*.mp4" -mtime +30 -delete 2>/dev/null
find outputs -name "*.mp4" -mtime +30 -delete 2>/dev/null
find test_output -name "*.mp4" -mtime +30 -delete 2>/dev/null

# 5. 一時ファイルの削除
echo "🧹 一時ファイルを削除..."
rm -f temp_bg_*.mp4 2>/dev/null
rm -f test_log_*.json 2>/dev/null

# 6. 不要なドキュメントをアーカイブ
echo "📚 古いドキュメントをアーカイブ..."
mkdir -p "$BACKUP_DIR/docs"
mv *_TEST_*.md "$BACKUP_DIR/docs/" 2>/dev/null

echo ""
echo "✅ 整理完了！"
echo "バックアップ先: $BACKUP_DIR"
echo ""
echo "📋 現在の本番ファイル:"
ls -la production_*.py
echo ""
echo "📁 残っている重要ファイル:"
ls -la automation/*.py