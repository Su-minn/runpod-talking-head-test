#!/usr/bin/env python3
"""
RunPod Serverless SadTalker vs Wav2Lip 비교 테스트
"""

import requests
import json
import time
import os
from typing import Dict, Any

# RunPod API 설정 (환경변수에서 읽기)
RUNPOD_API_KEY = os.getenv('RUNPOD_API_KEY')
RUNPOD_ENDPOINT_ID = os.getenv('RUNPOD_ENDPOINT_ID')

# GitHub Raw URLs (환경변수 또는 기본값)
GITHUB_IMAGE_URL = os.getenv('GITHUB_IMAGE_URL', "https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/profile.png")
GITHUB_AUDIO_WAV_URL = os.getenv('GITHUB_AUDIO_WAV_URL', "https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.wav")
GITHUB_AUDIO_MP3_URL = os.getenv('GITHUB_AUDIO_MP3_URL', "https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.mp3")

def call_runpod_api(endpoint_id: str, api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """RunPod Serverless API 호출"""
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Calling RunPod API...")
    print(f"📍 Endpoint: {endpoint_id}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=900)  # 15분 타임아웃
        response.raise_for_status()
        
        elapsed_time = time.time() - start_time
        result = response.json()
        
        print(f"✅ API call completed in {elapsed_time:.2f} seconds")
        return result
        
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (15 minutes)")
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {str(e)}")
        return {"error": str(e)}

def run_comparison_test(audio_format: str = "wav") -> Dict[str, Any]:
    """비교 테스트 실행"""
    
    # 사용할 오디오 URL 선택
    audio_url = GITHUB_AUDIO_WAV_URL if audio_format == "wav" else GITHUB_AUDIO_MP3_URL
    
    payload = {
        "input": {
            "input_image_url": GITHUB_IMAGE_URL,
            "input_audio_url": audio_url,
            "return_videos": False  # 비디오 파일은 너무 크므로 False로 설정
        }
    }
    
    print(f"\n🎯 Starting comparison test with {audio_format.upper()} audio...")
    print(f"🖼️  Image: {GITHUB_IMAGE_URL}")
    print(f"🎵 Audio: {audio_url}")
    
    result = call_runpod_api(RUNPOD_ENDPOINT_ID, RUNPOD_API_KEY, payload)
    return result

def analyze_results(result: Dict[str, Any]) -> None:
    """결과 분석 및 출력"""
    
    print("\n" + "="*80)
    print("📊 COMPARISON RESULTS")
    print("="*80)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    if "output" not in result:
        print(f"❌ Unexpected response format: {result}")
        return
    
    output = result["output"]
    
    if "error" in output:
        print(f"❌ Processing error: {output['error']}")
        return
    
    # 기본 정보
    print(f"🆔 Job ID: {output.get('job_id', 'N/A')}")
    print(f"⏱️  Total Processing Time: {output.get('total_processing_time', 0)} seconds")
    
    # 개별 모델 결과
    comparison = output.get('comparison', {})
    
    print(f"\n🎭 SadTalker Results:")
    sadtalker = comparison.get('sadtalker', {})
    print(f"   ✅ Success: {sadtalker.get('success', False)}")
    print(f"   ⏱️  Processing Time: {sadtalker.get('processing_time', 0)} seconds")
    print(f"   📁 Output Size: {sadtalker.get('output_file_size_mb', 0)} MB")
    if sadtalker.get('error'):
        print(f"   ❌ Error: {sadtalker['error']}")
    
    print(f"\n💋 Wav2Lip Results:")
    wav2lip = comparison.get('wav2lip', {})
    print(f"   ✅ Success: {wav2lip.get('success', False)}")
    print(f"   ⏱️  Processing Time: {wav2lip.get('processing_time', 0)} seconds")
    print(f"   📁 Output Size: {wav2lip.get('output_file_size_mb', 0)} MB")
    if wav2lip.get('error'):
        print(f"   ❌ Error: {wav2lip['error']}")
    
    # 분석 결과
    analysis = output.get('analysis', {})
    print(f"\n📈 Analysis:")
    print(f"   🏆 Faster Model: {analysis.get('faster_model', 'N/A').upper()}")
    print(f"   ⏰ Time Difference: {analysis.get('time_difference', 0)} seconds")
    print(f"   ✅ Both Succeeded: {analysis.get('both_succeeded', False)}")
    
    # 비용 추정 (대략적)
    total_time_minutes = output.get('total_processing_time', 0) / 60
    estimated_cost = total_time_minutes * 0.0018  # RTX 4090 기준 대략적인 비용
    print(f"\n💰 Estimated Cost: ${estimated_cost:.4f}")
    
    # 메타데이터
    metadata = output.get('metadata', {})
    if metadata:
        print(f"\n📋 Metadata:")
        print(f"   📅 Processing Date: {metadata.get('processing_date', 'N/A')}")
        print(f"   🐍 Python Version: {metadata.get('python_version', 'N/A')}")

def main():
    """메인 함수"""
    
    print("🎬 RunPod Serverless: SadTalker vs Wav2Lip 비교 테스트")
    print("="*80)
    
    # 환경 변수 확인
    if not RUNPOD_API_KEY:
        print("❌ RUNPOD_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   다음 명령어로 설정하세요:")
        print("   export RUNPOD_API_KEY='your-api-key-here'")
        return
    
    if not RUNPOD_ENDPOINT_ID:
        print("❌ RUNPOD_ENDPOINT_ID 환경 변수가 설정되지 않았습니다.")
        print("   다음 명령어로 설정하세요:")
        print("   export RUNPOD_ENDPOINT_ID='your-endpoint-id-here'")
        return
    
    # WAV 형식으로 테스트
    result = run_comparison_test("wav")
    analyze_results(result)
    
    # 추가 테스트를 원한다면 MP3로도 테스트
    choice = input("\n🎵 MP3 형식으로도 테스트하시겠습니까? (y/N): ").strip().lower()
    if choice == 'y' or choice == 'yes':
        print("\n" + "-"*80)
        result_mp3 = run_comparison_test("mp3")
        analyze_results(result_mp3)

if __name__ == "__main__":
    main() 