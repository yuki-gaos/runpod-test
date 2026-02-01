"""
Core API Logic - Mock Long-Running Process
Simulates 5-45 second processing with progress updates and file output
"""

import time
import json
import base64
import uuid
import os
from io import StringIO
from typing import Dict, Any, Generator, Optional


class MockProcessor:
    """Simulates a long-running AI/ML process with progress tracking"""
    
    def __init__(self, task_config: Dict[str, Any]):
        self.task_id = str(uuid.uuid4())
        self.task_config = task_config
        self.duration = task_config.get('duration', 20)  # Default 20 seconds
        self.output_format = task_config.get('output_format', 'text')
        self.progress = 0
        self.status = 'pending'
        self.result = None
        
        # Simulate different task types
        self.task_type = task_config.get('task_type', 'text_processing')
        self.steps = self._generate_processing_steps()
    
    def _generate_processing_steps(self) -> list:
        """Generate realistic processing steps based on task type"""
        base_steps = [
            "Initializing environment",
            "Loading configuration", 
            "Validating input data",
        ]
        
        if self.task_type == 'text_processing':
            base_steps.extend([
                "Tokenizing text",
                "Running language model",
                "Processing embeddings",
                "Generating response",
                "Formatting output"
            ])
        elif self.task_type == 'image_generation':
            base_steps.extend([
                "Loading diffusion model",
                "Encoding prompt",
                "Running diffusion steps", 
                "Decoding latents",
                "Post-processing image"
            ])
        elif self.task_type == 'data_analysis':
            base_steps.extend([
                "Loading dataset",
                "Feature engineering",
                "Running analysis",
                "Computing statistics",
                "Generating report"
            ])
        
        base_steps.extend([
            "Finalizing results",
            "Preparing output file",
            "Cleanup and completion"
        ])
        
        return base_steps
    
    def process(self) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
        """
        Main processing function that yields progress updates
        and returns final result with file
        """
        self.status = 'running'
        total_steps = len(self.steps)
        step_duration = self.duration / total_steps
        
        for i, step in enumerate(self.steps):
            # Simulate variable step duration (some steps take longer)
            if 'model' in step.lower() or 'diffusion' in step.lower():
                time.sleep(step_duration * 2)  # Model loading takes longer
            else:
                time.sleep(step_duration * 0.8)
            
            self.progress = int((i + 1) / total_steps * 100)
            
            # Yield progress update
            yield {
                'task_id': self.task_id,
                'status': 'processing',
                'progress': self.progress,
                'current_step': step,
                'step': i + 1,
                'total_steps': total_steps,
                'elapsed_time': (i + 1) * step_duration
            }
        
        # Generate final result and file
        self.status = 'completed'
        result_data = self._generate_result_file()
        
        return {
            'task_id': self.task_id,
            'status': 'completed', 
            'progress': 100,
            'result': result_data,
            'total_duration': self.duration,
            'task_type': self.task_type
        }
    
    def _generate_result_file(self) -> Dict[str, Any]:
        """Generate mock result file based on task type"""
        
        if self.task_type == 'text_processing':
            # Generate a mock text processing result
            content = f"""
# Text Processing Results - Task {self.task_id}

## Input Configuration
- Duration: {self.duration} seconds
- Task Type: {self.task_type}
- Processing Steps: {len(self.steps)}

## Processing Summary
Successfully processed input text using advanced language model.

## Generated Output
Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco.

## Statistics
- Tokens processed: 1,247
- Model confidence: 94.7%
- Processing time: {self.duration:.2f}s

## Metadata
Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
Task ID: {self.task_id}
            """.strip()
            
            return {
                'filename': f'text_result_{self.task_id[:8]}.md',
                'content_type': 'text/markdown',
                'size_bytes': len(content.encode()),
                'content_base64': base64.b64encode(content.encode()).decode(),
                'preview': content[:200] + '...' if len(content) > 200 else content
            }
            
        elif self.task_type == 'image_generation':
            # Mock image data (1x1 PNG)
            fake_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
            
            return {
                'filename': f'generated_image_{self.task_id[:8]}.png',
                'content_type': 'image/png', 
                'size_bytes': len(fake_png),
                'content_base64': base64.b64encode(fake_png).decode(),
                'preview': f'Generated {1024}x{1024} image with prompt from task {self.task_id[:8]}'
            }
            
        elif self.task_type == 'data_analysis':
            # Mock CSV data
            csv_content = f"""timestamp,metric,value,category
{time.strftime('%Y-%m-%d %H:%M:%S')},accuracy,0.947,model_performance
{time.strftime('%Y-%m-%d %H:%M:%S')},precision,0.923,model_performance  
{time.strftime('%Y-%m-%d %H:%M:%S')},recall,0.891,model_performance
{time.strftime('%Y-%m-%d %H:%M:%S')},f1_score,0.906,model_performance
{time.strftime('%Y-%m-%d %H:%M:%S')},processing_time,{self.duration:.2f},timing
{time.strftime('%Y-%m-%d %H:%M:%S')},memory_usage,2.1,resources"""
            
            return {
                'filename': f'analysis_results_{self.task_id[:8]}.csv',
                'content_type': 'text/csv',
                'size_bytes': len(csv_content.encode()),
                'content_base64': base64.b64encode(csv_content.encode()).decode(),
                'preview': 'Analysis complete. CSV contains 6 metrics including performance and resource usage.'
            }
        
        # Default fallback
        return {
            'filename': f'result_{self.task_id[:8]}.txt',
            'content_type': 'text/plain',
            'size_bytes': 50,
            'content_base64': base64.b64encode(f'Task {self.task_id} completed successfully!'.encode()).decode(),
            'preview': 'Basic task completion result'
        }


def validate_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Validate incoming request and extract configuration"""
    input_data = event.get('input', {})
    
    # Validate required fields
    if not isinstance(input_data, dict):
        raise ValueError("Input must be a dictionary")
    
    # Extract and validate configuration
    config = {
        'task_type': input_data.get('task_type', 'text_processing'),
        'duration': min(max(input_data.get('duration', 20), 5), 45),  # Clamp 5-45 seconds
        'output_format': input_data.get('output_format', 'base64'),
        'user_input': input_data.get('user_input', 'Default test input'),
    }
    
    # Validate task type
    valid_types = ['text_processing', 'image_generation', 'data_analysis']
    if config['task_type'] not in valid_types:
        raise ValueError(f"task_type must be one of: {valid_types}")
    
    return config