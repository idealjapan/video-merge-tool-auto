# OAuth アクセスエラーの解決方法

## エラー内容
「アクセスをブロック: YouTube Uploader は Google の審査プロセスを完了していません」

## 解決手順

### ステップ1: Google Cloud Consoleにアクセス

1. https://console.cloud.google.com/ を開く
2. プロジェクトを選択（YouTube Uploaderを作成したプロジェクト）

### ステップ2: テストユーザーを追加

1. 左メニューから「APIとサービス」→「OAuth同意画面」をクリック
2. 下にスクロールして「テストユーザー」セクションを探す
3. 「+ ADD USERS」ボタンをクリック
4. 以下のメールアドレスを追加：
   - ideal.office.information@gmail.com
   - その他使用したいGoogleアカウントのメールアドレス
5. 「保存」をクリック

### ステップ3: 再度認証を実行

```bash
cd /Users/shingo/Desktop/アプリ開発/video-merger-tool-Auto
python3 simple_youtube_setup.py
```

### 代替案: 開発者アカウントを使用

もしGoogle Cloud Consoleにアクセスできない場合：

1. YouTube Uploaderアプリを作成したGoogleアカウントでログイン
2. そのアカウントはデフォルトでテストユーザーとして登録されているはず

### チャンネルが表示されない問題

複数のチャンネルがある場合（ブランドアカウント）：

1. ログイン時にアカウント選択画面で適切なチャンネルを選択
2. YouTubeにログインして、右上のアイコンから「チャンネルを切り替える」で確認

### それでも解決しない場合

OAuth同意画面で「アプリを公開」を選択して本番環境に移行：
- ただし、これには数日かかる場合があります
- テスト用途なら上記のテストユーザー追加で十分です