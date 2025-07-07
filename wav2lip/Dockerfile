FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04

# 환경 변수 설정
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    python3-dev \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Python 심볼릭 링크 생성
RUN ln -s /usr/bin/python3.9 /usr/bin/python

# 작업 디렉토리 설정
WORKDIR /workspace

# pip 업그레이드
RUN python -m pip install --upgrade pip

# PyTorch 설치 (가벼운 버전)
RUN pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 \
    --extra-index-url https://download.pytorch.org/whl/cu113

# 기본 패키지들 설치
RUN pip install \
    numpy==1.21.6 \
    opencv-python==4.7.1.72 \
    librosa==0.9.2 \
    scipy==1.9.3 \
    pillow==9.5.0 \
    tqdm==4.64.1 \
    requests==2.28.2

# Wav2Lip 클론
RUN git clone https://github.com/Rudrabha/Wav2Lip.git
WORKDIR /workspace/Wav2Lip

# Wav2Lip 종속성 설치
RUN pip install -r requirements.txt

# Face detection 모델 설치
RUN pip install face-recognition dlib

# 체크포인트 디렉토리 생성
RUN mkdir -p checkpoints

# Wav2Lip GAN 모델 다운로드
RUN wget -O checkpoints/wav2lip_gan.pth \
    "https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA"

# Face detection 모델 다운로드 (대안 방법)
RUN python -c "
import urllib.request
import os
if not os.path.exists('checkpoints/wav2lip_gan.pth'):
    print('Downloading wav2lip_gan.pth from alternative source...')
    try:
        urllib.request.urlretrieve('https://github.com/justinjohn0306/Wav2Lip/releases/download/models/wav2lip_gan.pth', 'checkpoints/wav2lip_gan.pth')
        print('Download completed!')
    except:
        print('Download failed - will need manual upload')
"

# s3fd face detection 모델 다운로드
RUN mkdir -p face_detection/detection/sfd
RUN wget -O face_detection/detection/sfd/s3fd.pth \
    "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth" || \
    echo "s3fd model download failed - will try alternative"

# 대안 face detection 모델
RUN python -c "
import urllib.request
import os
if not os.path.exists('face_detection/detection/sfd/s3fd.pth'):
    print('Downloading s3fd model from alternative source...')
    try:
        urllib.request.urlretrieve('https://github.com/1adrianb/face-alignment/releases/download/v1.0/s3fd-619a316812.pth', 'face_detection/detection/sfd/s3fd.pth')
        print('s3fd download completed!')
    except:
        print('s3fd download failed')
"

# RunPod SDK 설치
RUN pip install runpod

# 작업 디렉토리를 workspace로 변경
WORKDIR /workspace

# Handler 복사
COPY handler.py /workspace/handler.py

# 실행 권한 설정
RUN chmod +x /workspace/handler.py

# 환경 변수 설정
ENV PYTHONPATH=/workspace/Wav2Lip:$PYTHONPATH

# 모델 파일 존재 확인 스크립트
RUN python -c "
import os
checkpoints = [
    '/workspace/Wav2Lip/checkpoints/wav2lip_gan.pth',
    '/workspace/Wav2Lip/face_detection/detection/sfd/s3fd.pth'
]
for checkpoint in checkpoints:
    if os.path.exists(checkpoint):
        size = os.path.getsize(checkpoint) / (1024*1024)
        print(f'✓ {checkpoint} ({size:.1f}MB)')
    else:
        print(f'✗ {checkpoint} - Missing!')
"

# 실행 명령
CMD ["python", "-u", "/workspace/handler.py"] 