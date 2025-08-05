#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
from functools import wraps
import os
import uuid
import subprocess
import threading
from werkzeug.utils import secure_filename
from video_merger_auto_bg import VideoMergerWithAutoBG
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
CORS(app)

# Basic認証の設定
def check_auth(username, password):
    """Basic認証のユーザー名とパスワードをチェック"""
    return username == 'videomerger' and password == 'SecurePass2025!'

def authenticate():
    """認証が必要な場合のレスポンスを返す"""
    return Response(
        'ログインが必要です', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """Basic認証を要求するデコレータ"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# 設定
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 処理状況
processing_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video_auto(job_id, main_path, output_path, options):
    """バックグラウンドで動画処理（自動背景生成付き）"""
    try:
        app.logger.info(f"Starting process_video_auto for job {job_id}")
        app.logger.info(f"Main path: {main_path}, Output path: {output_path}")
        
        processing_status[job_id] = {
            'status': 'processing',
            'progress': 10,
            'message': 'メイン動画を分析中...'
        }
        
        # VideoMergerWithAutoBGを使用
        merger = VideoMergerWithAutoBG(
            replicate_api_token=os.environ.get('REPLICATE_API_TOKEN')
        )
        app.logger.info(f"VideoMergerWithAutoBG initialized")
        
        # メイン動画の情報取得
        app.logger.info(f"Getting video info for {main_path}")
        main_info = merger.get_video_info(main_path)
        orientation = main_info['orientation']
        app.logger.info(f"Video info: {main_info}")
        
        processing_status[job_id] = {
            'status': 'processing',
            'progress': 20,
            'message': f'{orientation}動画を検出。背景を生成中...',
            'video_info': {
                'orientation': orientation,
                'original_size': f"{main_info['width']}x{main_info['height']}",
                'duration': main_info['duration']
            }
        }
        
        # 背景生成＋合成処理（常に動物・自然のランダム背景）
        result = merger.process_with_auto_background(
            main_video=main_path,
            output_video=output_path,
            main_scale=options.get('main_scale', 0.8),
            disclaimer_text=options.get('disclaimer_text', '※結果には個人差があり成果を保証するものではありません')
        )
        
        processing_status[job_id] = {
            'status': 'completed',
            'progress': 100,
            'message': '処理が完了しました！',
            'output_file': os.path.basename(output_path),
            'video_info': {
                'orientation': result['orientation'],
                'output_size': result['output_size'],
                'duration': result['duration']
            }
        }
        
    except Exception as e:
        app.logger.error(f"Error in process_video_auto: {str(e)}", exc_info=True)
        processing_status[job_id] = {
            'status': 'error',
            'progress': 0,
            'message': f'エラー: {str(e)}'
        }
    finally:
        # アップロードファイルを削除
        if os.path.exists(main_path):
            os.remove(main_path)

@app.route('/api/health')
def health_check():
    """ヘルスチェック用エンドポイント（認証不要）"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/')
# @requires_auth  # ローカルテスト用に一時的に無効化
def index():
    return render_template('index_auto_simple.html')

@app.route('/api/merge', methods=['POST'])
# @requires_auth  # ローカルテスト用に一時的に無効化
def merge_videos():
    try:
        app.logger.debug(f"Request files: {request.files}")
        app.logger.debug(f"Request form: {request.form}")
        
        # ファイルチェック
        if 'main_video' not in request.files:
            app.logger.error("No main_video in request.files")
            return jsonify({'error': 'メイン動画が選択されていません'}), 400
        
        main_file = request.files['main_video']
        
        if main_file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        if not allowed_file(main_file.filename):
            return jsonify({'error': '対応していないファイル形式です'}), 400
        
        # ジョブID生成
        job_id = str(uuid.uuid4())
        
        # ファイル保存
        main_filename = f"{job_id}_main_{secure_filename(main_file.filename)}"
        output_filename = f"{job_id}_output.mp4"
        
        main_path = os.path.join(UPLOAD_FOLDER, main_filename)
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        main_file.save(main_path)
        
        # オプション取得
        options = {
            'bg_style': request.form.get('bg_style', 'abstract gradient'),
            'main_scale': float(request.form.get('main_scale', 0.8)),
            'disclaimer_text': request.form.get('disclaimer_text'),
            'use_replicate': request.form.get('use_replicate', 'true').lower() == 'true'
        }
        
        # バックグラウンド処理開始
        processing_status[job_id] = {
            'status': 'queued', 
            'progress': 0,
            'message': '処理を開始しています...'
        }
        thread = threading.Thread(
            target=process_video_auto,
            args=(job_id, main_path, output_path, options)
        )
        thread.start()
        
        return jsonify({
            'status': 'success',
            'job_id': job_id,
            'message': '処理を開始しました'
        })
        
    except Exception as e:
        app.logger.error(f"Error in merge_videos: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<job_id>')
# @requires_auth  # ローカルテスト用に一時的に無効化
def get_status(job_id):
    if job_id in processing_status:
        return jsonify(processing_status[job_id])
    else:
        return jsonify({'error': 'ジョブが見つかりません'}), 404

@app.route('/api/download/<filename>')
# @requires_auth  # ローカルテスト用に一時的に無効化
def download_file(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'ファイルが見つかりません'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config')
# @requires_auth  # ローカルテスト用に一時的に無効化
def get_config():
    """設定情報を取得"""
    return jsonify({
        'replicate_enabled': True,  # 常にReplicate APIを使用
        'auto_background': True,    # 背景は自動生成のみ
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size': MAX_FILE_SIZE
    })

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)