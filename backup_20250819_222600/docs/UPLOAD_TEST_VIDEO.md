# テスト用動画のアップロード手順

## 📹 アップロードする動画
場所: `/Users/shingo/Desktop/アプリ開発/video-merger-tool-Auto/test_environment/temp_videos/`
- `main_video.mov` または `テスト広告.mov`

## 📁 Google Driveフォルダ
フォルダURL: https://drive.google.com/drive/folders/1GQSw_hQEsTCKAjtt9FyVmZryVUXsbyLL

## 🔧 手順

### 1. Google Driveフォルダを開く
上記URLをブラウザで開く

### 2. 動画をアップロード
- ドラッグ&ドロップまたは「新規」→「ファイルのアップロード」
- ファイル名は「広告名.mp4」形式（例：`テスト広告.mov`、`メイン広告.mp4`）

### 3. 共有設定を確認
**重要**: フォルダが以下のメールアドレスと共有されているか確認
```
video-merger-service@video-merge-automation.iam.gserviceaccount.com
```

権限: 「閲覧者」以上

### 4. テスト実行
```bash
python3 test_google_drive_simple.py
```

## 🧪 動画検索テスト

特定の広告名で検索テスト：
```python
from automation.google_drive_finder import GoogleDriveFinder

finder = GoogleDriveFinder()
video = finder.find_and_download("テスト広告")
if video:
    print(f"ダウンロード成功: {video}")
```