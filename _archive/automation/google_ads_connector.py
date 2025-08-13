#!/usr/bin/env python3
"""
Google Ads Auto Replacer連携モジュール
YouTubeアップロード後に自動的にGoogle Ads差し替えシステムに動画URLを送信
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class GoogleAdsConnector:
    """Google Ads Auto Replacerとの連携クラス"""
    
    def __init__(self, web_app_url: Optional[str] = None, api_token: Optional[str] = None):
        """
        初期化
        
        Args:
            web_app_url: Google Apps ScriptのWeb Apps URL
            api_token: API認証トークン（オプション）
        """
        # 環境変数から設定を読み込み
        self.web_app_url = web_app_url or os.getenv('GOOGLE_ADS_WEB_APP_URL')
        self.api_token = api_token or os.getenv('GOOGLE_ADS_API_TOKEN')
        
        if not self.web_app_url:
            logger.warning("Google Ads Web App URLが設定されていません")
    
    def send_video_url(
        self,
        video_url: str,
        project_name: str,
        ad_name: str,
        video_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        動画URLをGoogle Ads Auto Replacerに送信
        
        Args:
            video_url: YouTube動画のURL
            project_name: 案件名
            ad_name: 広告名
            video_name: 動画名（オプション）
            metadata: 追加メタデータ（オプション）
            
        Returns:
            dict: APIレスポンス
        """
        if not self.web_app_url:
            error_msg = "Google Ads Web App URLが設定されていません"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        
        # リクエストペイロード作成
        payload = {
            'videoUrl': video_url,
            'projectName': project_name,
            'adName': ad_name,
            'videoName': video_name or ad_name,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        
        # APIトークンがある場合は追加
        if self.api_token:
            payload['apiToken'] = self.api_token
        
        try:
            logger.info(f"Google Ads APIに送信: {project_name} - {ad_name}")
            logger.debug(f"ペイロード: {json.dumps(payload, ensure_ascii=False)}")
            
            # POSTリクエスト送信
            response = requests.post(
                self.web_app_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            # レスポンス処理
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    logger.info(f"Google Ads差し替え成功: {result.get('data', {})}")
                else:
                    logger.error(f"Google Ads差し替え失敗: {result.get('error')}")
                
                return result
            else:
                error_msg = f"HTTPエラー: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = "リクエストタイムアウト"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"リクエストエラー: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except json.JSONDecodeError as e:
            error_msg = f"JSONパースエラー: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"予期しないエラー: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def send_batch_videos(
        self,
        videos: list
    ) -> Dict[str, Any]:
        """
        複数の動画URLをバッチで送信
        
        Args:
            videos: 動画情報のリスト
                [
                    {
                        'video_url': 'https://youtube.com/...',
                        'project_name': '案件名',
                        'ad_name': '広告名',
                        'video_name': '動画名'（オプション）
                    },
                    ...
                ]
                
        Returns:
            dict: 処理結果サマリー
        """
        results = {
            'total': len(videos),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        for video_info in videos:
            result = self.send_video_url(
                video_url=video_info.get('video_url'),
                project_name=video_info.get('project_name'),
                ad_name=video_info.get('ad_name'),
                video_name=video_info.get('video_name')
            )
            
            if result.get('success'):
                results['success'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append({
                'ad_name': video_info.get('ad_name'),
                'result': result
            })
        
        logger.info(f"バッチ処理完了: 成功 {results['success']}/{results['total']}")
        return results
    
    def test_connection(self) -> bool:
        """
        接続テスト
        
        Returns:
            bool: 接続成功時True
        """
        if not self.web_app_url:
            logger.error("Web App URLが設定されていません")
            return False
        
        try:
            # テスト用のダミーデータで送信
            result = self.send_video_url(
                video_url='https://www.youtube.com/watch?v=test',
                project_name='接続テスト',
                ad_name='テスト広告'
            )
            
            # エラーメッセージが「不承認広告が見つかりません」の場合は接続成功とみなす
            if result.get('error') and '不承認広告が見つかりません' in result.get('error', ''):
                logger.info("Google Ads API接続テスト成功")
                return True
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"接続テスト失敗: {e}")
            return False


# スタンドアロン実行用
if __name__ == "__main__":
    # テスト実行
    connector = GoogleAdsConnector()
    
    # 環境変数からテストデータ取得
    test_video_url = os.getenv('TEST_VIDEO_URL', 'https://www.youtube.com/watch?v=example123')
    test_project = os.getenv('TEST_PROJECT_NAME', 'テスト案件')
    test_ad = os.getenv('TEST_AD_NAME', 'テスト広告01')
    
    print(f"Google Ads連携テスト")
    print(f"Web App URL: {connector.web_app_url}")
    print(f"API Token設定: {'あり' if connector.api_token else 'なし'}")
    
    # 接続テスト
    if connector.test_connection():
        print("✅ 接続テスト成功")
        
        # 実際の送信テスト
        result = connector.send_video_url(
            video_url=test_video_url,
            project_name=test_project,
            ad_name=test_ad
        )
        
        print(f"送信結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print("❌ 接続テスト失敗")