#!/bin/bash

# SadTalker vs Wav2Lip 비교 Docker 이미지 빌드 스크립트

echo "🚀 Building SadTalker vs Wav2Lip comparison Docker image..."

# Docker Hub 사용자명 (수정 필요)
DOCKER_USERNAME="your-dockerhub-username"
IMAGE_NAME="runpod-talking-head-comparison"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "📦 Image name: ${FULL_IMAGE_NAME}"

# M1/M2 Mac용 크로스 플랫폼 빌드 설정
if [[ $(uname -m) == "arm64" ]]; then
    echo "🍎 Detected Apple Silicon - using buildx for cross-platform build"
    
    # buildx 환경 확인
    docker buildx create --name mybuilder --use 2>/dev/null || true
    docker buildx inspect --bootstrap
    
    # linux/amd64 플랫폼용 빌드 및 푸시
    docker buildx build \
        --platform linux/amd64 \
        --file Dockerfile.comparison \
        --tag ${FULL_IMAGE_NAME} \
        --push \
        .
else
    echo "🐧 Building for linux/amd64 platform"
    
    # 일반 빌드
    docker build \
        --file Dockerfile.comparison \
        --tag ${FULL_IMAGE_NAME} \
        .
    
    # Docker Hub에 푸시
    echo "📤 Pushing to Docker Hub..."
    docker push ${FULL_IMAGE_NAME}
fi

if [ $? -eq 0 ]; then
    echo "✅ Docker image built and pushed successfully!"
    echo "🔗 Image URL: ${FULL_IMAGE_NAME}"
    echo ""
    echo "📝 Next steps:"
    echo "1. Go to RunPod.io → Serverless"
    echo "2. Create new template with image: ${FULL_IMAGE_NAME}"
    echo "3. Create endpoint using the template"
    echo "4. Test with the test script"
else
    echo "❌ Build failed!"
    exit 1
fi 