#!/usr/bin/env python3
"""
RunPod Serverless Handler: Wav2Lip
사용할 Docker 이미지: devxpy/cog-wav2lip 또는 rudrabha/wav2lip
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
    Wav2Lip RunPod handler
    Input:
    {
        'input_image_url': 'https://example.com/face.png',
        'input_audio_url': 'https://example.com/audio.wav',
        'options': {
            'quality': 'high',  # 'low', 'medium', 'high'
            'pad_top': 0,       # 상단 패딩
            'pad_bottom': 10,   # 하단 패딩
            'pad_left': 0,      # 좌측 패딩
            'pad_right': 0,     # 우측 패딩
            'resize_factor': 1, # 크기 조정 비율
            'nosmooth': False   # 부드러움 비활성화
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
        work_dir = f"/tmp/wav2lip_{job_id}"
        os.makedirs(work_dir, exist_ok=True)
        
        logger.info(f"Starting Wav2Lip job {job_id}")
        
        # 파일 다운로드
        image_path = download_file(image_url, f"{work_dir}/input_face.png")
        audio_path = download_file(audio_url, f"{work_dir}/input_audio.wav")
        
        # Wav2Lip 옵션 설정
        quality = options.get('quality', 'high')
        pad_top = options.get('pad_top', 0)
        pad_bottom = options.get('pad_bottom', 10)
        pad_left = options.get('pad_left', 0)
        pad_right = options.get('pad_right', 0)
        resize_factor = options.get('resize_factor', 1)
        nosmooth = options.get('nosmooth', False)
        
        # 출력 파일 경로
        output_path = f"{work_dir}/result.mp4"
        
        # Wav2Lip 모델 경로 설정
        checkpoint_path = "/workspace/Wav2Lip/checkpoints/wav2lip_gan.pth"
        if quality == 'high':
            checkpoint_path = "/workspace/Wav2Lip/checkpoints/wav2lip_gan.pth"
        else:
            checkpoint_path = "/workspace/Wav2Lip/checkpoints/wav2lip.pth"
        
        # Wav2Lip 실행 명령 구성
        cmd = [
            "python", "/workspace/Wav2Lip/inference.py",
            "--checkpoint_path", checkpoint_path,
            "--face", image_path,
            "--audio", audio_path,
            "--outfile", output_path,
            "--resize_factor", str(resize_factor),
            "--pad_top", str(pad_top),
            "--pad_bottom", str(pad_bottom),
            "--pad_left", str(pad_left),
            "--pad_right", str(pad_right)
        ]
        
        if nosmooth:
            cmd.append("--nosmooth")
        
        logger.info(f"Executing Wav2Lip: {' '.join(cmd)}")
        
        # Wav2Lip 실행
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=600  # 10분 타임아웃 (Wav2Lip이 더 빠름)
        )
        
        if result.returncode != 0:
            logger.error(f"Wav2Lip failed: {result.stderr}")
            raise Exception(f"Wav2Lip execution failed: {result.stderr}")
        
        # 결과 파일 확인
        if not os.path.exists(output_path):
            raise Exception("No output video generated")
        
        file_size = os.path.getsize(output_path)
        
        # 실제 환경에서는 S3나 다른 스토리지에 업로드
        # 여기서는 임시로 로컬 경로 반환
        output_url = f"file://{output_path}"
        
        processing_time = time.time() - start_time
        
        logger.info(f"Wav2Lip completed in {processing_time:.2f}s")
        
        return {
            "status": "success",
            "output_video_url": output_url,
            "processing_time": processing_time,
            "file_size": file_size,
            "model": "wav2lip",
            "options_used": options,
            "message": f"Wav2Lip processing completed successfully in {processing_time:.2f} seconds"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "Processing timeout (10 minutes)",
            "model": "wav2lip",
            "processing_time": time.time() - start_time
        }
    except Exception as e:
        logger.error(f"Error in Wav2Lip handler: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "model": "wav2lip",
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