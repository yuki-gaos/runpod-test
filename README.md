# RunPod Test Project

This repository demonstrates how to deploy a long-running Python API to RunPod using their serverless platform with Docker containers.

## Project Overview

**Goal**: Deploy a Python API that handles long-running processes (5-45 seconds) with:
- Streaming progress updates
- File transfer at completion
- Public accessibility
- Docker-based deployment to RunPod

## RunPod Platform Analysis

### Serverless vs Pods Comparison

| Feature | Serverless | Pods |
|---------|------------|------|
| **Billing** | Pay-per-second (only when running) | Per-minute (while Pod exists) |
| **Scaling** | Automatic (0 to hundreds of workers) | Manual (fixed resources) |
| **Cold Starts** | Yes (container initialization) | No (always running) |
| **Idle Costs** | $0 when not processing | Charged for entire uptime |
| **Use Cases** | Variable workloads, API endpoints | Development, training, consistent workloads |
| **Control** | Limited (containerized functions) | Full environment access |
| **Storage** | Ephemeral + optional network volumes | Container + volume + network volumes |
| **Networking** | HTTP endpoints only | SSH, HTTP, custom ports |
| **Deployment** | Docker images + handler functions | Any Docker container |

### Can They Convert to Each Other?

**Serverless → Pod**: 
✅ **YES** - Any Serverless-compatible repository can be deployed as a Pod from RunPod Hub
- Provides cost-effective option for consistent workloads
- Gains SSH access, persistent storage, custom ports

**Pod → Serverless**:
🔄 **PARTIAL** - Requires refactoring
- Pod containers must be modified to include RunPod handler functions
- Need to implement the `runpod.serverless.start()` pattern
- HTTP frameworks (Flask/FastAPI) need conversion to handler pattern

### Conversion Process

**Pod to Serverless Conversion Steps:**
1. Refactor your application to use RunPod handler functions:
   ```python
   import runpod
   
   def handler(event):
       input_data = event["input"]
       # Your existing logic here
       return result
   
   runpod.serverless.start({"handler": handler})
   ```
2. Remove persistent storage dependencies (use temp files + return URLs)
3. Ensure stateless operation (no session persistence between requests)
4. Test locally with RunPod SDK
5. Deploy to Serverless endpoint

**Serverless to Pod Conversion Steps:**
1. Take existing Docker image from Serverless
2. Deploy directly from RunPod Hub as Pod
3. Optionally: Remove handler wrapper, expose direct HTTP API
4. Configure persistent storage if needed
5. Set up custom networking/SSH access

## Our Implementation Strategy

For our **long-running API with streaming and file transfer**, **Serverless is the optimal choice** because:

✅ **Cost Efficiency**: Only pay during 5-45 second processing windows  
✅ **Auto-scaling**: Handle variable request loads automatically  
✅ **Public Access**: Built-in HTTP endpoints  
✅ **File Transfer**: Can return file URLs or base64 data  
✅ **Progress Updates**: Supported via RunPod's streaming/webhook mechanisms  

## Architecture

```
Client Request → RunPod Serverless Endpoint → Worker Instance
                                             ↓
Progress Updates ← WebSocket/Polling ← Handler Function → Processing
                                             ↓
File Result ← Public URL/Base64 ← Completed Processing
```

## Repository Structure

```
runpod-test/
├── README.md                 # This file
├── src/
│   ├── handler.py           # RunPod serverless handler
│   ├── api.py               # Core API logic (mock processing)
│   └── utils.py             # Utility functions
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Local development
├── scripts/
│   ├── build.sh            # Build and push Docker image
│   ├── deploy.sh           # Deploy to RunPod
│   └── test-local.sh       # Local testing
├── docs/
│   ├── deployment.md       # Deployment guide
│   ├── api-reference.md    # API documentation
│   └── troubleshooting.md  # Common issues
└── examples/
    ├── client.py           # Example API client
    └── test-requests.json  # Sample requests
```

## Quick Start

1. **Setup Environment**:
   ```bash
   pip install runpod docker
   ```

2. **Build Locally**:
   ```bash
   ./scripts/build.sh
   ```

3. **Test Locally**:
   ```bash
   ./scripts/test-local.sh
   ```

4. **Deploy to RunPod**:
   ```bash
   ./scripts/deploy.sh
   ```

## Next Steps

- [ ] Implement mock API with streaming progress
- [ ] Create Docker container
- [ ] Set up RunPod handler function
- [ ] Build deployment pipeline
- [ ] Test end-to-end functionality
- [ ] Document API endpoints and usage

---

*Built for testing RunPod's serverless platform capabilities*