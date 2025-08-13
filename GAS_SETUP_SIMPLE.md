# 🚀 GAS側の簡単セットアップ

## 必要なファイル（2つだけ！）

### 1. キュー処理システム.js
既に作成済み：`/google-ads-auto-replacer/キュー処理システム.js`

### 2. 既存の広告差し替え自動化.js
既にあるはず

## セットアップ手順（5分で完了）

### ステップ1: スプレッドシートを開く
https://docs.google.com/spreadsheets/d/1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U/

### ステップ2: Apps Scriptを開く
メニュー → 拡張機能 → Apps Script

### ステップ3: コードを追加
1. 新しいファイルを作成（＋ボタン → スクリプト）
2. `キュー処理システム.js`の内容をコピペ
3. 保存（Ctrl+S）

### ステップ4: トリガー設定（自動実行）
1. 時計アイコン（トリガー）をクリック
2. 「トリガーを追加」
3. 設定：
   - 実行する関数: `processQueueMain`
   - イベントのソース: 時間主導型
   - 時間ベースのトリガー: 5分ごと
4. 保存

## テスト方法

### 手動テスト（まずはこれ）
1. Apps Scriptエディタで
2. 関数を選択: `testQueueProcessing`
3. 実行ボタンをクリック
4. スプレッドシートの「広告差し替えキュー」シートを確認

### 確認ポイント
- ✅ TEST_で始まる行のステータスが変わる
- ✅ pending → processing → completed
- ✅ エラーが出ない

## ⚠️ 注意事項

### 本番モードにする前に
1. TEST_で始まるデータでテスト
2. 問題なければ本番データで実行

### エラーが出た場合
- 「DisapprovalChecker is not defined」→ 審査落ちチェック.jsも追加
- 「AdReplacementManager is not defined」→ 広告差し替え自動化.jsも追加

これだけです！