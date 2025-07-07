#!/usr/bin/env python3
"""
RunPod Serverless: SadTalker vs Wav2Lip 비교 테스트
두 개의 서로 다른 엔드포인트를 호출해서 결과를 비교합니다.
"""

import requests
import json
import time
import os
from typing import Dict, Any, Optional

# RunPod API 설정
RUNPOD_API_KEY = os.getenv('RUNPOD_API_KEY')

# 엔드포인트 ID들 (RunPod 웹사이트에서 생성 후 설정)
SADTALKER_ENDPOINT_ID = os.getenv('SADTALKER_ENDPOINT_ID')
WAV2LIP_ENDPOINT_ID = os.getenv('WAV2LIP_ENDPOINT_ID')

# GitHub Raw URLs
GITHUB_IMAGE_URL = "https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/profile.png"
GITHUB_AUDIO_WAV_URL = "https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.wav"
GITHUB_AUDIO_MP3_URL = "https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.mp3"

def call_runpod_endpoint(endpoint_id: str, api_key: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """RunPod Serverless 엔드포인트 호출"""
    
    if not endpoint_id:
        print(f"❌ Endpoint ID not provided")
        return None
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        print(f"🔄 Calling RunPod endpoint: {endpoint_id}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=1800)  # 30분 타임아웃
        api_call_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API call completed in {api_call_time:.2f}s")
            print(f"📊 Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error calling endpoint: {e}")
        return None

def test_sadtalker():
    """SadTalker 테스트"""
    print("\n🎭 Testing SadTalker...")
    print("=" * 50)
    
    payload = {
        "input": {
            "input_image_url": GITHUB_IMAGE_URL,
            "input_audio_url": GITHUB_AUDIO_MP3_URL,  # SadTalker는 MP3도 지원
            "options": {
                "still_mode": True,
                "preprocess": "crop",
                "enhancer": "gfpgan",
                "pose_style": 0,
                "face_model_resolution": 256
            }
        }
    }
    
    start_time = time.time()
    result = call_runpod_endpoint(SADTALKER_ENDPOINT_ID, RUNPOD_API_KEY, payload)
    total_time = time.time() - start_time
    
    if result:
        return {
            "model": "SadTalker",
            "success": True,
            "total_time": total_time,
            "processing_time": result.get('output', {}).get('processing_time', 0),
            "result": result,
            "image_url": GITHUB_IMAGE_URL,
            "audio_url": GITHUB_AUDIO_MP3_URL
        }
    else:
        return {
            "model": "SadTalker",
            "success": False,
            "total_time": total_time,
            "error": "API call failed"
        }

def test_wav2lip():
    """Wav2Lip 테스트"""
    print("\n💋 Testing Wav2Lip...")
    print("=" * 50)
    
    payload = {
        "input": {
            "input_image_url": GITHUB_IMAGE_URL,
            "input_audio_url": GITHUB_AUDIO_WAV_URL,  # Wav2Lip은 WAV 선호
            "options": {
                "quality": "high",
                "pad_top": 0,
                "pad_bottom": 10,
                "pad_left": 0,
                "pad_right": 0,
                "resize_factor": 1,
                "nosmooth": False
            }
        }
    }
    
    start_time = time.time()
    result = call_runpod_endpoint(WAV2LIP_ENDPOINT_ID, RUNPOD_API_KEY, payload)
    total_time = time.time() - start_time
    
    if result:
        return {
            "model": "Wav2Lip",
            "success": True,
            "total_time": total_time,
            "processing_time": result.get('output', {}).get('processing_time', 0),
            "result": result,
            "image_url": GITHUB_IMAGE_URL,
            "audio_url": GITHUB_AUDIO_WAV_URL
        }
    else:
        return {
            "model": "Wav2Lip",
            "success": False,
            "total_time": total_time,
            "error": "API call failed"
        }

def calculate_costs(processing_time: float, model: str) -> Dict[str, float]:
    """비용 계산 (RunPod Serverless 가격 기준)"""
    
    # RunPod GPU 시간당 가격 (추정)
    # RTX 4090: $0.50/hour
    # A100: $1.20/hour
    
    if model == "SadTalker":
        # SadTalker는 더 많은 GPU 리소스 사용
        gpu_price_per_hour = 1.20  # A100 기준
    else:
        # Wav2Lip은 상대적으로 적은 리소스 사용
        gpu_price_per_hour = 0.50  # RTX 4090 기준
    
    processing_hours = processing_time / 3600
    gpu_cost = processing_hours * gpu_price_per_hour
    
    # RunPod 서비스 요금 (약 10% 추가)
    service_fee = gpu_cost * 0.1
    total_cost = gpu_cost + service_fee
    
    return {
        "gpu_cost": round(gpu_cost, 4),
        "service_fee": round(service_fee, 4),
        "total_cost": round(total_cost, 4),
        "processing_hours": round(processing_hours, 4)
    }

def compare_results(sadtalker_result: Dict, wav2lip_result: Dict):
    """결과 비교 분석"""
    print("\n📊 COMPARISON RESULTS")
    print("=" * 60)
    
    # 성공 여부 확인
    both_success = sadtalker_result['success'] and wav2lip_result['success']
    
    if not both_success:
        print("❌ One or both models failed:")
        if not sadtalker_result['success']:
            print(f"   SadTalker failed: {sadtalker_result.get('error', 'Unknown error')}")
        if not wav2lip_result['success']:
            print(f"   Wav2Lip failed: {wav2lip_result.get('error', 'Unknown error')}")
        return
    
    # 처리 시간 비교
    print("⏱️  PROCESSING TIME COMPARISON:")
    print(f"   SadTalker: {sadtalker_result['processing_time']:.2f}s")
    print(f"   Wav2Lip:   {wav2lip_result['processing_time']:.2f}s")
    
    time_diff = sadtalker_result['processing_time'] - wav2lip_result['processing_time']
    if time_diff > 0:
        print(f"   🏆 Wav2Lip is {time_diff:.2f}s faster")
    else:
        print(f"   🏆 SadTalker is {abs(time_diff):.2f}s faster")
    
    # 비용 비교
    print("\n💰 COST COMPARISON:")
    sadtalker_costs = calculate_costs(sadtalker_result['processing_time'], "SadTalker")
    wav2lip_costs = calculate_costs(wav2lip_result['processing_time'], "Wav2Lip")
    
    print(f"   SadTalker: ${sadtalker_costs['total_cost']:.4f}")
    print(f"   Wav2Lip:   ${wav2lip_costs['total_cost']:.4f}")
    
    cost_diff = sadtalker_costs['total_cost'] - wav2lip_costs['total_cost']
    if cost_diff > 0:
        print(f"   🏆 Wav2Lip is ${cost_diff:.4f} cheaper")
    else:
        print(f"   🏆 SadTalker is ${abs(cost_diff):.4f} cheaper")
    
    # 파일 크기 비교 (가능한 경우)
    print("\n📁 OUTPUT FILE SIZE:")
    sad_size = sadtalker_result.get('result', {}).get('output', {}).get('file_size', 0)
    wav_size = wav2lip_result.get('result', {}).get('output', {}).get('file_size', 0)
    
    if sad_size and wav_size:
        print(f"   SadTalker: {sad_size / (1024*1024):.2f} MB")
        print(f"   Wav2Lip:   {wav_size / (1024*1024):.2f} MB")
    
    # 종합 평가
    print("\n🎯 SUMMARY:")
    print(f"   Speed Winner:  {'Wav2Lip' if time_diff > 0 else 'SadTalker'}")
    print(f"   Cost Winner:   {'Wav2Lip' if cost_diff > 0 else 'SadTalker'}")
    print(f"   Quality:       Manual comparison needed")
    
    # 상세 비용 분석
    print("\n💡 DETAILED COST ANALYSIS:")
    print("   SadTalker:")
    print(f"     - Processing: {sadtalker_costs['processing_hours']:.4f} hours")
    print(f"     - GPU Cost: ${sadtalker_costs['gpu_cost']:.4f}")
    print(f"     - Service Fee: ${sadtalker_costs['service_fee']:.4f}")
    print(f"     - Total: ${sadtalker_costs['total_cost']:.4f}")
    
    print("   Wav2Lip:")
    print(f"     - Processing: {wav2lip_costs['processing_hours']:.4f} hours")
    print(f"     - GPU Cost: ${wav2lip_costs['gpu_cost']:.4f}")
    print(f"     - Service Fee: ${wav2lip_costs['service_fee']:.4f}")
    print(f"     - Total: ${wav2lip_costs['total_cost']:.4f}")

def main():
    """메인 테스트 함수"""
    print("🚀 RunPod Serverless: SadTalker vs Wav2Lip Comparison Test")
    print("=" * 80)
    
    # 환경 변수 확인
    if not RUNPOD_API_KEY:
        print("❌ RUNPOD_API_KEY environment variable not set")
        print("💡 Run: export RUNPOD_API_KEY=\"your-api-key\"")
        return
    
    if not SADTALKER_ENDPOINT_ID:
        print("❌ SADTALKER_ENDPOINT_ID environment variable not set")
        print("💡 Run: export SADTALKER_ENDPOINT_ID=\"your-sadtalker-endpoint-id\"")
        return
    
    if not WAV2LIP_ENDPOINT_ID:
        print("❌ WAV2LIP_ENDPOINT_ID environment variable not set")
        print("💡 Run: export WAV2LIP_ENDPOINT_ID=\"your-wav2lip-endpoint-id\"")
        return
    
    print(f"🔑 API Key: {RUNPOD_API_KEY[:10]}...")
    print(f"📷 Image: {GITHUB_IMAGE_URL}")
    print(f"🎵 Audio (WAV): {GITHUB_AUDIO_WAV_URL}")
    print(f"🎵 Audio (MP3): {GITHUB_AUDIO_MP3_URL}")
    
    # 테스트 실행
    start_time = time.time()
    
    # 병렬 테스트를 위해 동시에 실행할 수도 있지만,
    # 여기서는 순차적으로 실행해서 결과를 비교
    sadtalker_result = test_sadtalker()
    wav2lip_result = test_wav2lip()
    
    total_test_time = time.time() - start_time
    
    # 결과 비교
    compare_results(sadtalker_result, wav2lip_result)
    
    print(f"\n⏱️  Total test time: {total_test_time:.2f}s")
    print("✅ Comparison test completed!")

if __name__ == "__main__":
    main() 