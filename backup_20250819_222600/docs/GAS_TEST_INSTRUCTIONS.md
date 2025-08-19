# 📋 GAS連携テスト手順

## 1. GASコードのデプロイ

### ステップ1: スプレッドシートを開く
```
https://docs.google.com/spreadsheets/d/1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U/
```

### ステップ2: Apps Scriptエディタを開く
1. メニュー → 拡張機能 → Apps Script
2. 既存のコードがある場合はバックアップ

### ステップ3: 新しいコードを追加
1. 新しいファイルを作成（＋ボタン → スクリプト）
2. ファイル名: `キュー処理v2.gs`
3. `gas_queue_processor.js`の内容をコピペ
4. 保存（Ctrl+S）

## 2. 手動テスト

### テスト1: 基本動作確認
```javascript
// Apps Scriptエディタで実行
testQueueProcessing()
```

**確認項目:**
- ✅ 「広告キュー」シートが作成される
- ✅ TEST_で始まるテストデータが追加される
- ✅ ステータスが「待機中」→「処理中」→「完了」に変わる
- ✅ エラーが出ない

### テスト2: Python側からのデータ処理
```bash
# ローカルで実行
cd /Users/shingo/Desktop/アプリ開発/video-merger-tool-Auto
python3 test_gas_integration.py
```

その後、GASエディタで:
```javascript
processQueueFromSheets()
```

**確認項目:**
- ✅ Python側で追加したデータが処理される
- ✅ ステータスが正しく更新される
- ✅ 処理時間が記録される

## 3. トリガー設定（自動実行）

### 手動でトリガー設定
1. Apps Scriptエディタで時計アイコンをクリック
2. 「トリガーを追加」
3. 設定:
   - 実行する関数: `processQueueFromSheets`
   - イベントのソース: 時間主導型
   - 時間ベースのトリガー: 5分ごと
4. 保存

### またはコードで設定
```javascript
setupQueueTrigger()
```

## 4. 動作確認

### Python側でキューに追加
```python
from automation.simple_queue_manager import SimpleQueueManager

queue = SimpleQueueManager()
process_id = queue.add_to_queue(
    video_url="https://www.youtube.com/watch?v=xxx",
    project_name="NB",
    ad_name="テスト広告",
    video_name="テスト動画"
)
print(f"追加済み: {process_id}")
```

### スプレッドシートで確認
1. 「広告キュー」シートを開く
2. 5分待つ（またはGASで手動実行）
3. ステータスが「完了」になることを確認

## 5. トラブルシューティング

### エラー: シートが見つからない
→ シート名が「広告キュー」になっているか確認

### エラー: ステータスが更新されない
→ 列の位置が正しいか確認（B列がステータス）

### エラー: 日本語が文字化け
→ スプレッドシートの言語設定を確認

## 6. 本番運用への移行

### チェックリスト
- [ ] TEST_プレフィックスのデータで動作確認完了
- [ ] 実際のYouTube URLで動作確認
- [ ] Google Ads API連携部分の実装（必要に応じて）
- [ ] エラー通知の設定（Larkなど）
- [ ] トリガーの間隔調整（5分→適切な間隔）

## 注意事項

1. **YouTube保留問題対策**
   - 一度に処理する件数を3件に制限
   - 処理間隔を2秒空ける

2. **リトライ機能**
   - 最大3回まで自動リトライ
   - 失敗した場合は「失敗」ステータスで記録

3. **テストモード**
   - TEST_で始まる広告名は実際の処理をスキップ
   - 動作確認用に使用