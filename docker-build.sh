#!/bin/bash
# Script to build and push Docker images to Docker Hub

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-your-dockerhub-username}"
IMAGE_NAME="dots-ocr-api"
VERSION="${VERSION:-latest}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}dots.ocr Docker Build & Push${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Login to Docker Hub
echo -e "${BLUE}Logging into Docker Hub...${NC}"
docker login

# Build CPU image
echo -e "${GREEN}Building CPU image...${NC}"
docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}-cpu -f Dockerfile .

# Build GPU image
echo -e "${GREEN}Building GPU image...${NC}"
docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}-gpu -f Dockerfile.gpu .

# Tag latest
docker tag ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}-cpu ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

# Push to Docker Hub
echo -e "${GREEN}Pushing images to Docker Hub...${NC}"
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}-cpu
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}-gpu
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Build and push completed!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Images pushed:"
echo "  - ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}-cpu"
echo "  - ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}-gpu"
echo "  - ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
echo ""
echo "To pull and run:"
echo "  docker pull ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
echo "  docker run -p 8000:8000 ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
