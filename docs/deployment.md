# Deployment Guide - RunPod Test API

This guide walks through deploying the RunPod Test API to RunPod's serverless platform.

## Prerequisites

1. **RunPod Account**: Sign up at [runpod.io](https://www.runpod.io)
2. **Docker Hub Account**: For hosting the container image
3. **API Key**: Get from RunPod Console → User Settings
4. **Local Environment**:
   ```bash
   pip install runpod docker
   ```

## Quick Deployment

### 1. Set Environment Variables

```bash
export RUNPOD_API_KEY='your_api_key_here'
export DOCKER_HUB_USERNAME='your_dockerhub_username'
```

### 2. Build and Deploy

```bash
# Build Docker image and push to Docker Hub
./scripts/build.sh

# Deploy to RunPod (creates deployment instructions)
./scripts/deploy.sh
```

### 3. Create Endpoint in RunPod Console

1. Go to [RunPod Console → Serverless](https://www.runpod.io/console/serverless)
2. Click **"New Endpoint"**
3. Configure as shown by the deploy script:

   | Setting | Value |
   |---------|-------|
   | Container Image | `yourusername/runpod-test-api:latest` |
   | Handler | `src.handler.handler` |
   | Container Disk | 10 GB |
   | GPU Types | RTX 3070/3080/3090 (or available) |
   | Min Workers | 0 |
   | Max Workers | 3 |
   | Idle Timeout | 60 seconds |

4. **Environment Variables**:
   ```
   PYTHONPATH=/app
   RUNPOD_DEBUG=false
   ```

5. Click **"Deploy"**

## Advanced Configuration

### GPU Selection

For optimal cost/performance:

- **Development/Testing**: RTX 3070, RTX 4060
- **Production**: RTX 3080, RTX 3090
- **High Throughput**: A40, A100

### Scaling Configuration

```json
{
  "min_workers": 0,           // No idle costs
  "max_workers": 5,           // Scale up to 5 workers
  "idle_timeout": 60,         // Workers shut down after 60s
  "scale_up_threshold": 2,    // Scale up when 2+ requests queued
  "scale_down_threshold": 0   // Scale down when idle
}
```

### Performance Optimizations

1. **Enable FlashBoot**: Faster cold starts
2. **Model Caching**: If using large ML models
3. **Network Volumes**: For persistent data (optional)

## Testing Your Deployment

### 1. Health Check

```bash
curl -X GET https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/health \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 2. Simple Test

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "task_type": "text_processing",
      "duration": 10,
      "user_input": "Hello RunPod!"
    }
  }'
```

### 3. Using the Example Client

```bash
export RUNPOD_ENDPOINT_ID='your_endpoint_id'
export RUNPOD_API_KEY='your_api_key'
python examples/client.py
```

## Monitoring and Logs

### RunPod Console
- **Logs**: Real-time logs in the endpoint dashboard
- **Metrics**: Request count, duration, errors
- **Scaling**: Active workers, queue length

### Log Levels
```python
# In your code
import logging
logging.getLogger('runpod').setLevel(logging.INFO)
```

## Cost Optimization

### Billing Model
- **Pay per second** of actual compute time
- **No charges** when workers are idle
- **No ingress/egress** fees

### Best Practices
1. **Optimize cold start time**: Keep Docker image small
2. **Right-size workers**: Match GPU to workload needs
3. **Set appropriate timeouts**: Avoid stuck workers
4. **Use async endpoints**: For better queuing efficiency

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check image exists on Docker Hub
docker pull yourusername/runpod-test-api:latest

# Test locally first
./scripts/test-local.sh
```

#### 2. Handler Import Error
- Ensure `PYTHONPATH=/app` in environment
- Check handler path: `src.handler.handler`

#### 3. Long Cold Starts
- Enable FlashBoot in endpoint settings
- Reduce Docker image size
- Consider keeping min_workers > 0 for production

#### 4. Timeout Errors
- Check if duration exceeds endpoint timeout
- Verify GPU type can handle the workload
- Monitor memory usage

### Debugging Steps

1. **Check Logs**: RunPod Console → Endpoint → Logs
2. **Test Locally**: Use `docker-compose up` for local testing
3. **Validate Image**: Ensure Docker image runs without issues
4. **Check Resources**: Verify GPU memory and disk space

## Production Checklist

- [ ] Image tested locally and in staging
- [ ] Environment variables configured
- [ ] Scaling policies set appropriately
- [ ] Monitoring and alerting configured
- [ ] Error handling and retries implemented
- [ ] Documentation updated
- [ ] Security review completed

## API Reference

See [api-reference.md](./api-reference.md) for detailed API documentation.

## Support

- **RunPod Docs**: [docs.runpod.io](https://docs.runpod.io)
- **Community**: [RunPod Discord](https://discord.gg/runpod)
- **Support**: [support@runpod.io](mailto:support@runpod.io)