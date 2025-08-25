#!/usr/bin/env python3
"""
審査状態シート（日別(YT)）の読み取り
不承認広告の検出と情報取得
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path
import gspread
from google.oauth2 import service_account

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApprovalStatusReader:
    """審査状態シートの読み取りクラス"""
    
    # スプレッドシート設定
    APPROVAL_SPREADSHEET_ID = '1yxEYTX-9e9PkIPCh62uJTvAigzyDHv_sSjTfv3qU9M0'
    APPROVAL_SHEET_NAME = '日別(YT)'
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        初期化
        
        Args:
            credentials_path: サービスアカウント認証ファイルのパス
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self._init_connection()
    
    def _init_connection(self):
        """Google Sheetsへの接続を初期化"""
        try:
            # 認証
            if not self.credentials_path:
                raise ValueError("認証ファイルパスが指定されていません")
            
            if not Path(self.credentials_path).exists():
                raise FileNotFoundError(f"認証ファイルが見つかりません: {self.credentials_path}")
            
            # サービスアカウント認証
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # gspreadクライアント初期化
            self.client = gspread.authorize(creds)
            
            # スプレッドシートを開く
            self.spreadsheet = self.client.open_by_key(self.APPROVAL_SPREADSHEET_ID)
            self.sheet = self.spreadsheet.worksheet(self.APPROVAL_SHEET_NAME)
            
            logger.info(f"審査状態シート接続成功: {self.APPROVAL_SHEET_NAME}")
            
        except Exception as e:
            logger.error(f"接続エラー: {e}")
            raise
    
    def get_disapproved_ads(self) -> List[Dict[str, str]]:
        """
        不承認広告を取得
        
        Returns:
            不承認広告のリスト [{
                'ad_group_name': '広告グループ名',
                'project_name': '案件名',
                'video_name': '動画名',
                'account_id': 'アカウントID',
                'status': '不承認'
            }, ...]
        """
        try:
            # シート全体を取得
            all_values = self.sheet.get_all_values()
            
            if len(all_values) < 6:  # ヘッダーが5行目
                logger.warning("データが見つかりません")
                return []
            
            disapproved_ads = []
            
            # データ行を処理（6行目から）
            for i, row in enumerate(all_values[5:], start=6):
                if len(row) < 28:  # AB列（インデックス27）まで必要
                    continue
                
                ad_group_name = str(row[0]).strip()  # A列: 広告グループ名
                
                # CP状態の確認（AA列 = インデックス26）
                if len(row) > 26:
                    cp_status = str(row[26]).strip().lower()  # AA列: CP状態
                    if cp_status in ['removed', 'paused']:
                        logger.info(f"CP状態が{cp_status}のためスキップ: {ad_group_name}")
                        continue
                
                # デマンドジェネレーションキャンペーンをスキップ
                if 'DG' in ad_group_name:
                    logger.info(f"デマンドジェネレーション広告をスキップ: {ad_group_name}")
                    continue
                
                approval_status = str(row[27]).strip()  # AB列: 承認ステータス
                account_id = str(row[25]).strip().replace('-', '')  # Z列: アカウントID
                
                # 不承認チェック
                if approval_status == '不承認' and ad_group_name:
                    # 広告グループ名を解析（例: "YT_案件名_動画名_MCC..."）
                    parts = ad_group_name.split('_')
                    
                    # YT_で始まる場合は2番目が案件名
                    if parts[0] == 'YT' and len(parts) > 1:
                        project_name = parts[1]  # NB, OM, SBC など
                        # MCCより前の部分を動画名として使用
                        video_name_parts = []
                        for part in parts[2:]:
                            if 'MCC' in part:
                                break
                            video_name_parts.append(part)
                        # 案件名を含めた完全な動画名を作成
                        video_name = f"{project_name}_{'_'.join(video_name_parts)}" if video_name_parts else ad_group_name
                    else:
                        # YT_で始まらない場合は従来の処理
                        project_name = parts[0] if parts else ''
                        video_name = '_'.join(parts[1:]) if len(parts) > 1 else ad_group_name
                    
                    disapproved_ads.append({
                        'ad_group_name': ad_group_name,
                        'project_name': project_name,
                        'video_name': video_name,
                        'account_id': account_id,
                        'status': approval_status,
                        'row_number': i  # 行番号（デバッグ用）
                    })
                    
                    logger.info(f"不承認広告検出: {ad_group_name} (行{i})")
            
            logger.info(f"不承認広告 {len(disapproved_ads)}件検出")
            return disapproved_ads
            
        except Exception as e:
            logger.error(f"データ取得エラー: {e}")
            return []
    
    def get_ad_by_name(self, ad_group_name: str) -> Optional[Dict[str, str]]:
        """
        広告グループ名で特定の広告情報を取得
        
        Args:
            ad_group_name: 広告グループ名
            
        Returns:
            広告情報、見つからない場合はNone
        """
        try:
            all_values = self.sheet.get_all_values()
            
            for i, row in enumerate(all_values[5:], start=6):
                if len(row) > 0 and str(row[0]).strip() == ad_group_name:
                    return {
                        'ad_group_name': ad_group_name,
                        'project_name': ad_group_name.split('_')[0],
                        'video_name': '_'.join(ad_group_name.split('_')[1:]),
                        'account_id': str(row[25]).strip().replace('-', '') if len(row) > 25 else '',
                        'status': str(row[27]).strip() if len(row) > 27 else '',
                        'row_number': i
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"広告検索エラー: {e}")
            return None


def main():
    """テスト実行"""
    import os
    from pathlib import Path
    
    # 認証ファイルパス設定
    project_root = Path(__file__).parent.parent
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(
        project_root / 'credentials' / 'google_service_account.json'
    )
    
    # リーダー初期化
    reader = ApprovalStatusReader()
    
    # 不承認広告を取得
    disapproved_ads = reader.get_disapproved_ads()
    
    print("\n=== 不承認広告一覧 ===")
    for ad in disapproved_ads:
        print(f"- {ad['ad_group_name']}")
        print(f"  案件: {ad['project_name']}")
        print(f"  動画: {ad['video_name']}")
        print(f"  アカウント: {ad['account_id']}")
        print()
    
    print(f"合計: {len(disapproved_ads)}件")


if __name__ == "__main__":
    main()