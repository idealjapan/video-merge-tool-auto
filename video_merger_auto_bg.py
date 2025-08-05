#!/usr/bin/env python3
import subprocess
import sys
import os
import json
import time
import requests
import logging
from typing import Dict, Tuple, Optional
from background_prompts import BackgroundPromptGenerator
from config import Config

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoMergerWithAutoBG:
    """動画サイズ自動検出＆背景自動生成機能付き動画合成ツール"""
    
    def __init__(self, replicate_api_token=None):
        self.replicate_api_token = replicate_api_token or os.environ.get('REPLICATE_API_TOKEN')
        
    def get_video_info(self, video_path: str) -> Dict:
        """動画の情報（解像度、長さ、アスペクト比）を取得"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height:format=duration',
            '-of', 'json',
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            width = data['streams'][0]['width']
            height = data['streams'][0]['height']
            duration = float(data['format']['duration'])
            
            # 縦横判定
            orientation = 'vertical' if height > width else 'horizontal'
            aspect_ratio = f"{width}:{height}"
            
            return {
                'width': width,
                'height': height,
                'duration': duration,
                'orientation': orientation,
                'aspect_ratio': aspect_ratio
            }
        except Exception as e:
            print(f"Error getting video info: {e}")
            sys.exit(1)
    
    def determine_output_size(self, main_video_info: Dict) -> Tuple[int, int, str]:
        """メイン動画の向きから出力サイズを決定"""
        if main_video_info['orientation'] == 'vertical':
            # 縦動画 → 1080x1920
            return 1080, 1920, 'vertical'
        else:
            # 横動画 → 1920x1080
            return 1920, 1080, 'horizontal'
    
    def generate_background_with_replicate(self, 
                                         orientation: str, 
                                         duration: float,
                                         style: str = None) -> Optional[str]:
        """Replicate APIを使って背景動画を生成"""
        
        if not self.replicate_api_token:
            raise ValueError("Replicate APIトークンが設定されていません")
        
        try:
            # Replicate API呼び出し
            headers = {
                'Authorization': f'Token {self.replicate_api_token}',
                'Content-Type': 'application/json'
            }
            
            # プロンプト生成（styleが指定されない場合はランダム）
            if style:
                prompt = BackgroundPromptGenerator.get_themed_prompt(style, orientation)
            else:
                prompt = BackgroundPromptGenerator.generate_prompt(orientation)
            
            logger.info(f"生成プロンプト: {prompt}")
            
            # 解像度設定（アスペクト比を維持）
            if orientation == 'vertical':
                width, height = 480, 852  # 9:16 (480p)
            else:
                width, height = 852, 480  # 16:9 (480p)
            
            # Seedance-1-Lite を使用（テキストから動画生成）
            # 縦動画の場合はプロンプトに明示的に追加
            if orientation == 'vertical':
                prompt = f"VERTICAL FORMAT 9:16 PORTRAIT: {prompt}"
                logger.info(f"Vertical video - Using 9:16 aspect ratio")
            
            data = {
                "version": "b6519549e375404f45af5ef2e4b01f651d4014f3b57d3270b430e0523bad9835",  # seedance-1-lite
                "input": {
                    "prompt": prompt,
                    "duration": 5,  # 5秒動画
                    "resolution": "480p",  # 480p解像度（処理速度優先）
                    "aspect_ratio": "9:16" if orientation == 'vertical' else "16:9",  # アスペクト比
                    "camera_fixed": False  # カメラ動きあり
                }
            }
            
            response = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                prediction = response.json()
                prediction_id = prediction['id']
                
                # 生成完了まで待機
                logger.info("背景動画を生成中...")
                while True:
                    time.sleep(2)  # チェック間隔を短縮
                    status_response = requests.get(
                        f"https://api.replicate.com/v1/predictions/{prediction_id}",
                        headers=headers
                    )
                    status = status_response.json()
                    
                    if status['status'] == 'succeeded':
                        output = status['output']
                        # outputがリストの場合は最初の要素を取得
                        if isinstance(output, list):
                            video_url = output[0] if output else None
                        else:
                            video_url = output
                        
                        if not video_url:
                            logger.error("No video URL in output")
                            return None
                            
                        # ダウンロード
                        video_response = requests.get(video_url)
                        bg_path = f"temp_bg_{prediction_id}.mp4"
                        with open(bg_path, 'wb') as f:
                            f.write(video_response.content)
                        return bg_path
                    elif status['status'] == 'failed':
                        logger.error(f"背景生成に失敗しました: {status}")
                        return None
                    
                    logger.info(f"状態: {status['status']}...")
            else:
                logger.error(f"API呼び出しエラー: {response.status_code}")
                logger.error(f"レスポンス: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Replicate API エラー: {e}", exc_info=True)
            return None
    
    
    def merge_videos(self, main_video: str, background_video: str, 
                    output_video: str, main_scale: float = 0.8,
                    disclaimer_text: Optional[str] = None):
        """動画を合成"""
        
        # メイン動画の情報取得
        main_info = self.get_video_info(main_video)
        output_width, output_height, orientation = self.determine_output_size(main_info)
        
        print(f"検出された動画タイプ: {orientation}")
        print(f"出力サイズ: {output_width}x{output_height}")
        
        # フォントパス（環境に応じて調整）
        font_path = os.environ.get('FONT_PATH', '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc')
        # macOSで日本語フォントが見つからない場合の代替
        if not os.path.exists(font_path):
            # 代替フォントを試す
            alternative_fonts = [
                '/System/Library/Fonts/Hiragino Sans GB.ttc',
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/Helvetica.ttc',
                '/Library/Fonts/Arial Unicode.ttf'
            ]
            for alt_font in alternative_fonts:
                if os.path.exists(alt_font):
                    font_path = alt_font
                    logger.info(f"Using alternative font: {alt_font}")
                    break
        
        # フィルター構築
        filter_parts = []
        
        # 背景動画を出力サイズにスケール
        # 縦動画の場合は、背景が横向きの場合に90度回転させる
        if orientation == 'vertical':
            # 縦動画用：必要に応じて回転してからスケール
            filter_parts.append(
                f"[0:v]transpose=1,"  # 90度時計回りに回転
                f"scale={output_width}:{output_height}:"
                f"force_original_aspect_ratio=increase,"
                f"crop={output_width}:{output_height}[bg]"
            )
        else:
            filter_parts.append(
                f"[0:v]scale={output_width}:{output_height}:"
                f"force_original_aspect_ratio=increase,"
                f"crop={output_width}:{output_height}[bg]"
            )
        
        # メイン動画をスケール（出力サイズに対する割合）
        # 横動画の場合は1920、縦動画の場合は1080を基準に
        if orientation == 'horizontal':
            # 横動画: 1920x1080に対する割合
            target_width = int(1920 * main_scale)
            target_height = int(1080 * main_scale)
        else:
            # 縦動画: 1080x1920に対する割合
            target_width = int(1080 * main_scale)
            target_height = int(1920 * main_scale)
        
        logger.info(f"Main video scale: {main_scale} ({main_scale*100}%)")
        logger.info(f"Target size: {target_width}x{target_height}")
        
        filter_parts.append(
            f"[1:v]scale={target_width}:{target_height}:"
            f"force_original_aspect_ratio=decrease[scaled]"
        )
        
        # 合成
        filter_parts.append("[bg][scaled]overlay=(W-w)/2:(H-h)/2[composite]")
        
        # 注意書き追加（オプション）
        if disclaimer_text:
            font_size = 32 if orientation == 'horizontal' else 28
            
            # OS別のフォントパスを取得
            japanese_fonts = Config.get_font_paths()
            
            font_file = None
            for font in japanese_fonts:
                if os.path.exists(font):
                    font_file = font
                    logger.info(f"Using font: {font}")
                    break
            
            if font_file:
                # フォントファイルを使用
                filter_parts.append(
                    f"[composite]drawtext="
                    f"fontfile='{font_file}':"
                    f"text='{disclaimer_text}':"
                    f"fontsize={font_size}:"
                    f"fontcolor=white:"
                    f"x=(w-text_w)/2:"
                    f"y=20:"
                    f"box=1:"
                    f"boxcolor=gray@0.7:"
                    f"boxborderw=15[v]"
                )
            else:
                # フォントファイルがない場合はfont名で指定
                filter_parts.append(
                    f"[composite]drawtext="
                    f"font='Hiragino Sans':"
                    f"text='{disclaimer_text}':"
                    f"fontsize={font_size}:"
                    f"fontcolor=white:"
                    f"x=(w-text_w)/2:"
                    f"y=20:"
                    f"box=1:"
                    f"boxcolor=gray@0.7:"
                    f"boxborderw=15[v]"
                )
            
            final_output = "[v]"
        else:
            final_output = "[composite]"
        
        filter_complex = ";".join(filter_parts)
        
        # デバッグ用：フィルターをログ出力
        logger.info(f"Filter complex: {filter_complex}")
        
        # FFmpegコマンド実行
        cmd = [
            'ffmpeg',
            '-stream_loop', '-1',
            '-i', background_video,
            '-i', main_video,
            '-filter_complex', filter_complex,
            '-map', final_output,
            '-map', '1:a?',
            '-t', str(main_info['duration']),
            '-c:v', 'libx264',
            '-preset', 'faster',  # 高速化のためfasterに変更
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            output_video
        ]
        
        print("動画を合成中...")
        subprocess.run(cmd, check=True)
        print(f"合成完了: {output_video}")
        
        return {
            'output_path': output_video,
            'output_size': f"{output_width}x{output_height}",
            'orientation': orientation,
            'duration': main_info['duration']
        }
    
    def process_with_auto_background(self, main_video: str, output_video: str,
                                   main_scale: float = 0.8,
                                   disclaimer_text: Optional[str] = None):
        """メイン処理：背景自動生成＋合成"""
        
        # メイン動画の情報取得
        main_info = self.get_video_info(main_video)
        output_width, output_height, orientation = self.determine_output_size(main_info)
        
        # 背景動画の生成（Replicate API必須）
        if not self.replicate_api_token:
            raise ValueError("Replicate APIトークンが必須です")
        
        bg_video = self.generate_background_with_replicate(
            orientation, 
            main_info['duration'],
            None  # 常にランダムな動物・自然背景
        )
        
        if not bg_video:
            raise RuntimeError("背景動画の生成に失敗しました")
        
        try:
            # 動画合成
            result = self.merge_videos(
                main_video, 
                bg_video, 
                output_video,
                main_scale,
                disclaimer_text
            )
            
            return result
            
        finally:
            # 一時ファイル削除
            if os.path.exists(bg_video) and bg_video.startswith(('temp_', 'default_')):
                os.remove(bg_video)


# CLI使用例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='自動背景生成付き動画合成ツール')
    parser.add_argument('main_video', help='メイン動画ファイル')
    parser.add_argument('output_video', help='出力動画ファイル')
    # 背景は常に動物・自然のランダム生成
    parser.add_argument('--main-scale', type=float, default=0.8,
                       help='メイン動画のスケール（0.1-1.0）')
    parser.add_argument('--text', help='注意書きテキスト')
    # Replicate APIは常に使用
    
    args = parser.parse_args()
    
    # 処理実行
    merger = VideoMergerWithAutoBG()
    result = merger.process_with_auto_background(
        args.main_video,
        args.output_video,
        main_scale=args.main_scale,
        disclaimer_text=args.text
    )
    
    print(f"\n完了！")
    print(f"出力: {result['output_path']}")
    print(f"サイズ: {result['output_size']} ({result['orientation']})")
    print(f"長さ: {result['duration']:.1f}秒")