FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu20.04

# 환경 변수 설정
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64

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
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    wget \
    curl \
    unzip \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 심볼릭 링크 생성
RUN ln -s /usr/bin/python3.9 /usr/bin/python

# 작업 디렉토리 설정
WORKDIR /workspace

# pip 업그레이드
RUN python -m pip install --upgrade pip

# PyTorch 및 기본 패키지 설치
RUN pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 \
    --extra-index-url https://download.pytorch.org/whl/cu113

# 기본 패키지들 설치
RUN pip install \
    numpy==1.21.6 \
    opencv-python==4.7.1.72 \
    scikit-image==0.19.3 \
    scipy==1.9.3 \
    imageio==2.25.1 \
    imageio-ffmpeg==0.4.8 \
    librosa==0.9.2 \
    numba==0.56.4 \
    resampy==0.4.2 \
    pillow==9.5.0 \
    tqdm==4.64.1 \
    yacs==0.1.8 \
    pyyaml==6.0 \
    face-alignment==1.3.5 \
    requests==2.28.2

# SadTalker 클론
RUN git clone https://github.com/OpenTalker/SadTalker.git
WORKDIR /workspace/SadTalker

# SadTalker 종속성 설치
RUN pip install -r requirements.txt

# 추가 필요 패키지 설치
RUN pip install \
    gfpgan==1.3.8 \
    basicsr==1.4.2 \
    facexlib==0.3.0 \
    realesrgan==0.3.0

# 체크포인트 디렉토리 생성
RUN mkdir -p checkpoints

# SadTalker 메인 체크포인트 다운로드
RUN wget -O checkpoints/SadTalker_V0.0.2_256.safetensors \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors" || \
    wget -O checkpoints/SadTalker_V0.0.2_256.safetensors \
    "https://huggingface.co/vinthony/SadTalker/resolve/main/SadTalker_V0.0.2_256.safetensors"

# SadTalker 512 체크포인트 다운로드 (고해상도용)
RUN wget -O checkpoints/SadTalker_V0.0.2_512.safetensors \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors" || \
    wget -O checkpoints/SadTalker_V0.0.2_512.safetensors \
    "https://huggingface.co/vinthony/SadTalker/resolve/main/SadTalker_V0.0.2_512.safetensors"

# GFPGAN 관련 디렉토리 및 모델 다운로드
RUN mkdir -p gfpgan/weights
RUN wget -O gfpgan/weights/GFPGANv1.4.pth \
    "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth"

# 추가 얼굴 인식 모델 다운로드
RUN mkdir -p checkpoints/shape_predictor
RUN wget -O checkpoints/shape_predictor_68_face_landmarks.dat.bz2 \
    "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
RUN cd checkpoints && bunzip2 shape_predictor_68_face_landmarks.dat.bz2

# BFM 모델 다운로드
RUN mkdir -p checkpoints/BFM_Fitting
RUN wget -O checkpoints/BFM_Fitting/01_MorphableModel.mat \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/01_MorphableModel.mat"
RUN wget -O checkpoints/BFM_Fitting/BFM_model_front.mat \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/BFM_model_front.mat"
RUN wget -O checkpoints/BFM_Fitting/Exp_Pca.bin \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/Exp_Pca.bin"
RUN wget -O checkpoints/BFM_Fitting/facemodel_info.mat \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/facemodel_info.mat"
RUN wget -O checkpoints/BFM_Fitting/select_vertex_id.mat \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/select_vertex_id.mat"
RUN wget -O checkpoints/BFM_Fitting/std_exp.txt \
    "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/std_exp.txt"

# RunPod SDK 설치
RUN pip install runpod

# 작업 디렉토리를 workspace로 변경
WORKDIR /workspace

# Handler 복사
COPY handler.py /workspace/handler.py

# 실행 권한 설정
RUN chmod +x /workspace/handler.py

# 환경 변수 설정
ENV PYTHONPATH=/workspace/SadTalker:$PYTHONPATH

# 실행 명령
CMD ["python", "-u", "/workspace/handler.py"] 