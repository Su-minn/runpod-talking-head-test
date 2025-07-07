#!/usr/bin/env python3
"""
SadTalker vs Wav2Lip 비교 테스트 스크립트

이 스크립트는 RunPod Serverless에서 SadTalker와 Wav2Lip을 
사용하여 talking head 비디오를 생성하고 결과를 비교합니다.
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Optional

class TalkingHeadTester:
    def __init__(self, api_key: str):
        """
        테스터 초기화
        
        Args:
            api_key: RunPod API 키
        """
        self.api_key = api_key
        self.base_url = "https://api.runpod.ai/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # GPU 비용 (시간당 달러)
        self.gpu_costs = {
            "rtx_4090": 1.10,  # 24GB VRAM
            "rtx_4080": 0.89,  # 16GB VRAM
            "a100": 2.89       # 80GB VRAM
        }
    
    def test_endpoint(self, endpoint_id: str, image_url: str, audio_url: str, 
                     model_name: str, timeout: int = 1800) -> Optional[Dict]:
        """
        RunPod 엔드포인트 테스트
        
        Args:
            endpoint_id: RunPod 엔드포인트 ID
            image_url: 이미지 URL
            audio_url: 음성 URL  
            model_name: 모델명 (sadtalker 또는 wav2lip)
            timeout: 타임아웃 (초)
            
        Returns:
            결과 딕셔너리 또는 None
        """
        try:
            print(f"\n=== {model_name.upper()} 테스트 시작 ===")
            start_time = time.time()
            
            # 작업 요청
            payload = {
                "input": {
                    "input_image_url": image_url,
                    "input_audio_url": audio_url
                }
            }
            
            print(f"요청 전송 중...")
            response = requests.post(
                f"{self.base_url}/{endpoint_id}/runsync",
                headers=self.headers,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code != 200:
                print(f"API 오류: {response.status_code}")
                print(f"응답: {response.text}")
                return None
            
            result = response.json()
            total_time = time.time() - start_time
            
            if result.get('status') == 'COMPLETED':
                output = result.get('output', {})
                execution_time = result.get('executionTime', 0) / 1000  # ms to s
                delay_time = result.get('delayTime', 0) / 1000  # ms to s
                
                print(f"✅ {model_name} 성공!")
                print(f"   실행 시간: {execution_time:.2f}초")
                print(f"   지연 시간: {delay_time:.2f}초")
                print(f"   총 시간: {total_time:.2f}초")
                
                if output.get('output_file_size'):
                    size_mb = output['output_file_size'] / (1024 * 1024)
                    print(f"   파일 크기: {size_mb:.2f}MB")
                
                return {
                    "model": model_name,
                    "success": True,
                    "execution_time": execution_time,
                    "delay_time": delay_time,
                    "total_time": total_time,
                    "output_url": output.get('output_video_url'),
                    "file_size": output.get('output_file_size', 0),
                    "processing_details": output
                }
            else:
                error_msg = result.get('error', '알 수 없는 오류')
                print(f"❌ {model_name} 실패: {error_msg}")
                return {
                    "model": model_name,
                    "success": False,
                    "error": error_msg,
                    "total_time": total_time
                }
                
        except requests.exceptions.Timeout:
            print(f"❌ {model_name} 타임아웃 ({timeout}초)")
            return {
                "model": model_name,
                "success": False,
                "error": "타임아웃",
                "total_time": time.time() - start_time
            }
        except Exception as e:
            print(f"❌ {model_name} 오류: {str(e)}")
            return {
                "model": model_name,
                "success": False,
                "error": str(e),
                "total_time": time.time() - start_time
            }
    
    def calculate_cost(self, execution_time: float, gpu_type: str = "rtx_4090") -> float:
        """
        비용 계산
        
        Args:
            execution_time: 실행 시간 (초)
            gpu_type: GPU 타입
            
        Returns:
            비용 (달러)
        """
        hourly_rate = self.gpu_costs.get(gpu_type, 1.10)
        return (execution_time / 3600) * hourly_rate
    
    def compare_results(self, sadtalker_result: Dict, wav2lip_result: Dict) -> None:
        """
        결과 비교 분석
        
        Args:
            sadtalker_result: SadTalker 결과
            wav2lip_result: Wav2Lip 결과
        """
        print("\n" + "="*60)
        print("📊 모델 비교 분석 결과")
        print("="*60)
        
        # 기본 정보
        models_data = [
            ("모델", "SadTalker", "Wav2Lip"),
            ("성공 여부", 
             "✅" if sadtalker_result.get('success') else "❌",
             "✅" if wav2lip_result.get('success') else "❌")
        ]
        
        if sadtalker_result.get('success') and wav2lip_result.get('success'):
            # 성능 비교
            sad_exec = sadtalker_result.get('execution_time', 0)
            wav_exec = wav2lip_result.get('execution_time', 0)
            
            sad_total = sadtalker_result.get('total_time', 0)
            wav_total = wav2lip_result.get('total_time', 0)
            
            # 비용 계산
            sad_cost = self.calculate_cost(sad_exec)
            wav_cost = self.calculate_cost(wav_exec)
            
            # 파일 크기
            sad_size = sadtalker_result.get('file_size', 0) / (1024 * 1024)
            wav_size = wav2lip_result.get('file_size', 0) / (1024 * 1024)
            
            models_data.extend([
                ("실행 시간", f"{sad_exec:.1f}초", f"{wav_exec:.1f}초"),
                ("총 시간", f"{sad_total:.1f}초", f"{wav_total:.1f}초"),
                ("예상 비용", f"${sad_cost:.4f}", f"${wav_cost:.4f}"),
                ("파일 크기", f"{sad_size:.1f}MB", f"{wav_size:.1f}MB"),
                ("속도 비교", 
                 f"기준", 
                 f"{sad_exec/wav_exec:.1f}배 빠름" if wav_exec > 0 else "N/A"),
                ("비용 효율성",
                 f"기준",
                 f"{sad_cost/wav_cost:.1f}배 저렴" if wav_cost > 0 else "N/A")
            ])
        
        # 테이블 출력
        for row in models_data:
            print(f"{row[0]:<12} | {row[1]:<15} | {row[2]:<15}")
        
        print("\n" + "="*60)
        
        # 추천 사항
        print("🎯 추천 사항:")
        if sadtalker_result.get('success') and wav2lip_result.get('success'):
            sad_exec = sadtalker_result.get('execution_time', 0)
            wav_exec = wav2lip_result.get('execution_time', 0)
            
            if wav_exec < sad_exec:
                print("   • 빠른 처리가 필요한 경우: Wav2Lip")
                print("   • 자연스러운 표정이 중요한 경우: SadTalker")
            else:
                print("   • 균형잡힌 품질과 속도: SadTalker")
                print("   • 정확한 립싱크가 중요한 경우: Wav2Lip")
        
        print("   • 프로덕션 환경: 요구사항에 따라 선택")
        print("   • 비용 최적화: Active Workers를 0으로 설정")
    
    def run_comparison_test(self, 
                           sadtalker_endpoint: str,
                           wav2lip_endpoint: str,
                           image_url: str,
                           audio_url: str) -> None:
        """
        비교 테스트 실행
        
        Args:
            sadtalker_endpoint: SadTalker 엔드포인트 ID
            wav2lip_endpoint: Wav2Lip 엔드포인트 ID
            image_url: 테스트 이미지 URL
            audio_url: 테스트 음성 URL
        """
        print("🚀 Talking Head 모델 비교 테스트 시작")
        print(f"이미지: {image_url}")
        print(f"음성: {audio_url}")
        
        # SadTalker 테스트
        sadtalker_result = self.test_endpoint(
            sadtalker_endpoint, 
            image_url, 
            audio_url, 
            "sadtalker",
            timeout=1800  # 30분
        )
        
        # Wav2Lip 테스트
        wav2lip_result = self.test_endpoint(
            wav2lip_endpoint,
            image_url,
            audio_url,
            "wav2lip", 
            timeout=600   # 10분
        )
        
        # 결과 비교
        if sadtalker_result and wav2lip_result:
            self.compare_results(sadtalker_result, wav2lip_result)
            
            # 결과 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results = {
                "timestamp": timestamp,
                "sadtalker": sadtalker_result,
                "wav2lip": wav2lip_result,
                "test_files": {
                    "image_url": image_url,
                    "audio_url": audio_url
                }
            }
            
            with open(f"test_results_{timestamp}.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 결과 저장됨: test_results_{timestamp}.json")
        else:
            print("\n❌ 테스트 실패")

def main():
    """메인 함수"""
    print("="*60)
    print("🎬 RunPod Talking Head 비교 테스트")
    print("="*60)
    
    # 설정 (실제 값으로 변경 필요)
    API_KEY = os.getenv("RUNPOD_API_KEY", "your-runpod-api-key")
    SADTALKER_ENDPOINT = os.getenv("SADTALKER_ENDPOINT", "your-sadtalker-endpoint-id")
    WAV2LIP_ENDPOINT = os.getenv("WAV2LIP_ENDPOINT", "your-wav2lip-endpoint-id")
    
    # 테스트 파일 URL (GitHub raw URL 사용 예정)
    IMAGE_URL = "https://raw.githubusercontent.com/your-username/repo/main/assets/profile.png"
    AUDIO_URL = "https://raw.githubusercontent.com/your-username/repo/main/assets/test.wav"
    
    if API_KEY == "your-runpod-api-key":
        print("⚠️  환경 변수 설정이 필요합니다:")
        print("export RUNPOD_API_KEY='your-actual-api-key'")
        print("export SADTALKER_ENDPOINT='your-sadtalker-endpoint-id'")
        print("export WAV2LIP_ENDPOINT='your-wav2lip-endpoint-id'")
        return
    
    # 테스터 생성 및 실행
    tester = TalkingHeadTester(API_KEY)
    tester.run_comparison_test(
        SADTALKER_ENDPOINT,
        WAV2LIP_ENDPOINT,
        IMAGE_URL,
        AUDIO_URL
    )

if __name__ == "__main__":
    main() 