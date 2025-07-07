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
    Wav2Lip RunPod handler function
    
    Input format:
    {
        'input_image_url': 'https://example.com/face.png',
        'input_audio_url': 'https://example.com/audio.wav'
    }
    
    Output format:
    {
        'output_video_url': 'file:///tmp/output.mp4',
        'processing_time': 45.2,
        'model': 'wav2lip',
        'success': true
    }
    """
    start_time = time.time()
    
    try:
        print("=== Wav2Lip Processing Started ===")
        
        # 입력 받기
        input_data = event['input']
        image_url = input_data['input_image_url']
        audio_url = input_data['input_audio_url']
        
        print(f"Image URL: {image_url}")
        print(f"Audio URL: {audio_url}")
        
        # 작업 디렉토리 생성
        job_id = event.get('id', str(int(time.time())))
        work_dir = f"/tmp/wav2lip_{job_id}"
        os.makedirs(work_dir, exist_ok=True)
        
        print(f"Work directory: {work_dir}")
        
        # 파일 다운로드
        image_path = download_file(image_url, f"{work_dir}/input_image.png")
        audio_path = download_file(audio_url, f"{work_dir}/input_audio.wav")
        
        # 출력 경로
        output_path = f"{work_dir}/output.mp4"
        
        # Wav2Lip 실행 명령어
        cmd = [
            "python", "/workspace/Wav2Lip/inference.py",
            "--checkpoint_path", "/workspace/Wav2Lip/checkpoints/wav2lip_gan.pth",
            "--face", image_path,
            "--audio", audio_path,
            "--outfile", output_path,
            "--resize_factor", "1",  # 품질 유지
            "--pad_top", "0",
            "--pad_bottom", "10",
            "--pad_left", "0", 
            "--pad_right", "0",
            "--nosmooth"  # 더 빠른 처리
        ]
        
        print(f"Running Wav2Lip command:")
        print(f"  {' '.join(cmd)}")
        
        # Wav2Lip 실행
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/workspace/Wav2Lip",
            timeout=600  # 10분 타임아웃
        )
        
        print(f"Wav2Lip stdout: {process.stdout}")
        if process.stderr:
            print(f"Wav2Lip stderr: {process.stderr}")
        
        if process.returncode != 0:
            raise Exception(f"Wav2Lip failed with return code {process.returncode}: {process.stderr}")
        
        # 출력 파일 확인
        if not os.path.exists(output_path):
            raise Exception(f"Output file not generated: {output_path}")
        
        # 최종 출력 경로로 복사
        final_output = f"/tmp/wav2lip_output_{job_id}.mp4"
        shutil.copy2(output_path, final_output)
        
        processing_time = time.time() - start_time
        
        print(f"=== Wav2Lip Processing Completed ===")
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"Output file: {final_output}")
        
        # 작업 디렉토리 정리 (선택적)
        # shutil.rmtree(work_dir)
        
        return {
            "output_video_url": f"file://{final_output}",
            "processing_time": processing_time,
            "model": "wav2lip",
            "success": True,
            "job_id": job_id,
            "output_file_size": os.path.getsize(final_output)
        }
        
    except subprocess.TimeoutExpired:
        error_msg = "Wav2Lip processing timed out (10 minutes)"
        print(f"ERROR: {error_msg}")
        return {
            "error": error_msg,
            "model": "wav2lip",
            "success": False,
            "processing_time": time.time() - start_time
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}")
        return {
            "error": error_msg,
            "model": "wav2lip",
            "success": False,
            "processing_time": time.time() - start_time
        }

# RunPod Serverless 시작
runpod.serverless.start({"handler": handler}) 