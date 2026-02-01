# API Reference - RunPod Test API

Complete reference for the RunPod Test API endpoints and request/response formats.

## Overview

The RunPod Test API simulates long-running processes (5-45 seconds) with streaming progress updates and file generation. It supports three task types: text processing, image generation, and data analysis.

**Base URL**: `https://api.runpod.ai/v2/{endpoint_id}`

## Authentication

All requests require a Bearer token in the Authorization header:

```bash
Authorization: Bearer YOUR_RUNPOD_API_KEY
```

## Endpoints

### POST /runsync - Synchronous Processing

Submits a task and waits for completion before returning results.

#### Request

```bash
POST /runsync
Content-Type: application/json
```

```json
{
  "input": {
    "task_type": "text_processing",
    "duration": 15,
    "user_input": "Your input data here"
  }
}
```

#### Response

```json
{
  "success": true,
  "task_id": "uuid-here",
  "task_type": "text_processing",
  "duration_seconds": 15,
  "progress_updates": [
    {
      "task_id": "uuid-here",
      "status": "processing",
      "progress": 20,
      "current_step": "Loading configuration",
      "step": 2,
      "total_steps": 10,
      "elapsed_time": 3.2
    }
  ],
  "result": {
    "task_id": "uuid-here",
    "status": "completed",
    "progress": 100,
    "result": {
      "filename": "text_result_12345678.md",
      "content_type": "text/markdown",
      "size_bytes": 1247,
      "content_base64": "base64-encoded-content-here",
      "preview": "Preview of the generated content..."
    },
    "total_duration": 15.3,
    "task_type": "text_processing"
  },
  "total_steps": 10,
  "metadata": {
    "runpod_request_id": "runpod-request-id",
    "processing_complete": true,
    "file_included": true
  }
}
```

### POST /run - Asynchronous Processing

Submits a task and returns immediately with a job ID for polling.

#### Request

Same format as `/runsync`

#### Response

```json
{
  "id": "job-uuid-here",
  "status": "IN_QUEUE"
}
```

### GET /status/{job_id} - Check Job Status

Check the status of an asynchronous job.

#### Response

```json
{
  "status": "COMPLETED",
  "output": {
    // Same format as /runsync response
  }
}
```

## Request Parameters

### Input Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_type` | string | Yes | Type of processing: `text_processing`, `image_generation`, `data_analysis` |
| `duration` | integer | No | Processing time in seconds (5-45, default: 20) |
| `user_input` | string | No | Input data for processing (default: "Default test input") |
| `output_format` | string | No | Output format: `base64`, `url` (default: `base64`) |

### Task Types

#### 1. Text Processing (`text_processing`)
- Simulates NLP/LLM processing
- Generates markdown reports
- File extension: `.md`

#### 2. Image Generation (`image_generation`)  
- Simulates AI image generation
- Returns 1x1 PNG (mock)
- File extension: `.png`

#### 3. Data Analysis (`data_analysis`)
- Simulates data processing
- Generates CSV with metrics
- File extension: `.csv`

## Response Format

### Success Response

All successful responses include:

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` for success |
| `task_id` | string | Unique task identifier |
| `task_type` | string | Type of task processed |
| `duration_seconds` | integer | Requested processing duration |
| `progress_updates` | array | List of progress updates during processing |
| `result` | object | Final result with file data |
| `metadata` | object | Additional metadata |

### Progress Update Object

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Task identifier |
| `status` | string | Always "processing" during updates |
| `progress` | integer | Completion percentage (0-100) |
| `current_step` | string | Description of current step |
| `step` | integer | Current step number |
| `total_steps` | integer | Total number of steps |
| `elapsed_time` | float | Elapsed time in seconds |

### File Result Object

| Field | Type | Description |
|-------|------|-------------|
| `filename` | string | Generated filename |
| `content_type` | string | MIME type of the file |
| `size_bytes` | integer | File size in bytes |
| `content_base64` | string | Base64-encoded file content |
| `preview` | string | Text preview of the content |

### Error Response

```json
{
  "success": false,
  "error": "error_type",
  "message": "Human-readable error message",
  "task_id": null
}
```

### Error Types

| Error Type | Description |
|------------|-------------|
| `validation_error` | Invalid input parameters |
| `processing_error` | Error during task execution |
| `timeout_error` | Task exceeded time limits |
| `resource_error` | Insufficient resources |

## Example Requests

### Text Processing

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT/runsync \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "task_type": "text_processing",
      "duration": 20,
      "user_input": "Analyze sentiment of customer reviews"
    }
  }'
```

### Image Generation

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT/runsync \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "task_type": "image_generation",
      "duration": 30,
      "user_input": "A sunset over mountains with flying cars"
    }
  }'
```

### Data Analysis

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT/runsync \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "task_type": "data_analysis", 
      "duration": 25,
      "user_input": "Q4 performance metrics analysis"
    }
  }'
```

## File Handling

### Downloading Files

Files are returned as base64-encoded content. To save:

```python
import base64

file_info = response['result']['result']
content_bytes = base64.b64decode(file_info['content_base64'])

with open(file_info['filename'], 'wb') as f:
    f.write(content_bytes)
```

### File Size Limits

- Maximum file size: 50 MB
- Recommended: < 10 MB for optimal performance
- Larger files should use external storage + URLs

## Rate Limits

- **Concurrent requests**: Limited by max_workers setting
- **Request size**: 10 MB request body limit
- **Duration**: 5-45 seconds per task (enforced)

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid API key) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

## SDKs and Libraries

### Python

```python
import requests

def call_runpod_api(endpoint_id, api_key, task_config):
    url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json={"input": task_config})
    return response.json()
```

### JavaScript

```javascript
async function callRunPodAPI(endpointId, apiKey, taskConfig) {
  const response = await fetch(`https://api.runpod.ai/v2/${endpointId}/runsync`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ input: taskConfig })
  });
  
  return await response.json();
}
```

## Webhooks (Future Enhancement)

For truly asynchronous processing with real-time updates:

```json
{
  "input": {
    "task_type": "text_processing",
    "duration": 30
  },
  "webhook": {
    "url": "https://your-app.com/webhook",
    "events": ["progress", "completed", "failed"]
  }
}
```

## Best Practices

1. **Use async endpoints** for long-running tasks
2. **Implement retries** with exponential backoff
3. **Validate inputs** before sending requests
4. **Handle timeouts** gracefully
5. **Store large files** externally and return URLs
6. **Monitor costs** with request logging

## Support

- **API Issues**: Check RunPod status page
- **Documentation**: [docs.runpod.io](https://docs.runpod.io)
- **Community**: RunPod Discord server