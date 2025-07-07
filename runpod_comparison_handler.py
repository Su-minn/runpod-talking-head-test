#!/usr/bin/env python3
"""
RunPod Serverless Handler: SadTalker vs Wav2Lip 비교 테스트
두 모델을 동시에 실행하고 결과를 비교합니다.
"""

import runpod
import os
import time
import subprocess
import requests
import json
import base64
from urllib.parse import urlparse
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(url, destination):
    """URL에서 파일 다운로드"""
    try:
        logger.info(f"Downloading file from {url} to {destination}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Successfully downloaded {len(response.content)} bytes")
        return destination
    except Exception as e:
        logger.error(f"Failed to download {url}: {str(e)}")
        raise

def run_sadtalker(image_path, audio_path, output_dir):
    """SadTalker 실행"""
    start_time = time.time()
    
    try:
        logger.info("Starting SadTalker processing...")
        
        # SadTalker 실행 명령어
        cmd = [
            "python", "/workspace/SadTalker/inference.py",
            "--driven_audio", audio_path,
            "--source_image", image_path,
            "--result_dir", output_dir,
            "--still", "--preprocess", "full",
            "--enhancer", "gfpgan"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/workspace/SadTalker")
        
        processing_time = time.time() - start_time
        
        if result.returncode != 0:
            logger.error(f"SadTalker failed: {result.stderr}")
            return None, processing_time, result.stderr
        
        # 결과 파일 찾기
        output_files = []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith(('.mp4', '.avi', '.mov')):
                    output_files.append(os.path.join(root, file))
        
        if not output_files:
            return None, processing_time, "No output video found"
        
        logger.info(f"SadTalker completed in {processing_time:.2f} seconds")
        return output_files[0], processing_time, None
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"SadTalker error: {str(e)}")
        return None, processing_time, str(e)

def run_wav2lip(image_path, audio_path, output_dir):
    """Wav2Lip 실행"""
    start_time = time.time()
    
    try:
        logger.info("Starting Wav2Lip processing...")
        
        # 출력 파일 경로
        output_path = os.path.join(output_dir, "wav2lip_result.mp4")
        os.makedirs(output_dir, exist_ok=True)
        
        # Wav2Lip 실행 명령어
        cmd = [
            "python", "/workspace/Wav2Lip/inference.py",
            "--checkpoint_path", "/workspace/Wav2Lip/checkpoints/wav2lip_gan.pth",
            "--face", image_path,
            "--audio", audio_path,
            "--outfile", output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/workspace/Wav2Lip")
        
        processing_time = time.time() - start_time
        
        if result.returncode != 0:
            logger.error(f"Wav2Lip failed: {result.stderr}")
            return None, processing_time, result.stderr
        
        if not os.path.exists(output_path):
            return None, processing_time, "No output video found"
        
        logger.info(f"Wav2Lip completed in {processing_time:.2f} seconds")
        return output_path, processing_time, None
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Wav2Lip error: {str(e)}")
        return None, processing_time, str(e)

def encode_video_to_base64(video_path):
    """비디오 파일을 base64로 인코딩"""
    try:
        with open(video_path, 'rb') as video_file:
            video_data = video_file.read()
            base64_data = base64.b64encode(video_data).decode('utf-8')
            return base64_data
    except Exception as e:
        logger.error(f"Failed to encode video: {str(e)}")
        return None

def get_file_size(file_path):
    """파일 크기 반환 (MB)"""
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    except:
        return 0

def handler(event):
    """
    RunPod handler function - SadTalker vs Wav2Lip 비교
    
    event['input'] = {
        'input_image_url': 'https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/profile.png',
        'input_audio_url': 'https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.wav',
        'return_videos': False  # True이면 base64로 비디오 반환, False이면 파일 정보만
    }
    """
    
    logger.info("Starting SadTalker vs Wav2Lip comparison...")
    overall_start_time = time.time()
    
    try:
        # 입력 받기
        input_data = event['input']
        image_url = input_data['input_image_url']
        audio_url = input_data['input_audio_url']
        return_videos = input_data.get('return_videos', False)
        
        # 작업 디렉토리 생성
        job_id = event.get('id', str(int(time.time())))
        work_dir = f"/tmp/{job_id}"
        os.makedirs(work_dir, exist_ok=True)
        
        # 입력 파일 다운로드
        image_path = os.path.join(work_dir, "input_image.png")
        audio_path = os.path.join(work_dir, "input_audio.wav")
        
        download_file(image_url, image_path)
        download_file(audio_url, audio_path)
        
        # 출력 디렉토리 생성
        sadtalker_output_dir = os.path.join(work_dir, "sadtalker_output")
        wav2lip_output_dir = os.path.join(work_dir, "wav2lip_output")
        
        # 두 모델 동시 실행 (순차적으로)
        logger.info("Running both models...")
        
        # SadTalker 실행
        sadtalker_video, sadtalker_time, sadtalker_error = run_sadtalker(
            image_path, audio_path, sadtalker_output_dir
        )
        
        # Wav2Lip 실행
        wav2lip_video, wav2lip_time, wav2lip_error = run_wav2lip(
            image_path, audio_path, wav2lip_output_dir
        )
        
        # 전체 처리 시간
        total_time = time.time() - overall_start_time
        
        # 결과 정리
        result = {
            "job_id": job_id,
            "total_processing_time": round(total_time, 2),
            "comparison": {
                "sadtalker": {
                    "processing_time": round(sadtalker_time, 2),
                    "success": sadtalker_video is not None,
                    "error": sadtalker_error,
                    "output_file_size_mb": get_file_size(sadtalker_video) if sadtalker_video else 0
                },
                "wav2lip": {
                    "processing_time": round(wav2lip_time, 2),
                    "success": wav2lip_video is not None,
                    "error": wav2lip_error,
                    "output_file_size_mb": get_file_size(wav2lip_video) if wav2lip_video else 0
                }
            },
            "analysis": {
                "faster_model": "sadtalker" if sadtalker_time < wav2lip_time else "wav2lip",
                "time_difference": abs(round(sadtalker_time - wav2lip_time, 2)),
                "both_succeeded": (sadtalker_video is not None) and (wav2lip_video is not None)
            }
        }
        
        # 비디오 파일 반환 (옵션)
        if return_videos:
            if sadtalker_video:
                result["comparison"]["sadtalker"]["video_base64"] = encode_video_to_base64(sadtalker_video)
            if wav2lip_video:
                result["comparison"]["wav2lip"]["video_base64"] = encode_video_to_base64(wav2lip_video)
        
        # 추가 메타데이터
        result["metadata"] = {
            "input_image_url": image_url,
            "input_audio_url": audio_url,
            "processing_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "python_version": subprocess.check_output(["python", "--version"]).decode().strip()
        }
        
        logger.info(f"Comparison completed in {total_time:.2f} seconds")
        return result
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return {
            "error": str(e),
            "job_id": event.get('id', 'unknown'),
            "processing_time": round(time.time() - overall_start_time, 2)
        }

# RunPod 서버리스 시작
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler}) 