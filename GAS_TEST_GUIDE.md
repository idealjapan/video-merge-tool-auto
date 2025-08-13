# GAS連携テストガイド

## 🧪 テスト手順

### 準備
1. スプレッドシートを開く
   - URL: https://docs.google.com/spreadsheets/d/1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U/
   - 「広告差し替えキュー」シートを確認

2. Google Apps Scriptを開く
   - 拡張機能 → Apps Script

### ステップ1: Python側でテストデータ追加

```bash
cd /Users/shingo/Desktop/アプリ開発/video-merger-tool-Auto
python3 -c "
from automation.simple_queue_manager import SimpleQueueManager
from datetime import datetime

queue = SimpleQueueManager()
process_id = queue.add_to_queue(
    video_url='https://youtube.com/watch?v=test_gas',
    project_name='GASテスト案件',
    ad_name=f'TEST_GAS連携_{datetime.now().strftime(\"%H%M%S\")}'
)
print(f'✅ キューに追加: {process_id}')
"
```

### ステップ2: スプレッドシートで確認
1. 「広告差し替えキュー」シートを更新（F5）
2. 新しい行が追加されていることを確認
   - 処理ID: TEST_GAS連携_XXXXXX
   - ステータス: pending

### ステップ3: GAS側でテスト実行

Google Apps Scriptエディタで以下を貼り付けて実行：

```javascript
function quickTest() {
  // キューを確認
  const spreadsheetId = '1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U';
  const sheet = SpreadsheetApp.openById(spreadsheetId)
    .getSheetByName('広告差し替えキュー');
  
  const data = sheet.getDataRange().getValues();
  
  // TEST_で始まるpending行を探す
  for (let i = 1; i < data.length; i++) {
    if (data[i][0].startsWith('TEST_') && data[i][1] === 'pending') {
      console.log('テスト対象発見: ' + data[i][0]);
      
      // ステータスを更新
      const row = i + 1;
      sheet.getRange(row, 2).setValue('processing');
      console.log('→ processing に更新');
      
      Utilities.sleep(2000);  // 2秒待つ
      
      sheet.getRange(row, 2).setValue('completed');
      sheet.getRange(row, 12).setValue('テスト成功');
      console.log('→ completed に更新');
      
      return '✅ テスト成功';
    }
  }
  
  return '❌ TEST_で始まるpendingタスクが見つかりません';
}
```

実行方法：
1. 関数を選択: `quickTest`
2. 実行ボタンをクリック
3. 初回は権限を許可

### ステップ4: 結果確認
スプレッドシートを更新して、ステータスが変わったことを確認：
- pending → processing → completed

## 🔍 デバッグ方法

### ログの確認（GAS側）
```javascript
// Apps Scriptエディタで
// 表示 → ログ
```

### Python側でリアルタイム監視
```python
from automation.simple_queue_manager import SimpleQueueManager
import time

queue = SimpleQueueManager()
sheet = queue.spreadsheet.worksheet('広告差し替えキュー')

print("監視中... (Ctrl+Cで終了)")
while True:
    data = sheet.get_all_values()
    for row in data[1:]:
        if row[0].startswith('TEST_'):
            print(f"{row[0]}: {row[1]}")  # 処理ID: ステータス
    time.sleep(5)
```

## ⚠️ 注意事項

1. **API制限**
   - スプレッドシートAPI: 100リクエスト/100秒
   - 大量のテストは避ける

2. **テストデータの削除**
   ```javascript
   // GAS側でクリーンアップ
   function cleanup() {
     const sheet = SpreadsheetApp.openById('...')
       .getSheetByName('広告差し替えキュー');
     const data = sheet.getDataRange().getValues();
     
     for (let i = data.length - 1; i >= 1; i--) {
       if (data[i][0].startsWith('TEST_')) {
         sheet.deleteRow(i + 1);
       }
     }
   }
   ```

3. **本番モードとの切り替え**
   - TEST_プレフィックスがあるものだけテスト処理
   - 本番データには触らない

## 成功の確認ポイント

✅ Python → スプレッドシート（データ追加）
✅ GAS → スプレッドシート（データ読み取り）
✅ GAS → スプレッドシート（ステータス更新）
✅ Python → スプレッドシート（結果確認）

これらがすべて動作すれば、連携は成功です！