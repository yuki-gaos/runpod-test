#!/usr/bin/env python3
"""
Example client for RunPod Test API
Demonstrates how to interact with the deployed serverless endpoint
"""

import json
import time
import base64
import requests
from typing import Dict, Any, Optional


class RunPodClient:
    """Client for interacting with RunPod Serverless API"""
    
    def __init__(self, endpoint_id: str, api_key: str):
        self.endpoint_id = endpoint_id
        self.api_key = api_key
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def submit_sync_request(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a synchronous request (waits for completion)"""
        url = f"{self.base_url}/runsync"
        
        payload = {
            "input": task_config
        }
        
        print(f"🚀 Submitting sync request to {url}")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    def submit_async_request(self, task_config: Dict[str, Any]) -> str:
        """Submit an asynchronous request (returns job ID)"""
        url = f"{self.base_url}/run"
        
        payload = {
            "input": task_config
        }
        
        print(f"🚀 Submitting async request to {url}")
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["id"]
    
    def check_status(self, job_id: str) -> Dict[str, Any]:
        """Check status of an async job"""
        url = f"{self.base_url}/status/{job_id}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Status check failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    def wait_for_completion(self, job_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """Wait for async job to complete"""
        print(f"⏳ Waiting for job {job_id} to complete...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.check_status(job_id)
            
            job_status = status.get("status", "unknown")
            print(f"📊 Status: {job_status}")
            
            if job_status == "COMPLETED":
                return status.get("output", {})
            elif job_status == "FAILED":
                raise Exception(f"Job failed: {status}")
            
            time.sleep(5)  # Poll every 5 seconds
        
        raise Exception(f"Job timed out after {max_wait} seconds")
    
    def download_file(self, file_info: Dict[str, Any], save_path: str) -> None:
        """Download file from base64 content"""
        content_base64 = file_info.get("content_base64")
        if not content_base64:
            raise ValueError("No base64 content found in file info")
        
        content_bytes = base64.b64decode(content_base64)
        
        with open(save_path, "wb") as f:
            f.write(content_bytes)
        
        print(f"💾 Saved file: {save_path} ({len(content_bytes)} bytes)")


def demo_sync_requests():
    """Demo synchronous requests - simple but blocks until complete"""
    print("=" * 60)
    print("🔄 SYNCHRONOUS REQUEST DEMO")
    print("=" * 60)
    
    # Note: Replace with your actual endpoint ID and API key
    client = RunPodClient(
        endpoint_id="YOUR_ENDPOINT_ID", 
        api_key="YOUR_API_KEY"
    )
    
    test_cases = [
        {
            "name": "Text Processing",
            "config": {
                "task_type": "text_processing",
                "duration": 10,
                "user_input": "Analyze this sample text for sentiment and key topics"
            }
        },
        {
            "name": "Image Generation",
            "config": {
                "task_type": "image_generation", 
                "duration": 15,
                "user_input": "A futuristic cityscape at sunset with flying cars"
            }
        },
        {
            "name": "Data Analysis",
            "config": {
                "task_type": "data_analysis",
                "duration": 8,
                "user_input": "Performance metrics for Q4 analysis"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"⏱️  Duration: {test_case['config']['duration']} seconds")
        
        start_time = time.time()
        
        try:
            result = client.submit_sync_request(test_case['config'])
            
            elapsed_time = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ Success! (took {elapsed_time:.1f}s)")
                print(f"📋 Task ID: {result['task_id']}")
                print(f"📊 Progress updates: {len(result.get('progress_updates', []))}")
                
                # Show file info
                file_info = result['result']['result']
                print(f"📄 Generated file: {file_info['filename']}")
                print(f"📦 Size: {file_info['size_bytes']} bytes")
                print(f"👀 Preview: {file_info['preview'][:100]}...")
                
                # Optionally save the file
                save_path = f"/tmp/{file_info['filename']}"
                client.download_file(file_info, save_path)
                
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
        
        print("-" * 40)


def demo_async_requests():
    """Demo asynchronous requests - submit and poll for results"""
    print("=" * 60)
    print("⚡ ASYNCHRONOUS REQUEST DEMO")
    print("=" * 60)
    
    client = RunPodClient(
        endpoint_id="YOUR_ENDPOINT_ID",
        api_key="YOUR_API_KEY" 
    )
    
    # Submit multiple jobs at once
    jobs = []
    
    for i, duration in enumerate([10, 25, 35]):
        config = {
            "task_type": "text_processing",
            "duration": duration,
            "user_input": f"Long running task #{i+1} - {duration} seconds"
        }
        
        print(f"\n🚀 Submitting job {i+1} (duration: {duration}s)")
        job_id = client.submit_async_request(config)
        jobs.append({
            "id": job_id,
            "duration": duration,
            "name": f"Job {i+1}"
        })
        print(f"📋 Job ID: {job_id}")
    
    print(f"\n⏳ Waiting for {len(jobs)} jobs to complete...")
    
    # Wait for all jobs
    for job in jobs:
        print(f"\n📊 Checking {job['name']} ({job['id']})")
        
        try:
            result = client.wait_for_completion(job['id'])
            
            if result.get('success'):
                print(f"✅ {job['name']} completed!")
                file_info = result['result']['result']
                print(f"📄 File: {file_info['filename']}")
            else:
                print(f"❌ {job['name']} failed: {result.get('error')}")
                
        except Exception as e:
            print(f"💥 {job['name']} exception: {str(e)}")


def demo_local_test():
    """Demo using the handler directly for local testing"""
    print("=" * 60)
    print("🏠 LOCAL TESTING DEMO")
    print("=" * 60)
    
    # Import the handler directly for local testing
    try:
        import sys
        sys.path.append('..')
        from src.handler import handler
        
        test_event = {
            "input": {
                "task_type": "text_processing",
                "duration": 5,  # Short for demo
                "user_input": "Quick local test"
            },
            "id": "local-test-001"
        }
        
        print("🧪 Running local handler test...")
        result = handler(test_event)
        
        print(f"📊 Result: {'SUCCESS' if result['success'] else 'FAILED'}")
        if result['success']:
            print(f"📋 Task ID: {result['task_id']}")
            print(f"⚡ Progress updates: {len(result['progress_updates'])}")
            print(f"📄 File generated: {result['result']['result']['filename']}")
        else:
            print(f"❌ Error: {result.get('error')} - {result.get('message')}")
            
    except ImportError:
        print("❌ Could not import handler - run from examples/ directory")
    except Exception as e:
        print(f"💥 Error: {str(e)}")


if __name__ == "__main__":
    print("🤖 RunPod Test API - Example Client")
    print("")
    
    # Check for credentials
    import os
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    api_key = os.getenv("RUNPOD_API_KEY")
    
    if endpoint_id and api_key:
        print("🔐 Found credentials, running live demos...")
        demo_sync_requests()
        demo_async_requests()
    else:
        print("⚠️  No credentials found (RUNPOD_ENDPOINT_ID, RUNPOD_API_KEY)")
        print("📋 Running local demo instead...")
        demo_local_test()
        
        print("\n" + "=" * 60)
        print("🚀 TO RUN LIVE DEMOS:")
        print("export RUNPOD_ENDPOINT_ID='your_endpoint_id'")
        print("export RUNPOD_API_KEY='your_api_key'")
        print("python examples/client.py")
    
    print("\n🎉 Demo complete!")