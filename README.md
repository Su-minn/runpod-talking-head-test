# 🎬 RunPod Serverless: SadTalker vs Wav2Lip 비교 테스트

9초 음성과 이미지로 SadTalker와 Wav2Lip을 RunPod Serverless에서 비교 테스트하는 프로젝트입니다.

## 📁 프로젝트 구조

```
runpod/
├── assets/                           # 테스트용 파일들
│   ├── profile.png                   # 1.6MB 이미지 (1607721 bytes)
│   ├── test.wav                      # 9.22초 WAV 음성 (295158 bytes)
│   └── test.mp3                      # 9.22초 MP3 음성 (147584 bytes)
├── runpod_comparison_handler.py      # 통합 RunPod handler
├── Dockerfile.comparison             # 통합 Docker 이미지
├── build_comparison_image.sh         # Docker 빌드 스크립트
├── test_runpod_comparison.py         # RunPod 테스트 스크립트
└── README.md                         # 이 파일
```

## 🚀 빠른 시작

### 1. 전제 조건

- **RunPod 계정** ([runpod.io](https://runpod.io) 가입)
- **Docker Hub 계정** (Docker 이미지 푸시용)
- **Docker Desktop** (로컬 빌드용)
- **Python 3.8+** (테스트 스크립트용)

### 2. RunPod 설정

1. **크레딧 충전**: 테스트용으로 $10-20 권장
2. **API Key 생성**: Settings → API Keys → Create API Key

### 3. Docker 이미지 빌드

```bash
# Docker Hub 사용자명 수정
vim build_comparison_image.sh
# DOCKER_USERNAME="your-dockerhub-username" 수정

# 이미지 빌드 및 푸시
./build_comparison_image.sh
```

### 4. RunPod Serverless 설정

1. **Template 생성**:
   - RunPod Dashboard → Serverless → Templates
   - Container Image: `your-dockerhub-username/runpod-talking-head-comparison:latest`
   - Container Disk: 15GB 이상
   - Exposed HTTP Ports: 8000

2. **Endpoint 생성**:
   - Serverless → Endpoints → Create
   - Template 선택
   - Workers: 0/3 (오토스케일링)
   - GPU: RTX 4090 또는 A100 권장

### 5. 테스트 실행

```bash
# 환경 변수 설정
export RUNPOD_API_KEY="your-api-key-here"
export RUNPOD_ENDPOINT_ID="your-endpoint-id-here"

# 가상환경 활성화 (선택사항)
source venv/bin/activate

# 테스트 실행
python test_runpod_comparison.py
```

## 📊 예상 결과

### SadTalker
- **처리 시간**: 15-20분
- **비용**: $0.25-0.37
- **특징**: 자연스러운 표정과 머리 움직임
- **출력 크기**: 5-10MB

### Wav2Lip
- **처리 시간**: 5-10분  
- **비용**: $0.09-0.18
- **특징**: 정확한 립싱크, 빠른 처리
- **출력 크기**: 3-7MB

## 🛠️ 기술 스택

### AI 모델
- **SadTalker**: OpenTalker/SadTalker (GitHub)
- **Wav2Lip**: Rudrabha/Wav2Lip (GitHub)

### 인프라
- **RunPod Serverless**: GPU 서버리스 플랫폼
- **Docker**: 컨테이너화
- **GitHub**: 파일 호스팅 (Raw URLs)

### 개발 환경
- **Python 3.8+**: 백엔드 로직
- **PyTorch 1.13**: 딥러닝 프레임워크
- **CUDA 11.7**: GPU 가속

## 📋 자세한 가이드

### Docker 이미지 상세

통합 Docker 이미지에 포함된 구성요소:

```dockerfile
# 베이스 이미지
FROM nvidia/cuda:11.7.1-devel-ubuntu20.04

# 주요 구성요소
- SadTalker (완전 설치)
- Wav2Lip (완전 설치)  
- GFPGAN (얼굴 개선)
- 사전 다운로드된 모델들
- RunPod handler
```

### API 사용법

```python
# 요청 형식
payload = {
    "input": {
        "input_image_url": "https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/profile.png",
        "input_audio_url": "https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.wav",
        "return_videos": False  # True이면 base64로 비디오 반환
    }
}

# 응답 형식
{
    "job_id": "unique-job-id",
    "total_processing_time": 1800.5,
    "comparison": {
        "sadtalker": {
            "processing_time": 1200.3,
            "success": true,
            "output_file_size_mb": 8.5
        },
        "wav2lip": {
            "processing_time": 600.2,
            "success": true,
            "output_file_size_mb": 5.2
        }
    },
    "analysis": {
        "faster_model": "wav2lip",
        "time_difference": 600.1,
        "both_succeeded": true
    }
}
```

## 🎯 테스트 파일 정보

### GitHub Raw URLs
- **이미지**: `https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/profile.png`
- **WAV 음성**: `https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.wav`
- **MP3 음성**: `https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.mp3`

### 파일 상세
- **profile.png**: 1,607,721 bytes (1.6MB)
- **test.wav**: 295,158 bytes (288KB), 9.22초
- **test.mp3**: 147,584 bytes (144KB), 9.22초

## 💰 비용 분석

### GPU 비용 (RTX 4090 기준)
- **시간당 비용**: ~$1.08
- **분당 비용**: ~$0.018

### 예상 테스트 비용
- **SadTalker**: 20분 × $0.018 = $0.36
- **Wav2Lip**: 10분 × $0.018 = $0.18
- **총 비교 테스트**: ~$0.54

## 🔧 문제 해결

### 일반적인 문제

1. **Docker 빌드 실패**
   ```bash
   # Docker Desktop이 실행 중인지 확인
   docker info
   
   # buildx 설정 (M1/M2 Mac)
   docker buildx create --use
   ```

2. **RunPod API 오류**
   ```bash
   # API 키 확인
   echo $RUNPOD_API_KEY
   
   # Endpoint 상태 확인
   # RunPod Dashboard에서 확인
   ```

3. **모델 다운로드 실패**
   - 인터넷 연결 확인
   - 모델 URL 유효성 확인
   - 충분한 디스크 공간 확인

### 로그 확인

```bash
# RunPod 로그 확인
# Dashboard → Serverless → Endpoints → Logs
```

## 📈 성능 최적화

### GPU 선택 가이드
- **개발/테스트**: RTX 4090 (권장)
- **프로덕션**: A100 (최고 성능)
- **예산 절약**: RTX 3090 (기본)

### 비용 최적화
1. **Workers 0/3 설정**: 사용하지 않을 때 비용 없음
2. **적절한 timeout 설정**: 15분 권장
3. **배치 처리**: 여러 파일을 한 번에 처리

## 🤝 기여하기

1. Fork this repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **Issues**: GitHub Issues 탭에서 문제 보고
- **Discussions**: GitHub Discussions에서 질문
- **Documentation**: [RunPod 공식 문서](https://docs.runpod.io/)

---

**만든 이**: Su-minn  
**Repository**: [runpod-talking-head-test](https://github.com/Su-minn/runpod-talking-head-test)  
**마지막 업데이트**: 2025년 1월 7일 