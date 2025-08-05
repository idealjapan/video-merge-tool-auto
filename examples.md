# 動画合成ツール 使用例集

## video_merger_advanced.py の使い方

### 基本的な使用方法

```bash
# ヘルプを表示
python3 video_merger_advanced.py -h

# 最もシンプルな使用（デフォルト設定）
python3 video_merger_advanced.py main.mp4 background.mp4 output.mp4
```

### 出力サイズを指定

```bash
# フルHD (1920x1080) で出力
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --size 1920x1080

# HD (1280x720) で出力
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --size 1280x720

# 正方形 (1080x1080) で出力（Instagram用など）
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --size 1080x1080

# 縦長 (720x1280) で出力（スマートフォン用）
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --size 720x1280
```

### メイン動画のサイズを調整

```bash
# メイン動画を60%のサイズに
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --main-scale 0.6

# メイン動画を90%のサイズに（大きめ）
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --main-scale 0.9

# メイン動画を50%のサイズに（小さめ）
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --main-scale 0.5
```

### 注意書きテキストを追加

```bash
# カスタムテキストを追加
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --text "※個人差があります"

# デフォルトの注意書きを使用
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --default-text

# 長いテキストも可能
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 --text "※この動画は演出です。実際の効果を保証するものではありません。"
```

### 複数のオプションを組み合わせ

```bash
# HD出力 + メイン動画70% + デフォルト注意書き
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 \
  --size 1280x720 \
  --main-scale 0.7 \
  --default-text

# フルHD + メイン動画60% + カスタムテキスト
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 \
  --size 1920x1080 \
  --main-scale 0.6 \
  --text "※効果には個人差があります"

# Instagram用正方形 + メイン動画80% + 注意書き
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 \
  --size 1080x1080 \
  --main-scale 0.8 \
  --text "詳細はプロフィールのリンクから"
```

### 短縮オプション

```bash
# 短縮オプションを使用
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 \
  -s 1920x1080 \
  -m 0.7 \
  -t "※個人差があります"

# デフォルトテキストの短縮オプション
python3 video_merger_advanced.py main.mp4 bg.mp4 output.mp4 -d
```

## よくある解像度

| 用途 | 解像度 | アスペクト比 | 使用例 |
|------|--------|------------|---------|
| フルHD | 1920x1080 | 16:9 | YouTube, 一般的な動画 |
| HD | 1280x720 | 16:9 | Web用動画, 軽量版 |
| 4K | 3840x2160 | 16:9 | 高品質動画 |
| Instagram正方形 | 1080x1080 | 1:1 | Instagramフィード |
| Instagram縦長 | 1080x1920 | 9:16 | Instagramストーリー, リール |
| TikTok | 1080x1920 | 9:16 | TikTok動画 |
| Twitter | 1280x720 | 16:9 | Twitter投稿 |

## 実用的な使用例

### 1. YouTube用の動画作成
```bash
python3 video_merger_advanced.py product.mp4 abstract_bg.mp4 youtube_video.mp4 \
  --size 1920x1080 \
  --main-scale 0.8 \
  --text "※結果には個人差があり、成果を保証するものではありません。"
```

### 2. Instagram広告用（正方形）
```bash
python3 video_merger_advanced.py ad_content.mp4 gradient_bg.mp4 instagram_ad.mp4 \
  --size 1080x1080 \
  --main-scale 0.7 \
  --text "期間限定キャンペーン中"
```

### 3. TikTok/リール用（縦長）
```bash
python3 video_merger_advanced.py demo.mp4 vertical_bg.mp4 tiktok_video.mp4 \
  --size 1080x1920 \
  --main-scale 0.6 \
  --text "フォローお願いします♪"
```

### 4. プレゼンテーション用
```bash
python3 video_merger_advanced.py presentation.mp4 corporate_bg.mp4 final_presentation.mp4 \
  --size 1920x1080 \
  --main-scale 0.85
```

## ヒント

1. **背景動画が短い場合**: 自動的にループされるので、2-3秒の短い背景動画でも問題ありません

2. **アスペクト比の違い**: 動画は自動的に中央に配置され、余白は黒で埋められます

3. **メインスケール**: 
   - 0.5-0.6: 背景を強調したい場合
   - 0.7-0.8: バランスの良い標準的な設定
   - 0.9-1.0: メイン動画を大きく見せたい場合

4. **テキストサイズ**: 出力解像度に応じて自動的に調整されます