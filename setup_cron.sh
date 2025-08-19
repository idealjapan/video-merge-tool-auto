#!/bin/bash

# Pythonスクリプトのcronジョブ設定

echo "==================================================="
echo "広告自動差し替えシステム - cronジョブ設定"
echo "==================================================="

# 設定
PYTHON_PATH="/usr/bin/python3"
PROJECT_DIR="/Users/shingo/Desktop/アプリ開発/video-merger-tool-Auto"
LOG_DIR="/Users/shingo/Desktop/アプリ開発/logs"

# ログディレクトリ作成
mkdir -p "$LOG_DIR"

# cronジョブの内容
CRON_JOB="0 * * * * cd $PROJECT_DIR && GOOGLE_APPLICATION_CREDENTIALS=$PROJECT_DIR/credentials/google_service_account.json REPLICATE_API_TOKEN=r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio $PYTHON_PATH production_disapproval_handler.py >> $LOG_DIR/ad_replacement.log 2>&1"

echo "以下のcronジョブを設定します："
echo "$CRON_JOB"
echo ""

# 現在のcrontabを表示
echo "現在のcrontab:"
crontab -l 2>/dev/null || echo "（設定なし）"
echo ""

# ユーザーに確認
read -p "このcronジョブを追加しますか？ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 既存のcrontabを取得して新しいジョブを追加
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ cronジョブを追加しました"
    echo ""
    echo "確認:"
    crontab -l | grep "production_disapproval_handler"
else
    echo "キャンセルしました"
fi

echo ""
echo "==================================================="
echo "その他の便利なコマンド:"
echo "==================================================="
echo "# ログを確認"
echo "tail -f $LOG_DIR/ad_replacement.log"
echo ""
echo "# cronジョブを確認"
echo "crontab -l"
echo ""
echo "# cronジョブを編集"
echo "crontab -e"
echo ""
echo "# cronジョブを削除"
echo "crontab -r"
echo ""
echo "# 手動実行"
echo "cd $PROJECT_DIR && python3 production_disapproval_handler.py"