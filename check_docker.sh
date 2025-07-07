#!/bin/bash

echo "🐳 Checking Docker status..."

if docker info >/dev/null 2>&1; then
    echo "✅ Docker is running!"
    echo "🔍 Docker version: $(docker --version)"
    echo ""
    echo "🚀 Ready to build Docker image!"
    echo ""
    echo "Next step: Tell me your Docker Hub username"
    echo "Example: myusername (from hub.docker.com/u/myusername)"
else
    echo "❌ Docker is not running"
    echo "🔧 Please start Docker Desktop app"
    echo "⏳ Wait for the Docker whale icon in the menu bar"
fi 