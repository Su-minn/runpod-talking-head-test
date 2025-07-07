# RunPod Serverless: SadTalker vs Wav2Lip 비교 테스트

> RunPod Serverless에서 SadTalker와 Wav2Lip을 사용하여 talking head 비디오 생성 성능을 비교하는 프로젝트입니다.

## 📋 프로젝트 개요

이 프로젝트는 두 가지 인기 있는 talking head 생성 모델의 성능을 비교합니다:

- **SadTalker**: 더 자연스러운 표정과 머리 움직임
- **Wav2Lip**: 정확한 립싱크와 빠른 처리 속도

## 🏗️ 프로젝트 구조

```
runpod/
├── assets/                    # 테스트용 파일들
│   ├── profile.png           # 테스트 이미지 (1.5MB)
│   ├── test.wav              # 테스트 음성 (~9초, 288KB)
│   └── test.mp3              # 테스트 음성 (~9초, 144KB)
├── sadtalker/                # SadTalker 구현
│   ├── Dockerfile            # SadTalker Docker 이미지
│   ├── handler.py            # RunPod 핸들러
│   ├── requirements.txt      # Python 패키지
│   └── build.sh              # 빌드 스크립트
├── wav2lip/                  # Wav2Lip 구현  
│   ├── Dockerfile            # Wav2Lip Docker 이미지
│   ├── handler.py            # RunPod 핸들러
│   ├── requirements.txt      # Python 패키지
│   └── build.sh              # 빌드 스크립트
├── test_comparison.py        # 비교 테스트 스크립트
├── upload_to_github.py       # GitHub 업로드 도구
└── README.md                 # 이 파일
```

## 🚀 시작하기

### 1. 사전 준비사항

#### 필수 도구
- Docker Desktop
- Python 3.9+
- Git

#### 계정 설정
- [Docker Hub](https://hub.docker.com) 계정
- [RunPod](https://runpod.io) 계정 + API 키
- [GitHub](https://github.com) 계정 + Personal Access Token

### 2. 환경 설정

```bash
# 환경 변수 설정
export GITHUB_TOKEN='your-github-personal-access-token'
export GITHUB_USERNAME='your-github-username'
export RUNPOD_API_KEY='your-runpod-api-key'
export SADTALKER_ENDPOINT='your-sadtalker-endpoint-id'
export WAV2LIP_ENDPOINT='your-wav2lip-endpoint-id'
```

### 3. 테스트 파일 GitHub 업로드

```bash
# GitHub에 테스트 파일들 업로드
python upload_to_github.py
```

이 스크립트는:
- `runpod-talking-head-test` 리포지토리 생성
- `assets/` 폴더의 파일들을 GitHub에 업로드
- RunPod에서 사용할 raw URL 생성

### 4. Docker 이미지 빌드 및 배포

#### SadTalker 빌드
```bash
cd sadtalker
# build.sh 파일에서 DOCKER_USERNAME을 실제 Docker Hub 사용자명으로 변경
./build.sh
```

#### Wav2Lip 빌드
```bash
cd wav2lip  
# build.sh 파일에서 DOCKER_USERNAME을 실제 Docker Hub 사용자명으로 변경
./build.sh
```

### 5. RunPod에서 엔드포인트 생성

#### SadTalker 엔드포인트
1. [RunPod Console](https://www.runpod.io/console/serverless) 접속
2. "New Endpoint" → "Docker Image" 선택
3. 설정:
   - **Container Image**: `your-username/sadtalker-runpod:v1.0`
   - **GPU**: 24GB VRAM (RTX 4090)
   - **Active Workers**: 0
   - **Max Workers**: 1
   - **Idle Timeout**: 5초
   - **Execution Timeout**: 1800초 (30분)

#### Wav2Lip 엔드포인트
1. "New Endpoint" → "Docker Image" 선택
2. 설정:
   - **Container Image**: `your-username/wav2lip-runpod:v1.0`
   - **GPU**: 16GB VRAM (RTX 4080)
   - **Active Workers**: 0
   - **Max Workers**: 1
   - **Idle Timeout**: 5초
   - **Execution Timeout**: 600초 (10분)

### 6. 비교 테스트 실행

```bash
# test_comparison.py에서 URL들을 github_urls.json의 값으로 업데이트 후
python test_comparison.py
```

## 📊 예상 테스트 결과

| 항목 | SadTalker | Wav2Lip |
|------|-----------|---------|
| **처리 시간** | 15-20분 | 5-10분 |
| **비용 (9초 영상)** | $0.25-0.37 | $0.09-0.18 |
| **립싱크 정확도** | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐⭐ |
| **얼굴 표정** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐☆☆ |
| **자연스러움** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ |

## 🛠️ 커스터마이징

### SadTalker 옵션 수정
`sadtalker/handler.py`에서 명령어 옵션 변경:
```python
cmd = [
    "python", "/workspace/SadTalker/inference.py",
    "--driven_audio", audio_path,
    "--source_image", image_path,
    "--result_dir", result_dir,
    "--still",              # 정적 모드 (빠름)
    "--preprocess", "crop", # 얼굴 크롭
    "--enhancer", "gfpgan", # 품질 향상
    # "--cpu"               # CPU 모드 (GPU 메모리 절약)
]
```

### Wav2Lip 옵션 수정
`wav2lip/handler.py`에서 명령어 옵션 변경:
```python
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
    # "--nosmooth"           # 더 빠른 처리
]
```

## 💰 비용 최적화 팁

1. **Active Workers를 0으로 설정**
   - 사용하지 않을 때 비용 없음
   - 첫 요청 시 10-30초 콜드 스타트

2. **적절한 GPU 선택**
   - 테스트: 16GB GPU
   - 프로덕션: 24GB GPU

3. **배치 처리**
   - 여러 작업을 동시에 처리하여 GPU 활용률 극대화

## 🔧 문제 해결

### Docker 빌드 실패
```bash
# M1 Mac에서 빌드 시
docker buildx create --use
docker buildx build --platform linux/amd64 -t your-image .
```

### GPU 메모리 부족
- 이미지 해상도 낮추기
- `--cpu` 옵션 사용 (느리지만 안정적)
- 더 큰 GPU 사용

### 느린 처리 속도
- Enhancer 옵션 끄기
- Still mode 사용 (SadTalker)
- `--nosmooth` 옵션 사용 (Wav2Lip)

## 📈 성능 모니터링

### RunPod 로그 확인
1. Endpoint 페이지 → "Logs" 탭
2. 실시간 처리 상황 모니터링
3. 오류 메시지 확인

### 비용 추적
1. Dashboard → Billing
2. 시간당 GPU 사용량 확인
3. 예상 월간 비용 계산

## 🔄 다음 단계

### 프로덕션 준비
- S3 연동으로 파일 업로드/다운로드
- 에러 핸들링 강화
- 로깅 시스템 구축
- 웹훅으로 완료 알림

### 성능 최적화
- 모델 양자화로 속도 개선
- 멀티 GPU 활용
- 캐싱 시스템 구현

### 기능 확장
- 실시간 스트리밍 지원
- 배치 처리 API
- 웹 UI 개발

## 📝 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해주세요.

---

**Happy Talking Head Generation! 🎬** 