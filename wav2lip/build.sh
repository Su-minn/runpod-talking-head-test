#!/bin/bash

# Wav2Lip Docker 빌드 및 푸시 스크립트

set -e

# 설정
DOCKER_USERNAME="your-dockerhub-username"  # 실제 Docker Hub 사용자명으로 변경
IMAGE_NAME="wav2lip-runpod"
VERSION="v1.0"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

echo "=== Wav2Lip Docker 이미지 빌드 시작 ==="
echo "이미지명: ${FULL_IMAGE_NAME}"

# Docker Hub 로그인 확인
echo "Docker Hub 로그인 상태 확인..."
docker info | grep Username || {
    echo "Docker Hub에 로그인이 필요합니다:"
    echo "docker login"
    exit 1
}

# Docker 빌드 (M1 Mac용 크로스 플랫폼 빌드)
echo "Docker 이미지 빌드 중..."
if [[ $(uname -m) == "arm64" ]]; then
    echo "M1/M2 Mac 감지됨 - linux/amd64 플랫폼으로 빌드"
    docker buildx build --platform linux/amd64 -t ${FULL_IMAGE_NAME} .
else
    echo "x86_64 플랫폼에서 빌드"
    docker build -t ${FULL_IMAGE_NAME} .
fi

echo "빌드 완료!"

# 이미지 크기 확인
echo "이미지 크기:"
docker images | grep ${IMAGE_NAME}

# Docker Hub에 푸시
echo "Docker Hub에 푸시 중..."
docker push ${FULL_IMAGE_NAME}

echo "=== 빌드 및 푸시 완료 ==="
echo "RunPod에서 사용할 이미지: ${FULL_IMAGE_NAME}"
echo ""
echo "RunPod 설정 정보:"
echo "- Container Image: ${FULL_IMAGE_NAME}"
echo "- GPU: 16GB VRAM (RTX 4080 이상)"
echo "- Active Workers: 0 (비용 절약)"
echo "- Max Workers: 1"
echo "- Idle Timeout: 5초"
echo "- Execution Timeout: 600초 (10분)" 