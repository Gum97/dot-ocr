# Quick Start - Docker Deploy Script
# Hướng dẫn nhanh để build và push lên Docker Hub

Write-Host "================================" -ForegroundColor Cyan
Write-Host "dots.ocr Docker Quick Deploy" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Bước 1: Nhập Docker Hub username
Write-Host "Bước 1: Nhập Docker Hub username của bạn" -ForegroundColor Yellow
$username = Read-Host "Docker Hub username"

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "Error: Username không được để trống!" -ForegroundColor Red
    exit 1
}

# Bước 2: Login Docker Hub
Write-Host "`nBước 2: Đăng nhập Docker Hub..." -ForegroundColor Yellow
docker login

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Đăng nhập Docker Hub thất bại!" -ForegroundColor Red
    exit 1
}

# Bước 3: Chọn phiên bản
Write-Host "`nBước 3: Chọn phiên bản để build:" -ForegroundColor Yellow
Write-Host "  1. CPU only (nhẹ hơn, ~3-4GB)"
Write-Host "  2. GPU (CUDA, ~5-6GB)"
Write-Host "  3. Cả hai"
$choice = Read-Host "Chọn (1/2/3)"

$imageName = "$username/dots-ocr-api"

# Build CPU
if ($choice -eq "1" -or $choice -eq "3") {
    Write-Host "`nBuilding CPU image..." -ForegroundColor Green
    docker build -t ${imageName}:latest-cpu -f Dockerfile .
    
    if ($LASTEXITCODE -eq 0) {
        # Tag as latest
        docker tag ${imageName}:latest-cpu ${imageName}:latest
        
        # Push
        Write-Host "Pushing CPU image to Docker Hub..." -ForegroundColor Green
        docker push ${imageName}:latest-cpu
        docker push ${imageName}:latest
    }
}

# Build GPU
if ($choice -eq "2" -or $choice -eq "3") {
    Write-Host "`nBuilding GPU image..." -ForegroundColor Green
    docker build -t ${imageName}:latest-gpu -f Dockerfile.gpu .
    
    if ($LASTEXITCODE -eq 0) {
        # Push
        Write-Host "Pushing GPU image to Docker Hub..." -ForegroundColor Green
        docker push ${imageName}:latest-gpu
    }
}

Write-Host "`n================================" -ForegroundColor Green
Write-Host "Deploy hoàn tất!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Image đã được push lên Docker Hub:" -ForegroundColor Cyan

if ($choice -eq "1" -or $choice -eq "3") {
    Write-Host "  - ${imageName}:latest-cpu" -ForegroundColor White
    Write-Host "  - ${imageName}:latest" -ForegroundColor White
}

if ($choice -eq "2" -or $choice -eq "3") {
    Write-Host "  - ${imageName}:latest-gpu" -ForegroundColor White
}

Write-Host ""
Write-Host "Để sử dụng:" -ForegroundColor Yellow
Write-Host "  docker pull ${imageName}:latest" -ForegroundColor White
Write-Host "  docker run -p 8000:8000 ${imageName}:latest" -ForegroundColor White
Write-Host ""
Write-Host "Hoặc dùng docker-compose:" -ForegroundColor Yellow
Write-Host "  docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "Xem docs tại: http://localhost:8000/docs" -ForegroundColor Cyan
