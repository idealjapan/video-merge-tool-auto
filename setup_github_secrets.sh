#!/bin/bash

echo "======================================"
echo "GitHub Secrets設定ガイド"
echo "======================================"
echo ""
echo "GitHub リポジトリの Settings > Secrets and variables > Actions で以下を設定："
echo ""
echo "【必須のSecrets】"
echo ""
echo "1. GOOGLE_SERVICE_ACCOUNT_JSON"
echo "   以下のコマンドの出力をコピー："
echo "   cat credentials/google_service_account.json"
echo ""
echo "2. REPLICATE_API_TOKEN"
echo "   値: r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio"
echo ""
echo "3. TOKEN_NB_PICKLE (base64エンコード)"
echo "   以下のコマンドの出力をコピー："
echo "   base64 credentials/token_NB.pickle"
echo ""
echo "4. TOKEN_OM_PICKLE (base64エンコード)"
echo "   以下のコマンドの出力をコピー："
echo "   base64 credentials/token_OM.pickle"
echo ""
echo "5. TOKEN_SBC_PICKLE (base64エンコード)"
echo "   以下のコマンドの出力をコピー："
echo "   base64 credentials/token_SBC.pickle"
echo ""
echo "6. CLIENT_SECRETS_JSON"
echo "   以下のコマンドの出力をコピー："
echo "   cat credentials/client_secrets.json"
echo ""
echo "======================================"
echo ""
echo "設定用コマンドを実行しますか？ (y/n)"
read -p "> " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "【1. GOOGLE_SERVICE_ACCOUNT_JSON】"
    echo "-----------------------------------"
    cat credentials/google_service_account.json
    echo ""
    echo ""
    
    echo "【2. REPLICATE_API_TOKEN】"
    echo "-----------------------------------"
    echo "r8_b8yPR5AADdMQz0VArWeBNE6zdfjJ4s22rguio"
    echo ""
    
    echo "【3. TOKEN_NB_PICKLE (base64)】"
    echo "-----------------------------------"
    base64 -i credentials/token_NB.pickle
    echo ""
    echo ""
    
    echo "【4. TOKEN_OM_PICKLE (base64)】"
    echo "-----------------------------------"
    base64 -i credentials/token_OM.pickle
    echo ""
    echo ""
    
    echo "【5. TOKEN_SBC_PICKLE (base64)】"
    echo "-----------------------------------"
    base64 -i credentials/token_SBC.pickle
    echo ""
    echo ""
    
    echo "【6. CLIENT_SECRETS_JSON】"
    echo "-----------------------------------"
    cat credentials/client_secrets.json
    echo ""
    echo ""
    
    echo "======================================"
    echo "上記の値をGitHub Secretsに設定してください"
    echo "設定ページ: https://github.com/[your-username]/[your-repo]/settings/secrets/actions"
    echo "======================================"
fi