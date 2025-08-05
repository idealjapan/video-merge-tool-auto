# 速度最適化ガイド

## 現在のボトルネック分析

1. **Replicate API（80%）**: 背景動画生成に30-40秒
2. **FFmpeg処理（15%）**: 動画合成に5-10秒
3. **その他（5%）**: ファイルアップロード/ダウンロード

## 改善案（コスト効率順）

### 1. 背景動画のプリセット化（無料・即効性あり）

```python
# video_merger_auto_bg.pyに追加
class PresetBackgrounds:
    """事前生成した背景動画を使用"""
    
    PRESETS = {
        "forest_vertical": "https://example.com/forest_9x16.mp4",
        "ocean_vertical": "https://example.com/ocean_9x16.mp4",
        "forest_horizontal": "https://example.com/forest_16x9.mp4",
        "ocean_horizontal": "https://example.com/ocean_16x9.mp4",
    }
    
    @staticmethod
    def get_random_background(orientation):
        # ランダムに事前生成した背景を選択
        # 処理時間：30秒 → 1秒
```

### 2. より高速なAI APIの使用（月額$10〜）

- **Runway ML Turbo**: 20秒で生成（Replicateの半分）
- **fal.ai**: 10倍高速と謳っている
- **Stability AI**: 画像生成は高速、動画も期待できる

### 3. ハイブリッドアプローチ（推奨）

```python
def generate_background(self, orientation, duration):
    # 1. まず高速なプリセットで処理
    if self.use_preset:
        return self.get_preset_background(orientation)
    
    # 2. プレミアムユーザーはAI生成
    elif self.is_premium:
        return self.generate_with_replicate(orientation, duration)
    
    # 3. 通常ユーザーはキャッシュから
    else:
        return self.get_cached_background(orientation)
```

### 4. EC2最適化（月額$20〜）

現在：t2.micro（1 vCPU、1GB RAM）
推奨：t3.small（2 vCPU、2GB RAM）

```bash
# FFmpeg並列処理が可能に
# 処理時間：10秒 → 3秒
```

### 5. CDN/S3活用（月額$5〜）

```python
# 生成済み動画をS3にキャッシュ
def get_or_create_background(self, params_hash):
    # S3から既存の背景を検索
    cached = s3.get_object(Bucket='backgrounds', Key=params_hash)
    if cached:
        return cached['Body'].read()
    
    # なければ生成してS3に保存
    new_bg = self.generate_background()
    s3.put_object(Bucket='backgrounds', Key=params_hash, Body=new_bg)
    return new_bg
```

## 実装優先順位

1. **背景プリセット**（1日で実装可能）
   - 10-20個の背景を事前生成
   - 処理時間：40秒 → 10秒

2. **S3キャッシュ**（2-3日で実装可能）
   - 同じパラメータの背景を再利用
   - 2回目以降：40秒 → 5秒

3. **高速API導入**（1週間で実装可能）
   - Runway MLまたはfal.ai
   - 処理時間：40秒 → 20秒

4. **EC2アップグレード**（即日可能）
   - t2.micro → t3.small
   - 月額約$15追加

## 期待される改善

- 現在：40-50秒/動画
- プリセット実装後：10-15秒/動画（75%高速化）
- 全対策実装後：5-10秒/動画（80-90%高速化）