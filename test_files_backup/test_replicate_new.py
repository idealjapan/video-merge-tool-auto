#!/usr/bin/env python3
"""
Replicate API テスト（新バージョン）
"""
import os
import replicate

# APIキー設定
os.environ['REPLICATE_API_TOKEN'] = 'r8_byPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'

try:
    # Replicateクライアント初期化
    client = replicate.Client(api_token='r8_byPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio')
    
    # アカウント情報取得
    print("Replicate接続テスト...")
    
    # シンプルなモデルでテスト（Stable Diffusion）
    output = client.run(
        "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
        input={"prompt": "a beautiful sunset"}
    )
    
    print("✅ Replicate API接続成功！")
    print(f"出力: {output}")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    print("\n別の方法でテスト...")
    
    # 直接HTTPリクエスト
    import requests
    
    # 異なるヘッダー形式を試す
    headers_variants = [
        {'Authorization': 'Token r8_byPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'},
        {'Authorization': 'Bearer r8_byPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'},
        {'Authorization': 'r8_byPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'},
    ]
    
    for i, headers in enumerate(headers_variants, 1):
        print(f"\n形式{i}: {list(headers.values())[0][:20]}...")
        response = requests.get('https://api.replicate.com/v1/account', headers=headers)
        print(f"結果: {response.status_code}")
        if response.status_code == 200:
            print("✅ この形式で成功！")
            break