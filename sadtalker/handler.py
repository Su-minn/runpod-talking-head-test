import runpod
import os
import time
import subprocess
import requests
import tempfile
import shutil
import json
from urllib.parse import urlparse

def download_file(url, destination):
    """URL에서 파일 다운로드"""
    try:
        print(f"Downloading from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded to {destination} ({len(response.content)} bytes)")
        return destination
    except Exception as e:
        print(f"Download failed: {str(e)}")
        raise

def handler(event):
    """
    SadTalker RunPod handler function
    
    Input format:
    {
        'input_image_url': 'https://example.com/face.png',
        'input_audio_url': 'https://example.com/audio.wav'
    }
    
    Output format:
    {
        'output_video_url': 'file:///tmp/output.mp4',
        'processing_time': 120.5,
        'model': 'sadtalker',
        'success': true
    }
    """
    start_time = time.time()
    
    try:
        print("=== SadTalker Processing Started ===")
        
        # 입력 받기
        input_data = event['input']
        image_url = input_data['input_image_url']
        audio_url = input_data['input_audio_url']
        
        print(f"Image URL: {image_url}")
        print(f"Audio URL: {audio_url}")
        
        # 작업 디렉토리 생성
        job_id = event.get('id', str(int(time.time())))
        work_dir = f"/tmp/sadtalker_{job_id}"
        os.makedirs(work_dir, exist_ok=True)
        
        print(f"Work directory: {work_dir}")
        
        # 파일 다운로드
        image_path = download_file(image_url, f"{work_dir}/input_image.png")
        audio_path = download_file(audio_url, f"{work_dir}/input_audio.wav")
        
        # 결과 디렉토리
        result_dir = f"{work_dir}/results"
        os.makedirs(result_dir, exist_ok=True)
        
        # SadTalker 실행 명령어
        cmd = [
            "python", "/workspace/SadTalker/inference.py",
            "--driven_audio", audio_path,
            "--source_image", image_path,
            "--result_dir", result_dir,
            "--still",  # 정적 모드 (더 빠름)
            "--preprocess", "crop",  # 얼굴 크롭
            "--enhancer", "gfpgan",  # 품질 향상
            "--cpu"  # CPU 모드 (GPU 메모리 절약용, 필요시 제거)
        ]
        
        print(f"Running SadTalker command:")
        print(f"  {' '.join(cmd)}")
        
        # SadTalker 실행
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            cwd="/workspace/SadTalker",
            timeout=1800  # 30분 타임아웃
        )
        
        print(f"SadTalker stdout: {process.stdout}")
        if process.stderr:
            print(f"SadTalker stderr: {process.stderr}")
        
        if process.returncode != 0:
            raise Exception(f"SadTalker failed with return code {process.returncode}: {process.stderr}")
        
        # 결과 파일 찾기
        output_files = []
        for root, dirs, files in os.walk(result_dir):
            for file in files:
                if file.endswith('.mp4'):
                    output_files.append(os.path.join(root, file))
        
        if not output_files:
            raise Exception("No output video generated")
        
        # 가장 최근 생성된 파일 선택
        actual_output = max(output_files, key=os.path.getctime)
        
        # 최종 출력 경로로 복사
        final_output = f"/tmp/sadtalker_output_{job_id}.mp4"
        shutil.copy2(actual_output, final_output)
        
        processing_time = time.time() - start_time
        
        print(f"=== SadTalker Processing Completed ===")
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"Output file: {final_output}")
        
        # 작업 디렉토리 정리 (선택적)
        # shutil.rmtree(work_dir)
        
        return {
            "output_video_url": f"file://{final_output}",
            "processing_time": processing_time,
            "model": "sadtalker",
            "success": True,
            "job_id": job_id,
            "output_file_size": os.path.getsize(final_output)
        }
        
    except subprocess.TimeoutExpired:
        error_msg = "SadTalker processing timed out (30 minutes)"
        print(f"ERROR: {error_msg}")
        return {
            "error": error_msg,
            "model": "sadtalker",
            "success": False,
            "processing_time": time.time() - start_time
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}")
        return {
            "error": error_msg,
            "model": "sadtalker", 
            "success": False,
            "processing_time": time.time() - start_time
        }

# RunPod Serverless 시작
runpod.serverless.start({"handler": handler}) 