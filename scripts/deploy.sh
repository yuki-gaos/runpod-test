#!/bin/bash
# Deployment script for RunPod Serverless

set -e

# Configuration
IMAGE_NAME="runpod-test-api"
DEFAULT_TAG="latest"
TAG="${1:-$DEFAULT_TAG}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying to RunPod Serverless${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check if RunPod CLI is installed
if ! command -v runpod &> /dev/null; then
    echo -e "${RED}❌ RunPod CLI not found!${NC}"
    echo -e "${BLUE}Installing RunPod CLI...${NC}"
    pip install runpod
fi

# Check environment variables
if [[ -z "${RUNPOD_API_KEY}" ]]; then
    echo -e "${YELLOW}⚠️  RUNPOD_API_KEY not set.${NC}"
    echo -e "${BLUE}Please set your RunPod API key:${NC}"
    echo -e "${YELLOW}export RUNPOD_API_KEY='your_api_key_here'${NC}"
    echo ""
    echo -e "${BLUE}Get your API key from: https://www.runpod.io/console/user/settings${NC}"
    exit 1
fi

# Check Docker Hub username for image registry
if [[ -z "${DOCKER_HUB_USERNAME}" ]]; then
    echo -e "${YELLOW}⚠️  DOCKER_HUB_USERNAME not set.${NC}"
    echo -e "${BLUE}Please set your Docker Hub username:${NC}"
    echo -e "${YELLOW}export DOCKER_HUB_USERNAME='your_dockerhub_username'${NC}"
    echo ""
    echo -e "${BLUE}This is needed to push the image to a public registry for RunPod.${NC}"
    exit 1
fi

DOCKER_IMAGE="${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG}"

# Build and push image
echo -e "${BLUE}📦 Building and pushing Docker image...${NC}"
echo -e "${BLUE}Image: ${DOCKER_IMAGE}${NC}"

# Build locally first
./scripts/build.sh "${TAG}"

# Tag for Docker Hub
docker tag "${IMAGE_NAME}:${TAG}" "${DOCKER_IMAGE}"

# Push to Docker Hub
echo -e "${YELLOW}📤 Pushing to Docker Hub...${NC}"
docker push "${DOCKER_IMAGE}"

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Failed to push Docker image!${NC}"
    echo -e "${BLUE}Make sure you're logged in: ${YELLOW}docker login${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker image pushed successfully!${NC}"

# Create deployment configuration
DEPLOYMENT_CONFIG=$(cat <<EOF
{
  "name": "runpod-test-api-$(date +%Y%m%d-%H%M%S)",
  "image": "${DOCKER_IMAGE}",
  "gpu_types": "NVIDIA GeForce RTX 3070,NVIDIA GeForce RTX 3080,NVIDIA GeForce RTX 3090",
  "handler": "src.handler.handler", 
  "docker_args": "",
  "ports": "8000/http",
  "volume_in_gb": 20,
  "container_disk_in_gb": 10,
  "env": {
    "PYTHONPATH": "/app",
    "RUNPOD_DEBUG": "false"
  },
  "scaling": {
    "min_workers": 0,
    "max_workers": 3,
    "idle_timeout": 60,
    "scale_up_threshold": 2,
    "scale_down_threshold": 0
  }
}
EOF
)

echo -e "${BLUE}⚙️  Deployment Configuration:${NC}"
echo "${DEPLOYMENT_CONFIG}" | jq .

# Deploy using RunPod CLI (simulated - actual CLI commands may vary)
echo -e "${YELLOW}🚀 Deploying to RunPod...${NC}"
echo ""

# Note: The actual RunPod CLI commands may be different
# This is a demonstration of the expected workflow

cat << EOF > /tmp/runpod-deploy.json
${DEPLOYMENT_CONFIG}
EOF

echo -e "${BLUE}📋 Deployment instructions:${NC}"
echo ""
echo -e "${YELLOW}1. Go to RunPod Console: ${BLUE}https://www.runpod.io/console/serverless${NC}"
echo -e "${YELLOW}2. Click 'New Endpoint'${NC}"
echo -e "${YELLOW}3. Configure the endpoint:${NC}"
echo -e "   • ${BLUE}Container Image:${NC} ${DOCKER_IMAGE}"
echo -e "   • ${BLUE}Handler:${NC} src.handler.handler"
echo -e "   • ${BLUE}Container Disk:${NC} 10 GB"
echo -e "   • ${BLUE}GPU Types:${NC} RTX 3070/3080/3090 (or any available)"
echo -e "   • ${BLUE}Max Workers:${NC} 3"
echo -e "   • ${BLUE}Idle Timeout:${NC} 60 seconds"

echo ""
echo -e "${YELLOW}4. Environment Variables:${NC}"
echo -e "   • ${BLUE}PYTHONPATH=${NC}/app"
echo -e "   • ${BLUE}RUNPOD_DEBUG=${NC}false"

echo ""
echo -e "${YELLOW}5. Advanced Settings (optional):${NC}"
echo -e "   • ${BLUE}FlashBoot:${NC} Enable for faster cold starts"
echo -e "   • ${BLUE}Model Caching:${NC} Enable if using large models"

echo ""
echo -e "${GREEN}✅ Ready for deployment!${NC}"

echo -e "${BLUE}🧪 Test your endpoint:${NC}"
cat << 'EOF'

curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "task_type": "text_processing",
      "duration": 15,
      "user_input": "Hello RunPod!"
    }
  }'

EOF

echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "   • ${YELLOW}RunPod Docs:${NC} https://docs.runpod.io/serverless"
echo -e "   • ${YELLOW}API Reference:${NC} https://docs.runpod.io/reference"
echo -e "   • ${YELLOW}Deployment Guide:${NC} ./docs/deployment.md"

echo ""
echo -e "${GREEN}🎉 Deployment preparation complete!${NC}"