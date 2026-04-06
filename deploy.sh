#!/bin/bash

# --- CONFIG ---
APP_NAME="Senior AI Agent Production"
COMPOSE_FILE="docker-compose.prod.yml"

echo "----------------------------------------------------------"
echo "🚀 Starting Deployment: $APP_NAME"
echo "----------------------------------------------------------"

# 1. Cập nhật mã nguồn mới nhất từ GitHub
echo "📥 Step 1: Pulling latest code from GitHub..."
git pull origin main

# 2. Kiểm tra xem file .env đã tồn tại chưa
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found! Please create it before deploying."
    exit 1
fi

# 3. Khởi chạy hệ thống bằng Docker Compose
echo "🏗️  Step 2: Building and starting containers..."
docker compose -f $COMPOSE_FILE up -d --build

# 4. Dọn dẹp các Docker image cũ/thừa để tiết kiệm ổ cứng (quan trọng cho VPS 20GB)
echo "🧹 Step 3: Cleaning up old Docker images..."
docker image prune -f

echo "----------------------------------------------------------"
echo "✅ Deployment Successful!"
echo "🌐 Access your app at: http://e1.chiasegpu.vn:3001"
echo "----------------------------------------------------------"
