#!/usr/bin/env python3
"""
YouTubeチャンネル振り分け管理
案件種別（NB、SBC、OM）によって異なるチャンネルにアップロード
"""
import logging
from typing import Optional, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class ChannelManager:
    """YouTubeチャンネルの振り分け管理"""
    
    # 案件種別とチャンネルのマッピング
    CHANNEL_MAPPING = {
        'NB': 'nb_channel',
        'SBC': 'sbc_channel', 
        'OM': 'om_channel'
    }
    
    # 各チャンネルの認証トークン（1つのOAuth2アプリを共有）
    TOKEN_MAPPING = {
        'nb_channel': 'youtube_nb_token.pickle',
        'sbc_channel': 'youtube_sbc_token.pickle',
        'om_channel': 'youtube_om_token.pickle'
    }
    
    def __init__(self, credentials_dir: str = "credentials"):
        """
        初期化
        
        Args:
            credentials_dir: 認証ファイルのディレクトリ
        """
        self.credentials_dir = Path(credentials_dir)
        
    def parse_ad_name(self, ad_name: str) -> Tuple[Optional[str], str]:
        """
        広告名から案件種別とクリーンな広告名を取得
        
        Args:
            ad_name: 広告名（例: "SBC_変わらない勇気"）
            
        Returns:
            (案件種別, クリーンな広告名)のタプル
            例: ("SBC", "変わらない勇気")
        """
        # プレフィックスをチェック
        for prefix in self.CHANNEL_MAPPING.keys():
            if ad_name.startswith(f"{prefix}_"):
                clean_name = ad_name[len(prefix) + 1:]  # プレフィックスとアンダースコアを除去
                return prefix, clean_name
        
        # プレフィックスがない場合
        logger.warning(f"広告名にプレフィックスがありません: {ad_name}")
        return None, ad_name
    
    def get_channel_info(self, ad_name: str) -> Dict[str, any]:
        """
        広告名から適切なチャンネル情報を取得
        
        Args:
            ad_name: 広告名
            
        Returns:
            チャンネル情報の辞書
        """
        project_type, clean_name = self.parse_ad_name(ad_name)
        
        if not project_type:
            raise ValueError(f"広告名に有効なプレフィックスがありません: {ad_name}")
        
        channel_id = self.CHANNEL_MAPPING[project_type]
        token_file = self.TOKEN_MAPPING[channel_id]
        token_path = self.credentials_dir / token_file
        
        return {
            'project_type': project_type,
            'channel_id': channel_id,
            'token_path': token_path,
            'clean_ad_name': clean_name,
            'channel_name': self._get_channel_display_name(project_type)
        }
    
    def _get_channel_display_name(self, project_type: str) -> str:
        """チャンネルの表示名を取得"""
        display_names = {
            'NB': 'NBチャンネル',
            'SBC': 'SBCチャンネル',
            'OM': 'OMチャンネル'
        }
        return display_names.get(project_type, f'{project_type}チャンネル')
    
    def validate_tokens(self) -> Dict[str, bool]:
        """
        各チャンネルのトークンファイルの存在を確認
        
        Returns:
            チャンネルごとのトークン存在状況
        """
        status = {}
        for channel_id, token_file in self.TOKEN_MAPPING.items():
            token_path = self.credentials_dir / token_file
            status[channel_id] = token_path.exists()
            
            if not token_path.exists():
                logger.info(f"トークン未生成: {token_path}")
        
        return status
    
    def get_upload_title(self, ad_name: str, suffix: str = "") -> str:
        """
        アップロード用のタイトルを生成
        
        Args:
            ad_name: 広告名（プレフィックス付き）
            suffix: タイトルの接尾辞（デフォルトは空）
            
        Returns:
            YouTubeアップロード用のタイトル（プレフィックスなしの動画名のみ）
        """
        _, clean_name = self.parse_ad_name(ad_name)
        if suffix:
            return f"{clean_name} - {suffix}"
        return clean_name  # 動画名のみ返す


# テスト用
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = ChannelManager()
    
    # テストケース
    test_cases = [
        "SBC_変わらない勇気",
        "NB_春のキャンペーン",
        "OM_新商品PR",
        "間違った名前"  # プレフィックスなし
    ]
    
    for ad_name in test_cases:
        print(f"\n広告名: {ad_name}")
        try:
            info = manager.get_channel_info(ad_name)
            print(f"  案件種別: {info['project_type']}")
            print(f"  チャンネル: {info['channel_name']}")
            print(f"  クリーン名: {info['clean_ad_name']}")
            print(f"  アップロードタイトル: {manager.get_upload_title(ad_name)}")
        except ValueError as e:
            print(f"  エラー: {e}")
    
    # トークンファイルの確認
    print("\nトークン状況:")
    status = manager.validate_tokens()
    for channel, exists in status.items():
        print(f"  {channel}: {'✓ 認証済み' if exists else '✗ 未認証'}")