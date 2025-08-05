# 動画合成ツール セットアップガイド

## 🚀 クイックスタート（初心者向け）

### 必要なもの
1. Replicate APIキー（[こちら](https://replicate.com/)で無料登録）
2. 5分程度の時間

### Windows向け簡単セットアップ

1. **Pythonのインストール**
   - [Python公式サイト](https://www.python.org/downloads/)から最新版をダウンロード
   - インストール時に「Add Python to PATH」にチェック

2. **FFmpegのインストール**
   - [FFmpeg公式](https://www.gyan.dev/ffmpeg/builds/)から「full」版をダウンロード
   - C:\ffmpeg に解凍
   - システム環境変数のPATHに C:\ffmpeg\bin を追加

3. **ツールのダウンロード**
   - このリポジトリをZIPでダウンロード
   - 好きな場所に解凍

4. **セットアップ**
   ```cmd
   cd video-merger-tool
   pip install flask flask-cors requests
   ```

5. **設定ファイルの作成**
   - `.env.local`ファイルを新規作成
   - 以下を記入（YOUR_API_KEYを実際のキーに置き換え）：
   ```
   REPLICATE_API_TOKEN=YOUR_API_KEY
   FLASK_PORT=5555
   ```

6. **起動**
   ```cmd
   python web_app_auto.py
   ```

### Mac向け簡単セットアップ

1. **Homebrewのインストール**（ターミナルで実行）
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **必要なソフトのインストール**
   ```bash
   brew install python ffmpeg
   pip3 install flask flask-cors requests
   ```

3. **ツールのセットアップ**
   ```bash
   # ダウンロード
   git clone [リポジトリURL]
   cd video-merger-tool
   
   # 設定ファイル作成
   echo "REPLICATE_API_TOKEN=YOUR_API_KEY" > .env.local
   
   # 起動
   ./run_local.sh
   ```

## 📱 使い方

1. ブラウザで http://localhost:5555 を開く
2. 動画をドラッグ＆ドロップ
3. 「動画を合成」をクリック
4. 完成したらダウンロード

## ❓ よくある質問

**Q: 動画のサイズ制限は？**
A: 500MBまで対応

**Q: どんな動画形式に対応？**
A: MP4, AVI, MOV, MKV, WebM

**Q: 処理時間は？**
A: 5秒の動画で約30-60秒

**Q: 料金は？**
A: Replicate APIの使用料のみ（1動画あたり1-2円程度）