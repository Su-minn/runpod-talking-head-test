#!/usr/bin/env python3
"""
RunPod Serverless Handler: SadTalker
사용할 Docker 이미지: vinthony/sadtalker
"""

import runpod
import os
import time
import subprocess
import requests
import json
import logging
from urllib.parse import urlparse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(url, destination):
    """URL에서 파일 다운로드"""
    try:
        logger.info(f"Downloading from {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Downloaded {len(response.content)} bytes to {destination}")
        return destination
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise

def handler(event):
    """
    SadTalker RunPod handler
    Input:
    {
        'input_image_url': 'https://example.com/face.png',
        'input_audio_url': 'https://example.com/audio.mp3',
        'options': {
            'still_mode': True,  # 정적 모드 (빠름)
            'preprocess': 'crop',  # 전처리 방식
            'enhancer': 'gfpgan',  # 얼굴 향상
            'pose_style': 0,  # 포즈 스타일 (0-45)
            'face_model_resolution': 256  # 얼굴 모델 해상도
        }
    }
    """
    start_time = time.time()
    
    try:
        # 입력 파라미터 받기
        input_data = event.get('input', {})
        image_url = input_data.get('input_image_url')
        audio_url = input_data.get('input_audio_url')
        options = input_data.get('options', {})
        
        if not image_url or not audio_url:
            raise ValueError("input_image_url and input_audio_url are required")
        
        # 작업 디렉토리 생성
        job_id = event.get('id', str(int(time.time())))
        work_dir = f"/tmp/sadtalker_{job_id}"
        os.makedirs(work_dir, exist_ok=True)
        
        logger.info(f"Starting SadTalker job {job_id}")
        
        # 파일 다운로드
        image_path = download_file(image_url, f"{work_dir}/input_image.png")
        audio_path = download_file(audio_url, f"{work_dir}/input_audio.wav")
        
        # SadTalker 옵션 설정
        still_mode = options.get('still_mode', True)
        preprocess = options.get('preprocess', 'crop')
        enhancer = options.get('enhancer', 'gfpgan')
        pose_style = options.get('pose_style', 0)
        resolution = options.get('face_model_resolution', 256)
        
        # 출력 디렉토리
        output_dir = f"{work_dir}/results"
        os.makedirs(output_dir, exist_ok=True)
        
        # SadTalker 실행 명령 구성
        cmd = [
            "python", "/workspace/SadTalker/inference.py",
            "--driven_audio", audio_path,
            "--source_image", image_path,
            "--result_dir", output_dir,
            "--size", str(resolution),
            "--pose_style", str(pose_style)
        ]
        
        if still_mode:
            cmd.append("--still")
        
        if preprocess:
            cmd.extend(["--preprocess", preprocess])
        
        if enhancer:
            cmd.extend(["--enhancer", enhancer])
        
        logger.info(f"Executing SadTalker: {' '.join(cmd)}")
        
        # SadTalker 실행
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=1200  # 20분 타임아웃
        )
        
        if result.returncode != 0:
            logger.error(f"SadTalker failed: {result.stderr}")
            raise Exception(f"SadTalker execution failed: {result.stderr}")
        
        # 결과 파일 찾기
        output_files = []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.mp4'):
                    output_files.append(os.path.join(root, file))
        
        if not output_files:
            raise Exception("No output video generated")
        
        output_video = output_files[0]
        file_size = os.path.getsize(output_video)
        
        # 실제 환경에서는 S3나 다른 스토리지에 업로드
        # 여기서는 임시로 로컬 경로 반환
        output_url = f"file://{output_video}"
        
        processing_time = time.time() - start_time
        
        logger.info(f"SadTalker completed in {processing_time:.2f}s")
        
        return {
            "status": "success",
            "output_video_url": output_url,
            "processing_time": processing_time,
            "file_size": file_size,
            "model": "sadtalker",
            "options_used": options,
            "message": f"SadTalker processing completed successfully in {processing_time:.2f} seconds"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "Processing timeout (20 minutes)",
            "model": "sadtalker",
            "processing_time": time.time() - start_time
        }
    except Exception as e:
        logger.error(f"Error in SadTalker handler: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "model": "sadtalker",
            "processing_time": time.time() - start_time
        }
    finally:
        # 임시 파일 정리 (선택사항)
        try:
            import shutil
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)
        except:
            pass

# RunPod 시작
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler}) 