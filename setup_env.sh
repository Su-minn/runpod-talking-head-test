#!/bin/bash

# RunPod Serverless 환경변수 설정

echo "🔑 Setting up RunPod environment variables..."

# RunPod API Key 설정 (사용시 직접 입력)
# export RUNPOD_API_KEY="YOUR_API_KEY_HERE"
echo "⚠️  RunPod API Key를 직접 설정하세요:"
echo "export RUNPOD_API_KEY=\"YOUR_RUNPOD_API_KEY_HERE\""
echo ""
echo "💡 실제 사용할 때는 set_api_key.sh 파일을 사용하세요."

# GitHub Raw URLs 설정
export GITHUB_IMAGE_URL="https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/profile.png"
export GITHUB_AUDIO_WAV_URL="https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.wav"
export GITHUB_AUDIO_MP3_URL="https://raw.githubusercontent.com/Su-minn/runpod-talking-head-test/main/assets/test.mp3"

# Docker 이미지 정보
export DOCKER_IMAGE="smsj68/runpod-talking-head-comparison:latest"

echo "✅ Environment variables set:"
echo "🔑 RUNPOD_API_KEY: ${RUNPOD_API_KEY:0:10}..."
echo "🖼️  GITHUB_IMAGE_URL: $GITHUB_IMAGE_URL"
echo "🎵 GITHUB_AUDIO_WAV_URL: $GITHUB_AUDIO_WAV_URL"
echo "🐳 DOCKER_IMAGE: $DOCKER_IMAGE"
echo ""
echo "💡 You can now use: source setup_env.sh" 