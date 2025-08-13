#!/usr/bin/env python3
import requests

token = 'r8_byPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio'
headers = {'Authorization': f'Token {token}'}
response = requests.get('https://api.replicate.com/v1/account', headers=headers)

print(f'APIキーテスト: {response.status_code}')
if response.status_code != 200:
    print(f'エラー: {response.text}')
else:
    print('認証成功！')
    print(response.json())