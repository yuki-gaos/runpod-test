"""
Utility functions for RunPod test application
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional
import base64


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_environment_config() -> Dict[str, Any]:
    """Get configuration from environment variables"""
    return {
        'runpod_api_key': os.environ.get('RUNPOD_API_KEY'),
        'runpod_endpoint_id': os.environ.get('RUNPOD_ENDPOINT_ID'),
        'webhook_secret': os.environ.get('WEBHOOK_SECRET'),
        'max_processing_time': int(os.environ.get('MAX_PROCESSING_TIME', '45')),
        'default_task_type': os.environ.get('DEFAULT_TASK_TYPE', 'text_processing'),
        'debug_mode': os.environ.get('DEBUG', 'false').lower() == 'true'
    }


def validate_file_size(content_base64: str, max_size_mb: int = 10) -> bool:
    """Validate that base64 encoded file is within size limits"""
    try:
        # Calculate actual file size from base64
        content_bytes = base64.b64decode(content_base64)
        size_mb = len(content_bytes) / (1024 * 1024)
        return size_mb <= max_size_mb
    except Exception:
        return False


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}m {remaining_seconds:.1f}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(remaining_minutes)}m"


def generate_file_metadata(content: str, filename: str, content_type: str) -> Dict[str, Any]:
    """Generate comprehensive file metadata"""
    content_bytes = content.encode() if isinstance(content, str) else content
    
    return {
        'filename': filename,
        'content_type': content_type,
        'size_bytes': len(content_bytes),
        'size_human': format_file_size(len(content_bytes)),
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'checksum': hash(content_bytes) % (10**10)  # Simple hash for verification
    }


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def create_error_response(error_type: str, message: str, task_id: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        'success': False,
        'error': error_type,
        'message': message,
        'task_id': task_id,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }


def create_success_response(data: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        'success': True,
        'task_id': task_id,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        **data
    }


class ProgressTracker:
    """Helper class for tracking and formatting progress updates"""
    
    def __init__(self, task_id: str, total_steps: int):
        self.task_id = task_id
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.step_times = []
    
    def next_step(self, step_name: str) -> Dict[str, Any]:
        """Advance to next step and return progress info"""
        self.current_step += 1
        current_time = time.time()
        self.step_times.append(current_time)
        
        progress_percent = int((self.current_step / self.total_steps) * 100)
        elapsed_time = current_time - self.start_time
        
        # Estimate remaining time based on average step duration
        if len(self.step_times) > 1:
            avg_step_time = elapsed_time / self.current_step
            remaining_steps = self.total_steps - self.current_step
            estimated_remaining = avg_step_time * remaining_steps
        else:
            estimated_remaining = None
        
        return {
            'task_id': self.task_id,
            'status': 'processing',
            'progress': progress_percent,
            'current_step': step_name,
            'step': self.current_step,
            'total_steps': self.total_steps,
            'elapsed_time': elapsed_time,
            'estimated_remaining': estimated_remaining,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def complete(self) -> Dict[str, Any]:
        """Mark processing as complete"""
        total_time = time.time() - self.start_time
        return {
            'task_id': self.task_id,
            'status': 'completed',
            'progress': 100,
            'total_duration': total_time,
            'total_steps': self.total_steps,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }


# Constants for validation
VALID_TASK_TYPES = ['text_processing', 'image_generation', 'data_analysis']
VALID_OUTPUT_FORMATS = ['base64', 'url', 'json']
MAX_DURATION_SECONDS = 45
MIN_DURATION_SECONDS = 5
MAX_FILE_SIZE_MB = 50