"""
RunPod Serverless Handler
Handles requests from RunPod serverless endpoints and manages long-running processes
"""

import runpod
import json
import asyncio
import logging
import sys
import os
from typing import Dict, Any, Optional
from src.api import MockProcessor, validate_request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main RunPod serverless handler function
    
    Handles incoming requests and manages the long-running process
    with progress updates and file generation.
    """
    try:
        logger.info(f"Received request: {json.dumps(event, indent=2)}")
        
        # Validate input
        config = validate_request(event)
        logger.info(f"Validated config: {config}")
        
        # Initialize processor
        processor = MockProcessor(config)
        logger.info(f"Initialized processor for task: {processor.task_id}")
        
        # Track progress updates for return
        progress_updates = []
        final_result = None
        
        # Process with progress tracking
        logger.info("Starting processing...")
        for progress_update in processor.process():
            progress_updates.append(progress_update)
            
            # Log significant milestones
            if progress_update.get('progress', 0) % 20 == 0:
                logger.info(f"Progress: {progress_update['progress']}% - {progress_update.get('current_step', 'Unknown')}")
        
        # The final iteration returns the complete result
        final_result = progress_update
        logger.info(f"Processing completed for task: {processor.task_id}")
        
        # Prepare response with all progress data + final result
        response = {
            'success': True,
            'task_id': processor.task_id,
            'task_type': config['task_type'],
            'duration_seconds': config['duration'],
            'progress_updates': progress_updates[:-1],  # Exclude final result from progress
            'result': final_result,
            'total_steps': len(progress_updates),
            'metadata': {
                'runpod_request_id': event.get('id', 'unknown'),
                'processing_complete': True,
                'file_included': True
            }
        }
        
        logger.info(f"Returning response with {len(progress_updates)} progress updates")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            'success': False,
            'error': 'validation_error',
            'message': str(e),
            'task_id': None
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'success': False,
            'error': 'processing_error', 
            'message': f"An unexpected error occurred: {str(e)}",
            'task_id': getattr(processor, 'task_id', None) if 'processor' in locals() else None
        }


def health_check() -> Dict[str, Any]:
    """Health check endpoint for RunPod"""
    return {
        'status': 'healthy',
        'service': 'runpod-test-api',
        'version': '1.0.0',
        'capabilities': [
            'text_processing',
            'image_generation', 
            'data_analysis'
        ],
        'limits': {
            'min_duration': 5,
            'max_duration': 45,
            'supported_formats': ['base64', 'url']
        }
    }


# Advanced handler with webhook support (for production use)
def handler_with_webhook(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced handler that supports webhooks for real-time progress updates
    This would be used in production for truly async processing
    """
    try:
        config = validate_request(event)
        webhook_url = event.get('webhook', {}).get('url')
        
        if webhook_url:
            # For webhook mode, return immediately and process async
            processor = MockProcessor(config)
            
            # In a real implementation, this would:
            # 1. Start processing in background
            # 2. Send progress updates to webhook URL  
            # 3. Send final result to webhook URL
            # 4. Return task_id for tracking
            
            return {
                'success': True,
                'task_id': processor.task_id,
                'status': 'accepted',
                'message': 'Task queued for processing. Progress updates will be sent to webhook.',
                'webhook_url': webhook_url,
                'estimated_duration': config['duration']
            }
        else:
            # Fallback to synchronous processing
            return handler(event)
            
    except Exception as e:
        logger.error(f"Webhook handler error: {str(e)}")
        return {
            'success': False,
            'error': 'webhook_error',
            'message': str(e)
        }


if __name__ == "__main__":
    # Debug startup
    print("🚀 Handler module starting...")
    print(f"Python path: {sys.path}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        print("📦 Testing imports...")
        import runpod
        print(f"✅ runpod version: {runpod.__version__}")
        
        from src.api import MockProcessor, validate_request
        print("✅ src.api imported successfully")
        
        print("🔧 Testing handler function...")
        test_result = health_check()
        print(f"✅ Health check: {test_result['status']}")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # For local testing
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Local test mode
        test_event = {
            'input': {
                'task_type': 'text_processing',
                'duration': 10,
                'user_input': 'Test processing task'
            },
            'id': 'test-request-123'
        }
        
        print("Running local test...")
        result = handler(test_event)
        print(json.dumps(result, indent=2))
    else:
        # Production mode - start RunPod serverless
        print("🎯 Starting RunPod serverless handler...")
        try:
            runpod.serverless.start({
                "handler": handler,
                "return_aggregate_stream": True  # Enable streaming responses
            })
        except Exception as e:
            print(f"❌ RunPod start error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)