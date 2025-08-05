#!/usr/bin/env python3
"""
自動バッチ処理版 - 動画を継続的に処理
設定ファイルやスプレッドシートから動画リストを読み込んで自動処理
"""
import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from video_merger_auto_bg import VideoMergerWithAutoBG

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchVideoProcessor:
    """バッチ処理で動画を自動合成"""
    
    def __init__(self, config_path: str = "batch_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.merger = VideoMergerWithAutoBG(
            replicate_api_token=os.environ.get('REPLICATE_API_TOKEN')
        )
        
        # 処理済みリストを管理
        self.processed_file = Path("processed_videos.json")
        self.processed_videos = self.load_processed_list()
        
    def load_config(self) -> Dict:
        """設定ファイルを読み込む"""
        default_config = {
            "input_folder": "batch_input",
            "output_folder": "batch_output",
            "watch_interval": 60,  # 60秒ごとにチェック
            "main_scale": 0.8,
            "disclaimer_text": "※結果には個人差があり成果を保証するものではありません",
            "auto_upload": False,  # 将来的にYouTube等への自動アップロード
            "spreadsheet_id": None  # Google Spreadsheetから読み込む場合
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        else:
            # デフォルト設定を保存
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
                
        return default_config
    
    def load_processed_list(self) -> List[str]:
        """処理済みファイルリストを読み込む"""
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_processed_list(self):
        """処理済みファイルリストを保存"""
        with open(self.processed_file, 'w') as f:
            json.dump(self.processed_videos, f, indent=2)
    
    def get_pending_videos(self) -> List[Path]:
        """未処理の動画ファイルを取得"""
        input_folder = Path(self.config['input_folder'])
        input_folder.mkdir(exist_ok=True)
        
        pending = []
        for video_file in input_folder.glob("*"):
            if video_file.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                if str(video_file) not in self.processed_videos:
                    pending.append(video_file)
                    
        return pending
    
    def process_video(self, video_path: Path) -> bool:
        """動画を処理"""
        try:
            logger.info(f"Processing: {video_path.name}")
            
            # 出力ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{video_path.stem}_merged_{timestamp}.mp4"
            output_path = Path(self.config['output_folder']) / output_name
            output_path.parent.mkdir(exist_ok=True)
            
            # 動画処理
            result = self.merger.process_with_auto_background(
                main_video=str(video_path),
                output_video=str(output_path),
                main_scale=self.config['main_scale'],
                disclaimer_text=self.config['disclaimer_text']
            )
            
            logger.info(f"Completed: {output_name}")
            logger.info(f"  Size: {result['output_size']}")
            logger.info(f"  Duration: {result['duration']:.1f}s")
            
            # 処理済みリストに追加
            self.processed_videos.append(str(video_path))
            self.save_processed_list()
            
            # 処理結果を記録
            self.log_result(video_path, output_path, result)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {video_path.name}: {e}", exc_info=True)
            return False
    
    def log_result(self, input_path: Path, output_path: Path, result: Dict):
        """処理結果をログファイルに記録"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "input_file": str(input_path),
            "output_file": str(output_path),
            "result": result
        }
        
        log_file = Path(self.config['output_folder']) / "processing_log.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def run_once(self) -> int:
        """一度だけ実行して未処理動画を処理"""
        pending_videos = self.get_pending_videos()
        
        if not pending_videos:
            logger.info("No pending videos found.")
            return 0
        
        logger.info(f"Found {len(pending_videos)} videos to process")
        processed_count = 0
        
        for video_path in pending_videos:
            if self.process_video(video_path):
                processed_count += 1
                # API制限を考慮して少し待機
                time.sleep(5)
                
        return processed_count
    
    def run_continuous(self):
        """継続的に監視して処理"""
        logger.info("Starting continuous batch processing...")
        logger.info(f"Watching folder: {self.config['input_folder']}")
        logger.info(f"Check interval: {self.config['watch_interval']}s")
        
        while True:
            try:
                processed = self.run_once()
                if processed > 0:
                    logger.info(f"Processed {processed} videos in this batch")
                    
                # 次のチェックまで待機
                time.sleep(self.config['watch_interval'])
                
            except KeyboardInterrupt:
                logger.info("Batch processing stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                time.sleep(60)  # エラー時は60秒待機


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='動画バッチ処理ツール')
    parser.add_argument('--once', action='store_true', 
                       help='一度だけ実行（監視モードではない）')
    parser.add_argument('--config', default='batch_config.json',
                       help='設定ファイルのパス')
    
    args = parser.parse_args()
    
    # 環境変数チェック
    if not os.environ.get('REPLICATE_API_TOKEN'):
        print("Error: REPLICATE_API_TOKEN is not set!")
        print("Please set it in .env.local or export it")
        exit(1)
    
    processor = BatchVideoProcessor(config_path=args.config)
    
    if args.once:
        # 一度だけ実行
        processed = processor.run_once()
        print(f"Processed {processed} videos")
    else:
        # 継続監視モード
        processor.run_continuous()