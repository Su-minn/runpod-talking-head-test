# 🚀 RunPod Serverless: SadTalker vs Wav2Lip 비교 가이드

## 📋 개요

이 프로젝트는 **RunPod Serverless**를 사용해서 **SadTalker**와 **Wav2Lip** 두 모델로 9초 음성과 이미지를 사용한 talking head를 만들고 비교합니다.

**✅ 올바른 방식: 기존 Docker 이미지 사용**
- SadTalker: `vinthony/sadtalker`
- Wav2Lip: `devxpy/cog-wav2lip` 또는 `rudrabha/wav2lip`

## 📁 프로젝트 구조

```
runpod/
├── assets/                           # 테스트 파일들 (GitHub에서 호스팅)
│   ├── profile.png                   # 1.6MB 이미지
│   ├── test.wav                      # 9.22초 WAV 음성
│   └── test.mp3                      # 9.22초 MP3 음성
├── sadtalker/
│   └── handler_runpod.py            # SadTalker RunPod handler
├── wav2lip/
│   └── handler_runpod.py            # Wav2Lip RunPod handler
├── compare_models.py                 # 비교 테스트 스크립트
└── README_RUNPOD_SETUP.md           # 이 파일
```

## 🎯 RunPod 설정 단계

### **Step 1: RunPod 계정 준비**

1. **가입**: [runpod.io](https://runpod.io) 가입
2. **크레딧 충전**: $10-20 충전 (테스트용)
3. **API Key 생성**: 
   - Dashboard → Settings → API Keys
   - "Create API Key" 클릭
   - **YOUR_API_KEY_HERE** (RunPod에서 생성)

### **Step 2: SadTalker 템플릿 생성**

1. **Serverless → Templates** 메뉴 이동
2. **"+ New Template"** 클릭
3. 다음 정보 입력:

```
Template Name: SadTalker-Handler
Container Image: vinthony/sadtalker:latest
Container Disk: 15 GB
Container Start Command: (비워두기)
Docker Command: (비워두기)
Ports: 8000
Environment Variables: (없음)
```

4. **"Save Template"** 클릭

### **Step 3: Wav2Lip 템플릿 생성**

1. **"+ New Template"** 클릭
2. 다음 정보 입력:

```
Template Name: Wav2Lip-Handler  
Container Image: devxpy/cog-wav2lip:latest
Container Disk: 10 GB
Container Start Command: (비워두기)
Docker Command: (비워두기)
Ports: 8000
Environment Variables: (없음)
```

3. **"Save Template"** 클릭

### **Step 4: SadTalker 엔드포인트 생성**

1. **Serverless → Endpoints** 메뉴 이동
2. **"+ New Endpoint"** 클릭
3. 다음 설정:

```
Endpoint Name: SadTalker-Endpoint
Template: SadTalker-Handler (위에서 생성한 템플릿)
GPU Type: RTX A5000 또는 RTX 4090 (16GB+ VRAM 권장)
Max Workers: 1
Idle Timeout: 5 minutes
Flash Boot: ON (빠른 시작)
```

4. **"Deploy"** 클릭
5. **Endpoint ID 복사** (예: `abcd1234-efgh-5678-ijkl-9012mnop3456`)

### **Step 5: Wav2Lip 엔드포인트 생성**

1. **"+ New Endpoint"** 클릭
2. 다음 설정:

```
Endpoint Name: Wav2Lip-Endpoint
Template: Wav2Lip-Handler (위에서 생성한 템플릿)
GPU Type: RTX 3090 또는 RTX 4090 (8GB+ VRAM)
Max Workers: 1
Idle Timeout: 5 minutes
Flash Boot: ON
```

3. **"Deploy"** 클릭
4. **Endpoint ID 복사** (예: `wxyz7890-abcd-1234-efgh-5678ijkl9012`)

### **Step 6: Handler 코드 업로드**

각 엔드포인트에 handler 코드를 업로드해야 합니다:

**SadTalker 엔드포인트:**
- `sadtalker/handler_runpod.py` 파일 내용을 복사
- RunPod Console에서 해당 엔드포인트의 "Edit" → "Handler Code" 탭
- 코드 붙여넣기 후 "Save" 

**Wav2Lip 엔드포인트:**
- `wav2lip/handler_runpod.py` 파일 내용을 복사
- RunPod Console에서 해당 엔드포인트의 "Edit" → "Handler Code" 탭  
- 코드 붙여넣기 후 "Save"

## 🧪 테스트 실행

### **환경변수 설정**

터미널에서 다음 명령어 실행:

```bash
# RunPod API Key
export RUNPOD_API_KEY="YOUR_API_KEY_HERE"

# 엔드포인트 ID들 (위에서 생성한 ID들로 변경)
export SADTALKER_ENDPOINT_ID="your-sadtalker-endpoint-id"
export WAV2LIP_ENDPOINT_ID="your-wav2lip-endpoint-id"
```

### **비교 테스트 실행**

```bash
python3 compare_models.py
```

## 📊 테스트 파일 정보

### **GitHub Raw URLs (자동 설정됨)**
- **이미지**: https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/profile.png
- **WAV 음성**: https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.wav  
- **MP3 음성**: https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.mp3

### **파일 세부정보**
- **profile.png**: 1,607,721 bytes (1.6MB)
- **test.wav**: 295,158 bytes (288KB, 9.22초)
- **test.mp3**: 147,584 bytes (144KB, 9.22초)

## 💰 예상 비용

### **SadTalker (A100 GPU 기준)**
- 처리 시간: 15-20분
- GPU 비용: ~$0.30-0.40
- 서비스 요금: ~$0.03-0.04
- **총 비용: ~$0.33-0.44**

### **Wav2Lip (RTX 4090 기준)**
- 처리 시간: 5-10분  
- GPU 비용: ~$0.04-0.08
- 서비스 요금: ~$0.004-0.008
- **총 비용: ~$0.044-0.088**

## 🎯 비교 결과 예측

| 항목 | SadTalker | Wav2Lip | 승자 |
|------|-----------|---------|------|
| **속도** | 15-20분 | 5-10분 | 🏆 Wav2Lip |
| **비용** | $0.33-0.44 | $0.04-0.09 | 🏆 Wav2Lip |
| **품질** | 자연스러운 표정 | 정확한 립싱크 | 용도에 따라 다름 |
| **안정성** | 높음 | 높음 | 비슷 |

## 🔧 문제 해결

### **엔드포인트가 시작되지 않는 경우**
1. GPU 가용성 확인
2. 템플릿 설정 재확인
3. Container Disk 용량 증가 (20GB로)

### **Handler 오류가 발생하는 경우**
1. 로그 확인: RunPod Console → Endpoint → Logs
2. 파일 경로 확인: `/workspace/` 경로 사용
3. 종속성 설치: requirements.txt 확인

### **API 호출 실패하는 경우**
1. API Key 확인
2. Endpoint ID 확인  
3. 네트워크 연결 확인

## 📝 추가 기능

### **옵션 사용자 정의**

**SadTalker 옵션:**
```python
"options": {
    "still_mode": True,           # 정적 모드 (빠름)
    "preprocess": "crop",         # 전처리 방식
    "enhancer": "gfpgan",         # 얼굴 향상
    "pose_style": 0,              # 포즈 스타일 (0-45)
    "face_model_resolution": 256  # 해상도
}
```

**Wav2Lip 옵션:**
```python
"options": {
    "quality": "high",            # 품질 (low/medium/high)
    "pad_top": 0,                 # 패딩
    "pad_bottom": 10,
    "pad_left": 0, 
    "pad_right": 0,
    "resize_factor": 1,           # 크기 조정
    "nosmooth": False             # 부드러움 비활성화
}
```

## ✅ 성공 체크리스트

- [ ] RunPod 계정 생성 및 크레딧 충전
- [ ] API Key 생성 
- [ ] SadTalker 템플릿 생성
- [ ] Wav2Lip 템플릿 생성
- [ ] SadTalker 엔드포인트 생성 및 Handler 업로드
- [ ] Wav2Lip 엔드포인트 생성 및 Handler 업로드
- [ ] 환경변수 설정
- [ ] 비교 테스트 실행
- [ ] 결과 분석

🎉 **모든 단계를 완료하면 두 모델의 성능을 정확히 비교할 수 있습니다!** 