# Google Drive API セットアップガイド

## 1. Google Cloud Consoleでの設定

### ステップ1: プロジェクト作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新規プロジェクトを作成（または既存のプロジェクトを選択）
3. プロジェクト名: `video-merger-automation`（任意）

### ステップ2: Google Drive APIを有効化
1. 左メニューから「APIとサービス」→「ライブラリ」
2. 「Google Drive API」を検索
3. 「有効にする」をクリック

### ステップ3: サービスアカウント作成
1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「サービスアカウント」
3. サービスアカウント名: `video-merger-service`（任意）
4. 「作成して続行」

### ステップ4: キーの作成
1. 作成したサービスアカウントをクリック
2. 「キー」タブ→「鍵を追加」→「新しい鍵を作成」
3. 形式：JSON
4. ダウンロードされたJSONファイルを保存

## 2. Google Driveの準備

### ステップ1: 共有フォルダ作成
1. Google Driveにアクセス
2. 新規フォルダ作成: `広告動画`
3. フォルダを右クリック→「共有」

### ステップ2: サービスアカウントに権限付与
1. JSONファイル内の`client_email`をコピー
   例: `video-merger@project-name.iam.gserviceaccount.com`
2. フォルダの共有設定でこのメールアドレスを追加
3. 権限: 「閲覧者」または「編集者」

### ステップ3: フォルダIDの取得（オプション）
1. フォルダを開く
2. URLから`folders/`の後の文字列をコピー
   例: `https://drive.google.com/drive/folders/1abc2def3ghi` → `1abc2def3ghi`

## 3. プロジェクトへの設定

### ファイル配置
```bash
# 認証情報ディレクトリを作成
mkdir -p credentials

# ダウンロードしたJSONファイルをコピー
cp ~/Downloads/your-service-account-key.json credentials/google_service_account.json
```

### 必要なパッケージインストール
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 4. 環境変数の設定（オプション）

`.env`ファイルに追加:
```
GOOGLE_DRIVE_FOLDER_ID=1abc2def3ghi  # 特定フォルダに限定する場合
```

## 5. 動作確認

```bash
# テストスクリプト実行
python3 test_google_drive.py
```

## トラブルシューティング

### 「権限がありません」エラー
- サービスアカウントのメールアドレスがフォルダに共有されているか確認
- 共有権限が「閲覧者」以上になっているか確認

### 「APIが有効になっていません」エラー
- Google Cloud ConsoleでGoogle Drive APIが有効になっているか確認
- プロジェクトIDが正しいか確認

### 「認証情報が見つかりません」エラー
- JSONファイルのパスが正しいか確認
- ファイル名が`google_service_account.json`になっているか確認

## セキュリティ注意事項
- **重要**: `google_service_account.json`は絶対にGitにコミットしない
- `.gitignore`に`credentials/`を追加済みか確認
- 本番環境では環境変数や秘密管理サービスを使用