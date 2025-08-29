"""
Google Driveから広告名で動画を検索・ダウンロード
"""
import os
import io
import logging
import tempfile
from pathlib import Path
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

logger = logging.getLogger(__name__)


class GoogleDriveFinder:
    """Google Driveから動画を検索・取得"""
    
    # 案件別のGoogle DriveフォルダID（_CRフォルダ）
    PROJECT_FOLDERS = {
        'NB': '19_CXgsduFUUjp8a4oc0A6V-F3CdfnwEY',  # NB_CRフォルダ
        'OM': '1SdeTusi1KwzF9TDK5wpT-dQt-H0E5F4k',  # OM_CRフォルダ
        'SBC': '1NXeyriGAJyYihRCQl1tFB7JHz2CeNRFP'  # SBC_CRフォルダ
    }
    
    def __init__(self, credentials_file: str = None, folder_id: str = None):
        """
        Args:
            credentials_file: サービスアカウントのJSONファイル
            folder_id: 検索対象のフォルダID（省略可能）
        """
        if credentials_file is None:
            credentials_file = str(Path(__file__).parent.parent / "credentials" / "google_service_account.json")
        
        # デフォルトのフォルダIDを設定（後方互換性のため）
        if folder_id is None:
            folder_id = "1GQSw_hQEsTCKAjtt9FyVmZryVUXsbyLL"
        
        self.folder_id = folder_id  # 特定フォルダに限定する場合
        self.service = self._init_service(credentials_file)
        self.temp_dir = Path(tempfile.gettempdir()) / "ad_videos_temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    def _init_service(self, credentials_file: str):
        """Google Drive APIサービスを初期化"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive API初期化成功")
            return service
        except Exception as e:
            logger.error(f"Google Drive API初期化エラー: {e}")
            raise
    
    def parse_ad_group_name(self, ad_group_name: str) -> dict:
        """
        広告グループ名を解析して案件名と動画名を抽出（改善版）
        
        正しい形式:
        YT_OM_売れっ子イラストレーター_撮影06_お家で趣味のイラストをお仕事にする_MCC02運用46_03_01
        → 動画名: 売れっ子イラストレーター_撮影06_お家で趣味のイラストをお仕事にする
        
        MCCつけ忘れの形式:
        YT_NB_老後は考えるな_撮影01_老後のことひとりで考えていませんか？_AIツール素材をフリー素材に_01_01
        → 動画名: 老後は考えるな_撮影01_老後のことひとりで考えていませんか？_AIツール素材をフリー素材に
        """
        import re
        
        parts = ad_group_name.split('_')
        
        # パーツが少なすぎる場合や、YTで始まらない場合
        if len(parts) < 2:
            # 完全に異なる形式
            return {
                'project': '',
                'video_name': ad_group_name,
                'has_mcc': False
            }
        
        if parts[0] != 'YT':
            # 旧形式の場合のフォールバック（YTで始まらない）
            return {
                'project': parts[0] if parts else '',
                'video_name': '_'.join(parts[1:]) if len(parts) > 1 else '',
                'has_mcc': False
            }
        
        # YT_のみの場合
        if len(parts) < 3:
            return {
                'project': parts[1] if len(parts) > 1 else '',
                'video_name': '',
                'has_mcc': False
            }
        
        # YT_案件名_以降を解析
        project = parts[1]  # NB, OM, SBC, RL
        
        # MCCが含まれているか確認
        has_mcc = any('MCC' in part for part in parts)
        
        # 末尾の数字パターンを検出（_数字_数字 または _数字_数字_数字）
        trailing_number_pattern = re.compile(r'^\d+$')
        
        # 後ろから数字だけの部分を特定
        trailing_numbers = []
        for i in range(len(parts) - 1, 1, -1):  # YTと案件名は除外
            if trailing_number_pattern.match(parts[i]):
                trailing_numbers.insert(0, parts[i])
            else:
                break
        
        # MCCまたは末尾の数字の前までを動画名として扱う
        video_name_parts = []
        
        for i, part in enumerate(parts[2:], 2):  # YTと案件名の後から
            # MCC部分に到達したら終了
            if 'MCC' in part:
                break
            # 末尾の数字部分に到達したら終了
            if trailing_numbers and i >= len(parts) - len(trailing_numbers):
                break
            
            video_name_parts.append(part)
        
        video_name = '_'.join(video_name_parts)
        
        return {
            'project': project,
            'video_name': video_name,
            'has_mcc': has_mcc
        }
    
    def find_video_by_ad_group(self, ad_group_name: str) -> Optional[Path]:
        """
        広告グループ名から案件を特定し、適切なフォルダから動画を検索
        
        Args:
            ad_group_name: 広告グループ名
            
        Returns:
            ダウンロードした動画ファイルのパス
        """
        # 広告グループ名を解析
        parsed = self.parse_ad_group_name(ad_group_name)
        project = parsed['project']
        video_name = parsed['video_name']
        has_mcc = parsed.get('has_mcc', True)
        
        logger.info(f"案件: {project}, 動画名: {video_name}")
        if not has_mcc:
            logger.warning(f"⚠️ MCC記載が欠けている可能性があります: {ad_group_name}")
        
        # 案件フォルダIDを取得
        folder_id = self.PROJECT_FOLDERS.get(project)
        if not folder_id:
            logger.error(f"案件 {project} のフォルダIDが設定されていません")
            # フォールバック：デフォルトフォルダで検索
            return self.find_and_download(video_name)
        
        # 案件フォルダ内で動画を検索
        return self.find_in_project_folder(folder_id, project, video_name)
    
    def find_in_project_folder(self, folder_id: str, project: str, video_name: str) -> Optional[Path]:
        """
        特定の案件フォルダから動画を検索してダウンロード
        """
        try:
            import unicodedata
            
            # Unicode正規化を適用（NFD形式）- Google Driveのファイル名形式に合わせる
            search_patterns = [
                unicodedata.normalize('NFD', video_name + '.mp4'),  # NFD形式で完全一致
                unicodedata.normalize('NFD', video_name),  # 拡張子なし
                video_name + '.mp4',  # 元の形式でも試す
                video_name,
            ]
            
            for pattern in search_patterns:
                logger.info(f"{project}フォルダで検索: {pattern}")
                
                # 完全一致検索を優先
                query = f"'{folder_id}' in parents and name = '{pattern}'"
                logger.info(f"クエリ: {query}")
                
                # supportsAllDrivesとincludeItemsFromAllDrivesを追加
                results = self.service.files().list(
                    q=query,
                    fields="files(id, name, mimeType)",
                    pageSize=20,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                
                files = results.get('files', [])
                logger.info(f"検索結果: {len(files)}個のファイル")
                
                # 動画ファイルのみをフィルタ
                video_files = [
                    f for f in files 
                    if 'video' in f.get('mimeType', '').lower() 
                    or any(ext in f['name'].lower() for ext in ['.mp4', '.mov', '.avi', '.mkv'])
                ]
                
                if video_files:
                    # 最も一致度の高いファイルを選択
                    best_match = self._find_best_match(video_files, video_name)
                    if best_match:
                        logger.info(f"動画ファイル発見: {best_match['name']}")
                        return self._download_file(best_match['id'], best_match['name'], video_name)
            
            logger.warning(f"動画が見つかりません: {video_name}")
            self._list_folder_contents(folder_id, project)
            return None
            
        except Exception as e:
            logger.error(f"検索エラー: {e}")
            return None
    
    def _find_best_match(self, files: list, target_name: str) -> Optional[dict]:
        """最も一致度の高いファイルを選択"""
        if not files:
            return None
        
        # ファイル名から拡張子を除去して比較
        from pathlib import Path
        
        # 完全一致を最優先
        for file in files:
            file_stem = Path(file['name']).stem
            # 完全一致チェック（スペースとアンダースコアの違いは許容）
            if file_stem == target_name:
                logger.info(f"完全一致: {file['name']}")
                return file
            if file_stem.replace(' ', '_') == target_name:
                logger.info(f"完全一致（スペース→アンダースコア）: {file['name']}")
                return file
            if file_stem.replace('_', ' ') == target_name:
                logger.info(f"完全一致（アンダースコア→スペース）: {file['name']}")
                return file
        
        # 完全一致がない場合はNone（曖昧な一致は使わない）
        logger.warning(f"完全一致するファイルが見つかりません: {target_name}")
        logger.warning(f"候補ファイル:")
        for file in files[:5]:  # 最初の5個だけ表示
            logger.warning(f"  - {file['name']}")
        
        return None
    
    def _list_folder_contents(self, folder_id: str, project: str):
        """フォルダ内のファイル一覧を表示（デバッグ用）"""
        try:
            query = f"'{folder_id}' in parents"
            results = self.service.files().list(
                q=query,
                fields="files(name, mimeType)",
                pageSize=30,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"\n{project}フォルダ内の動画ファイル:")
            for file in files:
                if 'video' in file.get('mimeType', '') or any(ext in file['name'].lower() for ext in ['.mp4', '.mov', '.avi']):
                    logger.info(f"  - {file['name']}")
        except Exception as e:
            logger.error(f"フォルダ内容取得エラー: {e}")
    
    def find_and_download(self, ad_name: str) -> Optional[Path]:
        """
        広告名で動画を検索してダウンロード（後方互換性のため維持）
        
        Args:
            ad_name: 広告名
            
        Returns:
            Path: ダウンロードした動画ファイルのパス
        """
        try:
            # 1. ファイルを検索
            query_parts = [
                f"name contains '{ad_name}'",
                "mimeType contains 'video/'"
            ]
            
            if self.folder_id:
                query_parts.append(f"'{self.folder_id}' in parents")
            
            query = " and ".join(query_parts)
            
            logger.info(f"Google Driveで検索: {ad_name}")
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)",
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                logger.warning(f"動画が見つかりません: {ad_name}")
                return None
            
            # 最初に見つかったファイルを使用
            file_info = files[0]
            logger.info(f"動画ファイル発見: {file_info['name']}")
            
            # 2. ファイルをダウンロード
            return self._download_file(file_info['id'], file_info['name'], ad_name)
            
        except Exception as e:
            logger.error(f"検索・ダウンロードエラー: {e}")
            return None
    
    def _download_file(self, file_id: str, file_name: str, ad_name: str) -> Optional[Path]:
        """
        ファイルIDから動画をダウンロード
        
        Args:
            file_id: Google DriveのファイルID
            file_name: オリジナルのファイル名
            ad_name: 広告名
            
        Returns:
            Path: ダウンロードしたファイルのパス
        """
        try:
            # 拡張子を取得
            ext = Path(file_name).suffix or '.mp4'
            output_path = self.temp_dir / f"{ad_name}{ext}"
            
            # ダウンロード実行
            request = self.service.files().get_media(fileId=file_id)
            
            with open(output_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        if progress % 20 == 0:
                            logger.info(f"ダウンロード進捗: {progress}%")
            
            logger.info(f"ダウンロード完了: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"ダウンロードエラー: {e}")
            return None
    
    def list_videos(self, limit: int = 100):
        """
        利用可能な動画一覧を取得
        
        Args:
            limit: 取得する最大数
            
        Returns:
            list: 動画ファイルのリスト
        """
        try:
            query_parts = ["mimeType contains 'video/'"]
            
            if self.folder_id:
                query_parts.append(f"'{self.folder_id}' in parents")
            
            query = " and ".join(query_parts)
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, size)",
                pageSize=limit
            ).execute()
            
            files = results.get('files', [])
            
            video_list = []
            for file in files:
                video_list.append({
                    'id': file['id'],
                    'name': file['name'],
                    'size_mb': int(file.get('size', 0)) / (1024 * 1024)
                })
            
            return video_list
            
        except Exception as e:
            logger.error(f"リスト取得エラー: {e}")
            return []


# 使用例
if __name__ == "__main__":
    finder = GoogleDriveFinder()
    
    # 動画を検索してダウンロード
    video_path = finder.find_and_download("広告A")
    if video_path:
        print(f"Downloaded: {video_path}")
    
    # 動画一覧
    videos = finder.list_videos()
    for v in videos:
        print(f"{v['name']}: {v['size_mb']:.1f}MB")