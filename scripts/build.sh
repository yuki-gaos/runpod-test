#!/bin/bash
# Build script for RunPod Test API

set -e  # Exit on any error

# Configuration
IMAGE_NAME="runpod-test-api"
TAG="${1:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔨 Building RunPod Test API Docker Image${NC}"
echo -e "${BLUE}Image: ${FULL_IMAGE_NAME}${NC}"
echo ""

# Check if we're in the right directory
if [[ ! -f "Dockerfile" ]]; then
    echo -e "${RED}❌ Error: Dockerfile not found. Run this script from the project root.${NC}"
    exit 1
fi

# Build the Docker image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build -t "${FULL_IMAGE_NAME}" .

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    
    # Show image details
    echo -e "${BLUE}📊 Image details:${NC}"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo ""
    echo -e "${BLUE}🚀 Next steps:${NC}"
    echo -e "  • Test locally: ${YELLOW}./scripts/test-local.sh${NC}"
    echo -e "  • Run with Docker Compose: ${YELLOW}docker-compose up${NC}"
    echo -e "  • Deploy to RunPod: ${YELLOW}./scripts/deploy.sh${NC}"
    
    # Optional: Push to Docker Hub if DOCKER_HUB_USERNAME is set
    if [[ -n "${DOCKER_HUB_USERNAME}" ]]; then
        echo ""
        echo -e "${YELLOW}📤 DOCKER_HUB_USERNAME is set. Push to Docker Hub? [y/N]${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
            HUB_IMAGE="${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG}"
            echo -e "${YELLOW}🔄 Tagging for Docker Hub: ${HUB_IMAGE}${NC}"
            docker tag "${FULL_IMAGE_NAME}" "${HUB_IMAGE}"
            
            echo -e "${YELLOW}📤 Pushing to Docker Hub...${NC}"
            docker push "${HUB_IMAGE}"
            
            if [[ $? -eq 0 ]]; then
                echo -e "${GREEN}✅ Successfully pushed to Docker Hub: ${HUB_IMAGE}${NC}"
                echo -e "${BLUE}You can now use this image in RunPod: ${HUB_IMAGE}${NC}"
            else
                echo -e "${RED}❌ Failed to push to Docker Hub${NC}"
                exit 1
            fi
        fi
    fi
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi