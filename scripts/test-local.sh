#!/bin/bash
# Local testing script for RunPod Test API

set -e

# Configuration
IMAGE_NAME="runpod-test-api:latest"
CONTAINER_NAME="runpod-test-local"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Testing RunPod API Locally${NC}"
echo ""

# Check if image exists
if ! docker images "${IMAGE_NAME}" | grep -q "runpod-test-api"; then
    echo -e "${YELLOW}📦 Image not found. Building first...${NC}"
    ./scripts/build.sh
fi

# Stop and remove existing container if running
if docker ps -a | grep -q "${CONTAINER_NAME}"; then
    echo -e "${YELLOW}🛑 Stopping existing test container...${NC}"
    docker stop "${CONTAINER_NAME}" 2>/dev/null || true
    docker rm "${CONTAINER_NAME}" 2>/dev/null || true
fi

echo -e "${BLUE}🚀 Starting test container...${NC}"

# Run container in test mode
docker run -d \
    --name "${CONTAINER_NAME}" \
    -e RUNPOD_DEBUG=true \
    -e PYTHONPATH=/app \
    "${IMAGE_NAME}" \
    python -m src.handler test

# Wait a moment for container to start
sleep 2

# Check if container is running
if ! docker ps | grep -q "${CONTAINER_NAME}"; then
    echo -e "${RED}❌ Container failed to start!${NC}"
    echo -e "${YELLOW}📋 Container logs:${NC}"
    docker logs "${CONTAINER_NAME}"
    docker rm "${CONTAINER_NAME}" 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ Container started successfully!${NC}"

# Run test cases
echo -e "${BLUE}🔬 Running test cases...${NC}"
echo ""

# Test 1: Text Processing
echo -e "${YELLOW}📝 Test 1: Text Processing (10 seconds)${NC}"
docker exec "${CONTAINER_NAME}" python -c "
import json
import sys
sys.path.append('/app')
from src.handler import handler

event = {
    'input': {
        'task_type': 'text_processing',
        'duration': 10,
        'user_input': 'Test text processing'
    },
    'id': 'test-text-001'
}

result = handler(event)
print('Result:', 'SUCCESS' if result['success'] else 'FAILED')
print('Task ID:', result['task_id'])
print('Steps:', len(result.get('progress_updates', [])))
print('File size:', result['result']['result']['size_bytes'], 'bytes')
"

echo ""

# Test 2: Image Generation
echo -e "${YELLOW}🎨 Test 2: Image Generation (15 seconds)${NC}"
docker exec "${CONTAINER_NAME}" python -c "
import json
import sys
sys.path.append('/app')
from src.handler import handler

event = {
    'input': {
        'task_type': 'image_generation', 
        'duration': 15,
        'user_input': 'A sunset over mountains'
    },
    'id': 'test-image-001'
}

result = handler(event)
print('Result:', 'SUCCESS' if result['success'] else 'FAILED')
print('Task ID:', result['task_id'])
print('Content type:', result['result']['result']['content_type'])
print('Preview:', result['result']['result']['preview'][:50] + '...')
"

echo ""

# Test 3: Data Analysis
echo -e "${YELLOW}📊 Test 3: Data Analysis (8 seconds)${NC}"
docker exec "${CONTAINER_NAME}" python -c "
import json
import sys
sys.path.append('/app')
from src.handler import handler

event = {
    'input': {
        'task_type': 'data_analysis',
        'duration': 8,
        'user_input': 'Analyze performance metrics'
    },
    'id': 'test-data-001'
}

result = handler(event)
print('Result:', 'SUCCESS' if result['success'] else 'FAILED') 
print('Task ID:', result['task_id'])
print('Filename:', result['result']['result']['filename'])
print('CSV preview:', result['result']['result']['preview'])
"

echo ""

# Test 4: Error Handling
echo -e "${YELLOW}❌ Test 4: Error Handling (invalid input)${NC}"
docker exec "${CONTAINER_NAME}" python -c "
import json
import sys
sys.path.append('/app')
from src.handler import handler

event = {
    'input': {
        'task_type': 'invalid_type',
        'duration': 100,  # Too long
    },
    'id': 'test-error-001'
}

result = handler(event)
print('Result:', 'FAILED (expected)' if not result['success'] else 'UNEXPECTED SUCCESS')
print('Error:', result.get('error', 'None'))
print('Message:', result.get('message', 'None'))
"

echo ""

# Show container logs
echo -e "${BLUE}📋 Container logs (last 20 lines):${NC}"
docker logs --tail 20 "${CONTAINER_NAME}"

# Cleanup
echo ""
echo -e "${YELLOW}🧹 Cleaning up test container...${NC}"
docker stop "${CONTAINER_NAME}"
docker rm "${CONTAINER_NAME}"

echo -e "${GREEN}✅ Local testing complete!${NC}"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo -e "  • Deploy to RunPod: ${YELLOW}./scripts/deploy.sh${NC}"
echo -e "  • Run full integration: ${YELLOW}docker-compose up${NC}"