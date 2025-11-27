@echo off
REM Script to build and push Docker images to Docker Hub (Windows)

REM Configuration
set DOCKER_USERNAME=your-dockerhub-username
set IMAGE_NAME=dots-ocr-api
set VERSION=latest

echo ================================
echo dots.ocr Docker Build ^& Push
echo ================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed
    exit /b 1
)

REM Login to Docker Hub
echo Logging into Docker Hub...
docker login

REM Build CPU image
echo Building CPU image...
docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%-cpu -f Dockerfile .

REM Build GPU image
echo Building GPU image...
docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%-gpu -f Dockerfile.gpu .

REM Tag latest
docker tag %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%-cpu %DOCKER_USERNAME%/%IMAGE_NAME%:latest

REM Push to Docker Hub
echo Pushing images to Docker Hub...
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%-cpu
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%-gpu
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:latest

echo.
echo ================================
echo Build and push completed!
echo ================================
echo.
echo Images pushed:
echo   - %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%-cpu
echo   - %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%-gpu
echo   - %DOCKER_USERNAME%/%IMAGE_NAME%:latest
echo.
echo To pull and run:
echo   docker pull %DOCKER_USERNAME%/%IMAGE_NAME%:latest
echo   docker run -p 8000:8000 %DOCKER_USERNAME%/%IMAGE_NAME%:latest

pause
