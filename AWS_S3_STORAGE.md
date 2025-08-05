# AWS S3を使った動画保存システム

## 現在の問題点
- EC2のディスク容量に制限（無料枠は8GB）
- 複数ユーザーで共有困難
- バックアップなし

## S3を使った解決策

### 保存フロー
```
1. メイン動画アップロード → S3に保存
2. 背景動画生成 → S3に保存
3. 合成動画作成 → S3に保存
4. ダウンロードリンク生成（24時間有効）
```

### フォルダ構造（S3）
```
your-video-bucket/
├── inputs/
│   └── 2024-08-04/
│       └── job-uuid/
│           └── main.mp4
├── backgrounds/
│   └── 2024-08-04/
│       └── job-uuid/
│           └── background.mp4
├── outputs/
│   └── 2024-08-04/
│       └── job-uuid/
│           └── final.mp4
└── logs/
    └── processing.log
```

## コスト
- **S3ストレージ**: $0.023/GB/月
- **データ転送**: 
  - アップロード: 無料
  - ダウンロード: $0.09/GB（最初の100GB/月は無料）

## 実装例

### 1. 環境変数設定
```bash
export S3_BUCKET_NAME=your-video-bucket
export AWS_REGION=ap-northeast-1
export STORAGE_MODE=s3  # 's3' or 'local'
```

### 2. S3自動削除設定
```json
{
  "Rules": [
    {
      "Id": "DeleteOldVideos",
      "Status": "Enabled",
      "Prefix": "outputs/",
      "Expiration": {
        "Days": 7
      }
    }
  ]
}
```

## メリット
1. **無制限の容量**（実質的に）
2. **高可用性**（99.999999999%）
3. **自動バックアップ**
4. **CDN連携可能**（CloudFront）
5. **署名付きURL**でセキュア

## アクセス方法

### Webインターフェース経由
- ダウンロードボタン → 署名付きURL → ブラウザでダウンロード

### 直接URL
- 24時間有効な署名付きURL
- メールやチャットで共有可能

### プログラムから
```python
# S3から直接ダウンロード
aws s3 cp s3://bucket/outputs/2024-08-04/job-id/final.mp4 ./

# 署名付きURL生成
url = s3_client.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucket, 'Key': key},
    ExpiresIn=86400  # 24時間
)
```