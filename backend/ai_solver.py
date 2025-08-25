#!/usr/bin/env python3
"""
COMPLETE AI SOLVER - Claude API Automation with All Original Features
Features:
- Complete 1300+ line implementation with all original functionality
- Claude Sonnet 4 model (claude-sonnet-4-20250514)
- Clean Review-tab style interface to check images
- Claude API automation with vision capabilities
- Direct images folder usage (no Review integration)
- View Solutions modal with detailed formatting
- Export capabilities (JSON, CSV)
- Comprehensive error handling and debugging
- Progress tracking and statistics
- Quality control and flagging system
- Modular architecture ready
"""

import os
import sys
import json
import base64
import asyncio
import aiofiles
from pathlib import Path
from datetime import datetime
import traceback
import re
import csv
import io
from flask import Flask, request, jsonify, send_from_directory, send_file
import anthropic
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from PIL import Image

# ==================== CONFIGURATION ====================
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
QUESTION_BANKS_DIR = Path('./question_banks')
CLAUDE_API_MODEL = "claude-sonnet-4-20250514"  # ✅ UPDATED TO CLAUDE SONNET 4!
CLAUDE_API_MAX_TOKENS = 4000
CONFIDENCE_THRESHOLD = 0.85
QUALITY_THRESHOLD_DISPLAY = "85%"
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5005

# ==================== TEMPLATES ====================
def get_claude_prompt_template(subject: str, question_number: int) -> str:
    """Get the Claude prompt template - optimized for Claude Sonnet 4"""
    return f"""You are an expert {subject} tutor using Claude Sonnet 4, analyzing a multiple-choice question image. Please provide a comprehensive analysis in the following JSON format:

{{
    "question_text": "Full transcription of the question text",
    "options": {{
        "A": "Option A text",
        "B": "Option B text", 
        "C": "Option C text",
        "D": "Option D text"
    }},
    "correct_answer": "A",
    "simple_answer": "Brief explanation of why this answer is correct",
    "detailed_explanation": {{
        "reasoning": "Step-by-step logical reasoning",
        "key_concepts": "Main physics concepts involved",
        "common_mistakes": "What students often get wrong"
    }},
    "calculation_steps": [
        "Step 1: Identify given values",
        "Step 2: Apply relevant formula", 
        "Step 3: Calculate result"
    ],
    "topic": "Specific physics topic (e.g., Mechanics, Thermodynamics)",
    "difficulty": "easy/medium/hard",
    "confidence_score": 0.95
}}

Important guidelines for Claude Sonnet 4:
- Read the question image carefully and transcribe all text accurately
- Identify all answer options (A, B, C, D)
- Provide the correct answer with high confidence
- Give detailed explanations suitable for A-level physics
- Aim for 95%+ confidence to meet quality standards
- If calculations are needed, show all steps clearly
- If unsure about any aspect, indicate lower confidence score
- Use Claude Sonnet 4's enhanced reasoning capabilities
- Leverage improved instruction following and accuracy

Question {question_number} Analysis:"""

def get_css_styles() -> str:
    """Get comprehensive CSS styles for the interface"""
    return """
        * { 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
        }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333; 
            min-height: 100vh;
        }
        
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 2rem; 
        }
        
        .header { 
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
            color: white; 
            padding: 2rem; 
            border-radius: 15px; 
            text-align: center; 
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3);
        }
        
        .header h1 { 
            font-size: 2.5rem; 
            margin-bottom: 0.5rem; 
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header p { 
            opacity: 0.9; 
            font-size: 1.1rem; 
            margin: 0.5rem 0;
        }
        
        .status-section { 
            background: rgba(255, 255, 255, 0.95); 
            border-radius: 15px; 
            padding: 2rem; 
            margin-bottom: 2rem; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .status-info { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 1.5rem; 
            margin-bottom: 2rem; 
        }
        
        .status-card { 
            background: linear-gradient(135deg, #f8f9ff 0%, #e8f0fe 100%);
            padding: 1.5rem; 
            border-radius: 12px; 
            text-align: center;
            border: 1px solid rgba(79, 172, 254, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .status-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(79, 172, 254, 0.2);
        }
        
        .status-card h4 { 
            color: #6366f1; 
            margin-bottom: 0.5rem; 
            font-size: 0.9rem; 
            text-transform: uppercase; 
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        .status-card div { 
            font-size: 2.2rem; 
            font-weight: bold; 
            color: #1e293b; 
        }
        
        .automation-controls { 
            display: flex; 
            gap: 1rem; 
            flex-wrap: wrap; 
            justify-content: center;
        }
        
        .btn { 
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); 
            color: white; 
            border: none; 
            padding: 0.875rem 1.75rem; 
            border-radius: 10px; 
            font-weight: 600; 
            cursor: pointer; 
            transition: all 0.3s ease; 
            text-decoration: none; 
            display: inline-block;
            font-size: 0.95rem;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }
        
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-preview { 
            background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        }
        
        .btn-preview:hover {
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
        }
        
        .btn-check { 
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
        }
        
        .btn-check:hover {
            box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
        }
        
        .btn-automate { 
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); 
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
        }
        
        .btn-automate:hover {
            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
        }
        
        .btn-solutions { 
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); 
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
        }
        
        .btn-solutions:hover {
            box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4);
        }
        
        .process-section { 
            background: rgba(255, 255, 255, 0.95); 
            border-radius: 15px; 
            padding: 2rem; 
            margin-bottom: 2rem; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .process-section h3 {
            color: #1e293b;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }
        
        .process-steps { 
            padding-left: 2rem; 
        }
        
        .process-steps li { 
            margin-bottom: 1rem; 
            line-height: 1.6;
            color: #475569;
        }
        
        .process-steps strong {
            color: #1e293b;
        }
        
        .images-section { 
            background: rgba(255, 255, 255, 0.95); 
            border-radius: 15px; 
            padding: 2rem; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .images-section h3 {
            color: #1e293b;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }
        
        .images-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
            gap: 1.5rem; 
            margin-top: 1.5rem; 
        }
        
        .image-card { 
            border: 1px solid rgba(226, 232, 240, 0.8); 
            border-radius: 12px; 
            overflow: hidden; 
            transition: all 0.3s ease;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .image-card:hover { 
            transform: translateY(-4px); 
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border-color: #6366f1;
        }
        
        .image-header { 
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
            padding: 1rem 1.5rem; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }
        
        .image-header h4 { 
            margin: 0; 
            color: #1e293b;
            font-weight: 600;
        }
        
        .status-badge { 
            padding: 0.375rem 0.75rem; 
            border-radius: 6px; 
            font-size: 0.8rem; 
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-solved { 
            background: #dcfce7; 
            color: #166534; 
            border: 1px solid #bbf7d0;
        }
        
        .status-review { 
            background: #fef3c7; 
            color: #92400e; 
            border: 1px solid #fde68a;
        }
        
        .status-pending { 
            background: #fecaca; 
            color: #991b1b; 
            border: 1px solid #fca5a5;
        }
        
        .image-preview { 
            width: 100%; 
            height: 220px; 
            object-fit: contain; 
            background: #f8fafc; 
            cursor: pointer;
            transition: opacity 0.3s ease;
        }
        
        .image-preview:hover {
            opacity: 0.9;
        }
        
        .image-info { 
            padding: 1.5rem; 
        }
        
        .image-info p { 
            margin-bottom: 0.75rem; 
            font-size: 0.9rem; 
            color: #64748b; 
            line-height: 1.4;
        }
        
        .image-info strong {
            color: #374151;
        }
        
        .notification { 
            position: fixed; 
            top: 2rem; 
            right: 2rem; 
            padding: 1rem 1.5rem; 
            border-radius: 10px; 
            color: white; 
            font-weight: 600; 
            z-index: 1000; 
            transform: translateX(400px); 
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            max-width: 400px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }
        
        .notification.show { 
            transform: translateX(0); 
        }
        
        .notification.success { 
            background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
        }
        
        .notification.error { 
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); 
        }
        
        .notification.info { 
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
        }
        
        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.6);
            backdrop-filter: blur(4px);
        }
        
        .modal-content {
            background-color: #ffffff;
            margin: 2% auto;
            padding: 0;
            border-radius: 16px;
            width: 92%;
            max-width: 1200px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: modalSlideIn 0.3s ease-out;
        }
        
        @keyframes modalSlideIn {
            from {
                opacity: 0;
                transform: scale(0.9) translateY(-20px);
            }
            to {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }
        
        .modal-header {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 2rem 2.5rem;
            border-radius: 16px 16px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-header h2 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .close {
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
            opacity: 0.8;
            transition: opacity 0.3s ease;
        }
        
        .close:hover {
            opacity: 1;
        }
        
        .modal-body {
            padding: 2.5rem;
        }
        
        .solutions-toolbar {
            display: flex;
            gap: 1rem;
            margin-bottom: 2.5rem;
            flex-wrap: wrap;
            padding: 1.5rem;
            background: #f8fafc;
            border-radius: 12px;
        }
        
        .btn-small {
            padding: 0.625rem 1.25rem;
            font-size: 0.875rem;
            border-radius: 8px;
        }
        
        .solutions-summary {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border: 1px solid #e2e8f0;
        }
        
        .solutions-summary h3 {
            color: #1e293b;
            margin-bottom: 1rem;
            font-size: 1.4rem;
        }
        
        .solutions-summary p {
            margin-bottom: 0.5rem;
            color: #475569;
            line-height: 1.5;
        }
        
        .solution-item {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            margin-bottom: 2rem;
            overflow: hidden;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .solution-item:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-color: #6366f1;
        }
        
        .solution-header {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 1.5rem 2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .solution-header h4 {
            margin: 0;
            flex: 1;
            color: #1e293b;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .confidence-badge {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 0.375rem 0.75rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .solution-section {
            padding: 1.5rem 2rem;
            border-top: 1px solid #f1f5f9;
        }
        
        .solution-section:first-of-type {
            border-top: none;
        }
        
        .solution-section strong {
            color: #374151;
            font-weight: 600;
        }
        
        .solution-section p, .solution-section ul, .solution-section ol {
            margin-top: 0.5rem;
            line-height: 1.6;
            color: #4b5563;
        }
        
        .solution-section ul li, .solution-section ol li {
            margin-bottom: 0.5rem;
        }
        
        .answer-highlight {
            background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
            color: #166534;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: bold;
            display: inline-block;
            border: 1px solid #bbf7d0;
        }
        
        .flag-reason {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 4px solid #f59e0b;
            border-radius: 0 8px 8px 0;
        }
        
        .flag-reason strong {
            color: #92400e;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container { 
                padding: 1rem; 
            }
            
            .header h1 { 
                font-size: 2rem; 
            }
            
            .automation-controls { 
                flex-direction: column; 
            }
            
            .status-info { 
                grid-template-columns: repeat(2, 1fr); 
                gap: 1rem;
            }
            
            .images-grid { 
                grid-template-columns: 1fr; 
            }
            
            .modal-content {
                width: 95%;
                margin: 1% auto;
            }
            
            .modal-header {
                padding: 1.5rem;
            }
            
            .modal-body {
                padding: 1.5rem;
            }
            
            .solutions-toolbar {
                flex-direction: column;
                gap: 0.5rem;
            }
        }
        
        /* Loading Animation */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading {
            animation: pulse 2s infinite;
        }
        
        /* Progress Bar */
        .progress-container {
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .progress-bar {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            height: 8px;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
    """

# ==================== MAIN APPLICATION ====================
app = Flask(__name__)
os.environ['ANTHROPIC_API_KEY'] = ANTHROPIC_API_KEY

@dataclass
class QuestionData:
    question_number: int
    image_filename: str
    question_text: str = ""
    options: Dict[str, str] = None
    correct_answer: str = ""
    explanation: str = ""
    detailed_explanation: Dict = None
    calculation_steps: List[str] = None
    topic: str = ""
    difficulty: str = ""
    confidence_score: float = 0.0
    solved_by_ai: bool = False
    needs_review: bool = False
    flag_reason: str = ""
    solved_at: str = ""
    processing_time: float = 0.0
    api_usage: Dict = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class AutomatedAISolver:
    """Complete Automated AI Solver using Claude API"""
    
    def __init__(self, api_key: str = None, question_banks_dir=None):
        self.question_banks_dir = Path(question_banks_dir) if question_banks_dir else QUESTION_BANKS_DIR
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.stats = {
            'total_processed': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_tokens_used': 0,
            'total_cost': 0.0
        }
        
        print(f"🔍 DEBUG: Initializing AutomatedAISolver...")
        print(f"🔑 API Key present: {'✅ Yes' if self.api_key else '❌ No'}")
        if self.api_key:
            print(f"🔑 API Key length: {len(self.api_key)}")
            print(f"🔑 API Key preview: {self.api_key[:20]}...")
            print(f"🤖 Model: {CLAUDE_API_MODEL}")
        
        if not self.api_key:
            print("⚠️ WARNING: ANTHROPIC_API_KEY not found - automation features disabled")
            print("💡 Set it with: export ANTHROPIC_API_KEY='your-key-here'")
            self.client = None
        else:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                print("✅ Claude API client initialized successfully")
                
                # Test API connection with Claude Sonnet 4
                try:
                    print("🧪 Testing Claude Sonnet 4 API connection...")
                    test_message = self.client.messages.create(
                        model=CLAUDE_API_MODEL,
                        max_tokens=50,
                        messages=[{"role": "user", "content": "Hello, are you Claude Sonnet 4?"}]
                    )
                    response = test_message.content[0].text
                    print(f"✅ API connection test successful!")
                    print(f"📝 Claude response: {response[:100]}...")
                    print(f"📊 Test usage: {test_message.usage}")
                except Exception as e:
                    print(f"❌ API connection test failed: {e}")
                    
            except Exception as e:
                print(f"❌ Failed to initialize Claude client: {e}")
                self.client = None
    
    def find_image_paths(self, paper_folder: str) -> List[Path]:
        """Find all image paths in paper folder with enhanced detection"""
        paper_path = self.question_banks_dir / paper_folder
        image_paths = []
        
        # Try multiple possible image folder locations
        possible_image_folders = [
            paper_path / "images",
            paper_path / "extracted_images", 
            paper_path / "question_images",
            paper_path,  # Images directly in paper folder
        ]
        
        print(f"🔍 Searching for images in: {paper_folder}")
        
        for images_folder in possible_image_folders:
            if images_folder.exists():
                print(f"📁 Found image folder: {images_folder}")
                
                # Supported image extensions
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
                
                for ext in image_extensions:
                    for image_file in images_folder.glob(f"*{ext}"):
                        image_paths.append(image_file)
                        print(f"📸 Found image: {image_file.name}")
        
        # Sort by filename for consistent ordering
        image_paths.sort(key=lambda x: x.name)
        print(f"✅ Total images found: {len(image_paths)}")
        return image_paths
    
    def encode_image_to_base64(self, image_path: Path) -> Optional[str]:
        """Encode image to base64 for Claude API with enhanced error handling"""
        try:
            print(f"🔄 Encoding image: {image_path.name}")
            
            # Check file size (Claude has limits)
            file_size = image_path.stat().st_size
            max_size = 5 * 1024 * 1024  # 5MB limit
            
            if file_size > max_size:
                print(f"⚠️ Image too large: {file_size:,} bytes (max: {max_size:,})")
                
                # Try to compress image
                try:
                    with Image.open(image_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        
                        # Resize if too large
                        if img.width > 1024 or img.height > 1024:
                            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                            
                        # Save compressed version temporarily
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                            img.save(temp_file.name, 'JPEG', quality=85, optimize=True)
                            
                            # Encode compressed version
                            with open(temp_file.name, 'rb') as f:
                                encoded = base64.b64encode(f.read()).decode('utf-8')
                                print(f"✅ Image compressed and encoded: {len(encoded):,} chars")
                                
                            # Clean up temp file
                            os.unlink(temp_file.name)
                            return encoded
                            
                except Exception as compression_error:
                    print(f"❌ Image compression failed: {compression_error}")
                    return None
            else:
                # Normal encoding for reasonable file sizes
                with open(image_path, 'rb') as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')
                    print(f"✅ Image encoded successfully: {len(encoded):,} chars")
                    return encoded
                    
        except Exception as e:
            print(f"❌ Error encoding image {image_path}: {e}")
            traceback.print_exc()
            return None
    
    def get_image_media_type(self, image_path: Path) -> str:
        """Get media type for image"""
        ext = image_path.suffix.lower()
        media_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff'
        }
        return media_types.get(ext, 'image/jpeg')
    
    def extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON from Claude API response with enhanced parsing"""
        print(f"🔍 Parsing response (length: {len(response_text)})")
        print(f"📝 Response preview: {response_text[:300]}...")
        
        try:
            # Strategy 1: Look for JSON in markdown code blocks
            json_pattern = r'```json\s*(.*?)\s*```'
            json_match = re.search(json_pattern, response_text, re.DOTALL)
            
            if json_match:
                json_text = json_match.group(1).strip()
                print("✅ Found JSON in code block")
            else:
                # Strategy 2: Look for JSON object in response
                brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                json_matches = re.findall(brace_pattern, response_text, re.DOTALL)
                
                if json_matches:
                    # Take the largest JSON object (most likely to be complete)
                    json_text = max(json_matches, key=len)
                    print("✅ Found JSON object in response")
                else:
                    # Strategy 3: Try to parse the entire response as JSON
                    json_text = response_text.strip()
                    print("⚠️ Attempting to parse entire response as JSON")
            
            # Clean up common JSON formatting issues
            json_text = json_text.replace('\n', '').replace('\r', '')
            json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)  # Remove trailing commas
            
            # Parse JSON
            parsed = json.loads(json_text)
            print("✅ JSON parsed successfully")
            
            # Validate required fields
            required_fields = ['question_text', 'correct_answer', 'confidence_score']
            for field in required_fields:
                if field not in parsed:
                    print(f"⚠️ Missing required field: {field}")
                    parsed[field] = ""
            
            # Ensure confidence score is a number
            if isinstance(parsed.get('confidence_score'), str):
                try:
                    parsed['confidence_score'] = float(parsed['confidence_score'])
                except:
                    parsed['confidence_score'] = 0.0
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"📝 Failed JSON text: {json_text[:500] if 'json_text' in locals() else 'Not extracted'}...")
            
            # Return a minimal structure if parsing fails
            return {
                "question_text": "Failed to parse response",
                "options": {},
                "correct_answer": "",
                "simple_answer": f"JSON parsing error: {str(e)}",
                "detailed_explanation": {"error": str(e)},
                "calculation_steps": [],
                "topic": "Unknown",
                "difficulty": "unknown",
                "confidence_score": 0.0
            }
        except Exception as e:
            print(f"❌ Unexpected error in JSON extraction: {e}")
            traceback.print_exc()
            return {
                "question_text": "Unexpected error",
                "options": {},
                "correct_answer": "",
                "simple_answer": f"Error: {str(e)}",
                "confidence_score": 0.0
            }
    
    async def solve_question_with_claude(self, question_data: QuestionData, image_path: Path, subject: str) -> QuestionData:
        """Solve individual question using Claude API with comprehensive error handling"""
        start_time = datetime.now()
        print(f"\n🚀 Starting to solve Q{question_data.question_number} with Claude Sonnet 4")
        
        if not self.client:
            print("❌ Claude API client not initialized")
            question_data.needs_review = True
            question_data.flag_reason = "Claude API client not initialized"
            question_data.solved_at = datetime.now().isoformat()
            return question_data
        
        try:
            # Step 1: Encode image
            print("🔄 Step 1: Encoding image...")
            image_base64 = self.encode_image_to_base64(image_path)
            if not image_base64:
                raise Exception("Failed to encode image")
            
            media_type = self.get_image_media_type(image_path)
            prompt_text = get_claude_prompt_template(subject, question_data.question_number)
            
            print(f"🔄 Step 2: Calling Claude Sonnet 4 API...")
            print(f"📝 Model: {CLAUDE_API_MODEL}")
            print(f"📝 Max tokens: {CLAUDE_API_MAX_TOKENS}")
            print(f"📝 Media type: {media_type}")
            print(f"📝 Image size: {len(image_base64):,} chars")
            
            # Step 2: Call Claude API with Claude Sonnet 4
            message = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=CLAUDE_API_MODEL,
                    max_tokens=CLAUDE_API_MAX_TOKENS,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt_text
                            }
                        ]
                    }]
                )
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ API call successful! ({processing_time:.2f}s)")
            print(f"📊 Usage: {message.usage}")
            
            # Update stats
            self.stats['successful_calls'] += 1
            self.stats['total_tokens_used'] += message.usage.input_tokens + message.usage.output_tokens
            
            # Calculate approximate cost (Claude Sonnet 4: $3/$15 per million tokens)
            input_cost = (message.usage.input_tokens / 1_000_000) * 3.0
            output_cost = (message.usage.output_tokens / 1_000_000) * 15.0
            total_cost = input_cost + output_cost
            self.stats['total_cost'] += total_cost
            
            # Step 3: Parse response
            print("🔄 Step 3: Parsing Claude Sonnet 4 response...")
            response_text = message.content[0].text
            solution_data = self.extract_json_from_response(response_text)
            
            # Step 4: Update question data
            print("🔄 Step 4: Updating question data...")
            question_data.question_text = solution_data.get('question_text', '')
            question_data.options = solution_data.get('options', {})
            question_data.correct_answer = solution_data.get('correct_answer', '')
            question_data.explanation = solution_data.get('simple_answer', '')
            question_data.detailed_explanation = solution_data.get('detailed_explanation', {})
            question_data.calculation_steps = solution_data.get('calculation_steps', [])
            question_data.topic = solution_data.get('topic', '')
            question_data.difficulty = solution_data.get('difficulty', 'medium')
            question_data.confidence_score = solution_data.get('confidence_score', 0.0)
            question_data.solved_by_ai = True
            question_data.solved_at = datetime.now().isoformat()
            question_data.processing_time = processing_time
            question_data.api_usage = {
                'input_tokens': message.usage.input_tokens,
                'output_tokens': message.usage.output_tokens,
                'cost': total_cost
            }
            
            # Step 5: Quality check
            print("🔄 Step 5: Quality assessment...")
            quality_issues = []
            
            if question_data.confidence_score < CONFIDENCE_THRESHOLD:
                quality_issues.append(f"Low confidence: {question_data.confidence_score:.1%}")
            
            if not question_data.correct_answer:
                quality_issues.append("No answer provided")
            
            if not question_data.question_text or len(question_data.question_text) < 10:
                quality_issues.append("Question text too short or missing")
            
            if quality_issues:
                question_data.needs_review = True
                question_data.flag_reason = "; ".join(quality_issues)
                print(f"⚠️ Quality issues found: {question_data.flag_reason}")
            else:
                question_data.needs_review = False
                print(f"✅ Quality check passed")
            
            print(f"🎉 Q{question_data.question_number} completed successfully!")
            print(f"   Answer: {question_data.correct_answer}")
            print(f"   Confidence: {question_data.confidence_score:.1%}")
            print(f"   Processing time: {processing_time:.2f}s")
            print(f"   Cost: ${total_cost:.4f}")
            
            self.stats['total_processed'] += 1
            return question_data
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error solving Q{question_data.question_number}: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            
            # Update stats
            self.stats['failed_calls'] += 1
            self.stats['total_processed'] += 1
            
            # Update question data with error info
            question_data.needs_review = True
            question_data.flag_reason = f"API Error: {str(e)}"
            question_data.solved_by_ai = True  # Mark as attempted
            question_data.solved_at = datetime.now().isoformat()
            question_data.processing_time = processing_time
            
            return question_data
    
    def get_paper_images_with_details(self, paper_folder: str) -> Dict:
        """Get all images with details for Review-style interface"""
        try:
            paper_path = self.question_banks_dir / paper_folder
            
            # Load solutions.json to get question mapping
            solutions_file = paper_path / "solutions.json"
            questions_data = {}
            
            if solutions_file.exists():
                with open(solutions_file, 'r') as f:
                    solutions_data = json.load(f)
                    questions = solutions_data.get('questions', [])
                    for q in questions:
                        questions_data[q.get('question_number')] = q
            
            # Find all images
            image_paths = self.find_image_paths(paper_folder)
            
            if not image_paths:
                return {"success": False, "error": "No images found in any expected folders"}
            
            images = []
            
            for image_path in image_paths:
                try:
                    # Extract question number from filename
                    question_num = self.extract_question_number_from_filename(image_path.stem)
                    
                    # Get image dimensions and file size
                    with Image.open(image_path) as img:
                        width, height = img.size
                    
                    file_size = image_path.stat().st_size
                    
                    # Get question data if available
                    question_data = questions_data.get(question_num, {})
                    
                    images.append({
                        "filename": image_path.name,
                        "question_number": question_num,
                        "question_text": question_data.get('question_text', ''),
                        "solved": question_data.get('solved_by_ai', False),
                        "needs_review": question_data.get('needs_review', False),
                        "confidence": question_data.get('confidence_score', 0),
                        "correct_answer": question_data.get('correct_answer', ''),
                        "size": file_size,
                        "dimensions": f"{width}x{height}",
                        "url": f"/images/{paper_folder}/{image_path.name}",
                        "path": str(image_path)
                    })
                    
                except Exception as e:
                    print(f"Error processing image {image_path.name}: {e}")
            
            # Sort by question number
            images.sort(key=lambda x: x["question_number"] or 999)
            
            return {
                "success": True,
                "images": images,
                "total_images": len(images)
            }
            
        except Exception as e:
            print(f"Error in get_paper_images_with_details: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def extract_question_number_from_filename(self, filename: str) -> Optional[int]:
        """Extract question number from various filename patterns"""
        patterns = [
            r'question[_\-\s]*(\d+)',
            r'q[_\-\s]*(\d+)',
            r'^(\d+)',
            r'(\d+)',  # Any number in filename
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    async def process_paper_automated(self, paper_folder: str, batch_size: int = 3, delay: float = 2.0) -> Dict:
        """Process entire paper automatically with comprehensive progress tracking"""
        if not self.client:
            return {"success": False, "error": "Claude API not configured"}
        
        try:
            paper_path = self.question_banks_dir / paper_folder
            master_file = paper_path / "solutions.json"
            
            if not master_file.exists():
                return {"success": False, "error": "Master solutions.json not found"}
            
            print(f"🚀 Starting automated processing with Claude Sonnet 4")
            print(f"📁 Paper: {paper_folder}")
            print(f"⚙️ Batch size: {batch_size}")
            print(f"⏱️ Delay: {delay}s between batches")
            
            # Load existing data
            async with aiofiles.open(master_file, 'r') as f:
                content = await f.read()
                master_data = json.loads(content)
            
            questions = master_data.get('questions', [])
            metadata = master_data.get('metadata', {})
            subject = metadata.get('subject', 'Physics').title()
            
            total_questions = len(questions)
            processed_count = 0
            flagged_count = 0
            error_count = 0
            
            print(f"📊 Total questions: {total_questions}")
            print(f"📚 Subject: {subject}")
            
            # Find all available images
            image_paths = self.find_image_paths(paper_folder)
            if not image_paths:
                return {"success": False, "error": "No images found"}
            
            print(f"📸 Images found: {len(image_paths)}")
            
            # Create image path lookup
            image_lookup = {}
            for img_path in image_paths:
                question_num = self.extract_question_number_from_filename(img_path.stem)
                if question_num:
                    image_lookup[question_num] = img_path
            
            print(f"🔗 Image-question mappings: {len(image_lookup)}")
            
            # Process in batches
            start_time = datetime.now()
            
            for i in range(0, len(questions), batch_size):
                batch = questions[i:i + batch_size]
                batch_tasks = []
                batch_start_time = datetime.now()
                
                print(f"\n🔥 Processing batch {i//batch_size + 1}/{(len(questions) + batch_size - 1)//batch_size}")
                
                for question in batch:
                    question_num = question.get('question_number')
                    
                    # Skip if already solved
                    if question.get('solved_by_ai', False):
                        print(f"⭐ Skipping Q{question_num} - already solved")
                        continue
                    
                    # Find corresponding image
                    image_path = image_lookup.get(question_num)
                    if not image_path:
                        print(f"⚠️ No image found for Q{question_num}")
                        continue
                    
                    # Create question data object
                    question_data = QuestionData(
                        question_number=question_num,
                        image_filename=image_path.name
                    )
                    
                    # Add to batch
                    batch_tasks.append(
                        self.solve_question_with_claude(question_data, image_path, subject)
                    )
                
                # Process batch concurrently
                if batch_tasks:
                    print(f"⚡ Processing {len(batch_tasks)} questions concurrently...")
                    solved_questions = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    
                    # Update master data
                    for solved_q in solved_questions:
                        if isinstance(solved_q, Exception):
                            print(f"❌ Batch processing error: {solved_q}")
                            error_count += 1
                            continue
                        
                        # Find and update the corresponding question
                        for j, question in enumerate(questions):
                            if question.get('question_number') == solved_q.question_number:
                                # Convert dataclass to dict for JSON serialization
                                update_data = solved_q.to_dict()
                                update_data['solved_at'] = solved_q.solved_at
                                
                                questions[j].update(update_data)
                                processed_count += 1
                                
                                if solved_q.needs_review:
                                    flagged_count += 1
                                
                                break
                    
                    # Save progress after each batch
                    master_data['questions'] = questions
                    master_data['metadata'].update({
                        'last_updated': datetime.now().isoformat(),
                        'automated_solver_version': 'Enhanced Claude Sonnet 4 v2.0',
                        'model_used': CLAUDE_API_MODEL,
                        'processing_stats': {
                            'total_processed': processed_count,
                            'total_flagged': flagged_count,
                            'total_errors': error_count,
                            'processing_time': str(datetime.now() - start_time),
                            'api_stats': self.stats
                        }
                    })
                    
                    async with aiofiles.open(master_file, 'w') as f:
                        await f.write(json.dumps(master_data, indent=2, default=str))
                    
                    batch_time = (datetime.now() - batch_start_time).total_seconds()
                    print(f"✅ Batch completed in {batch_time:.2f}s")
                    print(f"📊 Progress: {processed_count}/{total_questions} ({processed_count/total_questions*100:.1f}%)")
                    print(f"💰 Total cost so far: ${self.stats['total_cost']:.4f}")
                
                # Rate limiting delay
                if i + batch_size < len(questions):
                    print(f"⏳ Waiting {delay}s before next batch...")
                    await asyncio.sleep(delay)
            
            # Final statistics
            total_time = (datetime.now() - start_time).total_seconds()
            solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
            completion_rate = (solved_count / total_questions * 100) if total_questions > 0 else 0
            
            print(f"\n🎉 AUTOMATION COMPLETE!")
            print(f"⏱️ Total time: {total_time:.1f}s")
            print(f"📊 Processed: {processed_count} questions")
            print(f"✅ Total solved: {solved_count}/{total_questions}")
            print(f"⚠️ Flagged: {flagged_count} questions")
            print(f"❌ Errors: {error_count} questions")
            print(f"📈 Completion rate: {completion_rate:.1f}%")
            print(f"🤖 Model used: {CLAUDE_API_MODEL}")
            print(f"💰 Total cost: ${self.stats['total_cost']:.4f}")
            print(f"📞 API calls: {self.stats['successful_calls']} successful, {self.stats['failed_calls']} failed")
            print(f"🎫 Tokens used: {self.stats['total_tokens_used']:,}")
            
            return {
                "success": True,
                "message": f"Automated processing complete! Processed {processed_count} questions using {CLAUDE_API_MODEL}.",
                "stats": {
                    "total_questions": total_questions,
                    "processed": processed_count,
                    "solved": solved_count,
                    "flagged": flagged_count,
                    "errors": error_count,
                    "completion_rate": completion_rate,
                    "processing_time": total_time,
                    "model_used": CLAUDE_API_MODEL,
                    "total_cost": self.stats['total_cost'],
                    "api_calls": {
                        "successful": self.stats['successful_calls'],
                        "failed": self.stats['failed_calls']
                    },
                    "tokens_used": self.stats['total_tokens_used']
                }
            }
            
        except Exception as e:
            print(f"❌ Automated processing error: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}

# Initialize components
automated_solver = AutomatedAISolver()

# ==================== FLASK ROUTES ====================

@app.route('/solver/<paper_folder>')
def serve_solver_interface(paper_folder):
    """Serve the complete AI solver interface"""
    try:
        # Get paper info
        paper_path = QUESTION_BANKS_DIR / paper_folder
        solutions_file = paper_path / "solutions.json"
        
        if not solutions_file.exists():
            return f"Error: solutions.json not found for {paper_folder}", 404
        
        with open(solutions_file, 'r') as f:
            solutions_data = json.load(f)
        
        metadata = solutions_data.get('metadata', {})
        questions = solutions_data.get('questions', [])
        
        subject = metadata.get('subject', 'Physics').title()
        year = metadata.get('year', '2025')
        month = metadata.get('month', 'Unknown').title()
        paper_code = metadata.get('paper_code', '1')
        
        title = f"{subject} {year} {month} Paper {paper_code}"
        total_questions = len(questions)
        solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
        flagged_count = sum(1 for q in questions if q.get('needs_review', False))
        
        # Calculate additional statistics
        total_confidence = sum(q.get('confidence_score', 0) for q in questions if q.get('solved_by_ai'))
        avg_confidence = (total_confidence / solved_count * 100) if solved_count > 0 else 0
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>🤖 AI Solver - {title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{get_css_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Enhanced AI Solver</h1>
            <p>{title}</p>
            <p>🚀 Claude Sonnet 4 Automation • 📁 Enhanced Image Detection • 🎯 Quality Control</p>
            <small>Model: {CLAUDE_API_MODEL} • Threshold: {QUALITY_THRESHOLD_DISPLAY}</small>
        </div>
        
        <div class="status-section">
            <div class="status-info">
                <div class="status-card">
                    <h4>Total Questions</h4>
                    <div id="totalQuestions">{total_questions}</div>
                </div>
                <div class="status-card">
                    <h4>Solved</h4>
                    <div id="solvedCount">{solved_count}</div>
                </div>
                <div class="status-card">
                    <h4>Flagged</h4>
                    <div id="flaggedCount">{flagged_count}</div>
                </div>
                <div class="status-card">
                    <h4>Progress</h4>
                    <div id="progressPercent">{round((solved_count / total_questions) * 100, 1) if total_questions > 0 else 0}%</div>
                </div>
                <div class="status-card">
                    <h4>Avg Confidence</h4>
                    <div id="avgConfidence">{avg_confidence:.1f}%</div>
                </div>
            </div>
            
            <div class="progress-container">
                <div class="progress-bar" style="width: {(solved_count / total_questions) * 100 if total_questions > 0 else 0}%"></div>
            </div>
            
            <div class="automation-controls">
                <button class="btn btn-preview" onclick="loadImagePreview()">🔍 Preview Images</button>
                <button class="btn btn-check" onclick="checkAutomationStatus()">⚙️ Check Status</button>
                <button class="btn btn-automate" onclick="startAutomation()">🚀 Start Automation</button>
                <button class="btn btn-solutions" onclick="viewSolutions()">📋 View Solutions</button>
            </div>
        </div>
        
        <div class="process-section">
            <h3>🔥 Enhanced Automation Process:</h3>
            <ol class="process-steps">
                <li><strong>1. Enhanced Image Detection:</strong> Automatically finds images in multiple possible folders (images/, extracted_images/, etc.)</li>
                <li><strong>2. Claude Sonnet 4 Processing:</strong> Uses the latest Claude Sonnet 4 model for superior reasoning and accuracy</li>
                <li><strong>3. Quality Control:</strong> Comprehensive confidence scoring and error detection with detailed flagging</li>
                <li><strong>4. Progress Tracking:</strong> Real-time statistics, cost tracking, and performance monitoring</li>
                <li><strong>5. Solutions Review:</strong> Detailed solution viewer with export capabilities and filtering options</li>
            </ol>
        </div>
        
        <div class="images-section">
            <h3>📸 Question Images Detection</h3>
            <p>Automatically searches in: <code>images/</code>, <code>extracted_images/</code>, <code>question_images/</code></p>
            <div class="images-grid" id="imagesGrid">
                <div class="loading" style="text-align: center; padding: 3rem; color: #6b7280;">
                    <h4>🔍 Ready to scan for images</h4>
                    <p>Click "Preview Images" to automatically detect and verify all question images</p>
                    <p><small>Supports: PNG, JPG, GIF, WebP, BMP, TIFF formats</small></p>
                </div>
            </div>
        </div>
        
        <!-- Enhanced Solutions Modal -->
        <div id="solutionsModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>📋 AI Solutions - {title}</h2>
                    <span class="close" onclick="closeSolutionsModal()">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="solutions-toolbar">
                        <button class="btn btn-small" onclick="exportSolutions('json')">📄 Export JSON</button>
                        <button class="btn btn-small" onclick="exportSolutions('csv')">📊 Export CSV</button>
                        <button class="btn btn-small" onclick="showOnlyFlagged()">⚠️ Flagged Only</button>
                        <button class="btn btn-small" onclick="showOnlyHighConfidence()">✅ High Confidence</button>
                        <button class="btn btn-small" onclick="showAllSolutions()">📋 Show All</button>
                        <button class="btn btn-small" onclick="refreshSolutions()">🔄 Refresh</button>
                    </div>
                    <div id="solutionsContent">
                        <div class="loading" style="text-align: center; padding: 2rem;">
                            Loading solutions...
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const paperFolder = '{paper_folder}';
        let currentSolutions = [];
        
        function showNotification(message, type = 'info') {{
            const existing = document.querySelectorAll('.notification');
            existing.forEach(n => n.remove());
            
            const notification = document.createElement('div');
            notification.className = `notification ${{type}}`;
            notification.innerHTML = message;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.classList.add('show'), 100);
            setTimeout(() => {{
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }}, 5000);
        }}
        
        async function loadImagePreview() {{
            try {{
                showNotification('🔍 Scanning for images...', 'info');
                
                const response = await fetch('/api/get-images-preview', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ paper_folder: paperFolder }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    displayImages(data.images);
                    showNotification(`✅ Found ${{data.total_images}} images in multiple folders`, 'success');
                }} else {{
                    showNotification(`⚠️ Failed to load images: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                showNotification(`❌ Error: ${{error.message}}`, 'error');
            }}
        }}
        
        function displayImages(images) {{
            const grid = document.getElementById('imagesGrid');
            
            if (images.length === 0) {{
                grid.innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: #dc3545;">
                        <h4>❌ No images found</h4>
                        <p>Searched in: images/, extracted_images/, question_images/</p>
                        <p>Supported formats: PNG, JPG, GIF, WebP, BMP, TIFF</p>
                    </div>
                `;
                return;
            }}
            
            grid.innerHTML = images.map(img => `
                <div class="image-card">
                    <div class="image-header">
                        <h4>Question ${{img.question_number || '?'}}</h4>
                        <span class="status-badge ${{img.solved ? (img.needs_review ? 'status-review' : 'status-solved') : 'status-pending'}}">
                            ${{img.solved ? (img.needs_review ? 'Review' : 'Solved') : 'Pending'}}
                        </span>
                    </div>
                    <img src="${{img.url}}" alt="Question ${{img.question_number}}" class="image-preview" 
                         onclick="window.open('${{img.url}}', '_blank')" 
                         loading="lazy">
                    <div class="image-info">
                        <p><strong>File:</strong> ${{img.filename}}</p>
                        <p><strong>Size:</strong> ${{img.dimensions}} • ${{(img.size / 1024).toFixed(1)}} KB</p>
                        ${{img.question_text ? `<p><strong>Text:</strong> ${{img.question_text.substring(0, 80)}}...</p>` : ''}}
                        ${{img.confidence > 0 ? `<p><strong>Confidence:</strong> ${{(img.confidence * 100).toFixed(1)}}%</p>` : ''}}
                        ${{img.correct_answer ? `<p><strong>Answer:</strong> <span class="answer-highlight">${{img.correct_answer}}</span></p>` : ''}}
                    </div>
                </div>
            `).join('');
        }}
        
        async function checkAutomationStatus() {{
            try {{
                showNotification('⚙️ Checking Claude Sonnet 4 status...', 'info');
                
                const response = await fetch('/api/check-api-status');
                const data = await response.json();
                
                if (data.success && data.api_key_configured) {{
                    showNotification(`✅ Claude Sonnet 4 ready! Model: ${{data.model_info || '{CLAUDE_API_MODEL}'}}`, 'success');
                }} else {{
                    showNotification('⚠️ Claude API not configured', 'error');
                }}
                
                // Also refresh progress
                const progressResponse = await fetch('/api/get-progress', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ paper_folder: paperFolder }})
                }});
                
                const progressData = await progressResponse.json();
                if (progressData.success) {{
                    updateProgress(progressData.progress);
                }}
            }} catch (error) {{
                showNotification(`❌ Error: ${{error.message}}`, 'error');
            }}
        }}
        
        async function startAutomation() {{
            const confirmMessage = `Start automated Claude Sonnet 4 solving for ${{paperFolder}}?

🤖 Model: {CLAUDE_API_MODEL}
📊 Batch processing with rate limits
💰 Cost: ~$3-15 per million tokens
⏱️ Time: ~2-5 seconds per question

This will process all unsolved questions automatically.`;

            if (confirm(confirmMessage)) {{
                try {{
                    showNotification('🚀 Starting Claude Sonnet 4 automation...', 'info');
                    
                    const startTime = Date.now();
                    
                    const response = await fetch('/api/start-automation', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ 
                            paper_folder: paperFolder,
                            batch_size: 3,
                            delay: 2.0 
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        const stats = data.stats;
                        const processingTime = ((Date.now() - startTime) / 1000).toFixed(1);
                        
                        let message = `🎉 Automation Complete! (${{processingTime}}s)

📊 Processed: ${{stats.processed}} questions
✅ Total solved: ${{stats.solved}}/${{stats.total_questions}}
⚠️ Flagged for review: ${{stats.flagged}}
❌ Errors: ${{stats.errors || 0}}
📈 Progress: ${{stats.completion_rate.toFixed(1)}}%
🤖 Model: ${{stats.model_used || '{CLAUDE_API_MODEL}'}}`;

                        if (stats.total_cost) {{
                            message += `
💰 Total cost: ${{stats.total_cost.toFixed(4)}}
🎫 Tokens used: ${{stats.tokens_used?.toLocaleString() || 'N/A'}}`;
                        }}
                        
                        alert(message);
                        location.reload();
                    }} else {{
                        showNotification(`❌ Automation failed: ${{data.error}}`, 'error');
                    }}
                }} catch (error) {{
                    showNotification(`❌ Error: ${{error.message}}`, 'error');
                }}
            }}
        }}
        
        async function viewSolutions() {{
            try {{
                showNotification('📋 Loading solutions...', 'info');
                
                const response = await fetch('/api/get-solutions', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ paper_folder: paperFolder }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    currentSolutions = data.solutions;
                    displaySolutions(data.solutions, data.metadata);
                    document.getElementById('solutionsModal').style.display = 'block';
                    showNotification('✅ Solutions loaded', 'success');
                }} else {{
                    showNotification(`⚠️ Failed to load solutions: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                showNotification(`❌ Error: ${{error.message}}`, 'error');
            }}
        }}
        
        function displaySolutions(solutions, metadata) {{
            const content = document.getElementById('solutionsContent');
            
            // Calculate enhanced statistics
            const totalQuestions = solutions.length;
            const solvedCount = solutions.filter(s => s.solved_by_ai).length;
            const flaggedCount = solutions.filter(s => s.needs_review).length;
            const highConfidenceCount = solutions.filter(s => s.confidence_score >= 0.85).length;
            const avgConfidence = solutions.filter(s => s.solved_by_ai).reduce((sum, s) => sum + (s.confidence_score || 0), 0) / (solvedCount || 1) * 100;
            const totalCost = metadata.processing_stats?.api_stats?.total_cost || 0;
            
            let html = `
                <div class="solutions-summary">
                    <h3>📊 Enhanced Summary</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">
                        <div><strong>Paper:</strong> ${{metadata.subject || 'Unknown'}} ${{metadata.year || ''}} ${{metadata.month || ''}} Paper ${{metadata.paper_code || ''}}</div>
                        <div><strong>Total Questions:</strong> ${{totalQuestions}}</div>
                        <div><strong>Solved:</strong> ${{solvedCount}} (${{(solvedCount/totalQuestions*100).toFixed(1)}}%)</div>
                        <div><strong>Flagged:</strong> ${{flaggedCount}} (${{(flaggedCount/solvedCount*100).toFixed(1) || 0}}%)</div>
                        <div><strong>High Confidence (≥85%):</strong> ${{highConfidenceCount}} (${{(highConfidenceCount/solvedCount*100).toFixed(1) || 0}}%)</div>
                        <div><strong>Avg Confidence:</strong> ${{avgConfidence.toFixed(1)}}%</div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">
                        <div><strong>Model Used:</strong> ${{metadata.processing_stats?.model_used || metadata.automated_solver_version || '{CLAUDE_API_MODEL}'}}</div>
                        <div><strong>Last Updated:</strong> ${{metadata.last_updated ? new Date(metadata.last_updated).toLocaleString() : 'Unknown'}}</div>
                        ${{totalCost > 0 ? `<div><strong>Total Cost:</strong> ${{totalCost.toFixed(4)}}</div>` : ''}}
                        ${{metadata.processing_stats?.api_stats?.total_tokens_used ? `<div><strong>Tokens Used:</strong> ${{metadata.processing_stats.api_stats.total_tokens_used.toLocaleString()}}</div>` : ''}}
                    </div>
                </div>
                <hr style="margin: 2rem 0; border: none; height: 1px; background: #e2e8f0;">
            `;
            
            // Sort solutions by question number
            const sortedSolutions = [...solutions].sort((a, b) => (a.question_number || 999) - (b.question_number || 999));
            
            sortedSolutions.forEach(solution => {{
                const statusClass = solution.solved_by_ai ? 
                    (solution.needs_review ? 'status-review' : 'status-solved') : 
                    'status-pending';
                    
                const statusText = solution.solved_by_ai ?
                    (solution.needs_review ? 'Needs Review' : 'Solved') :
                    'Pending';
                    
                const confidenceColor = solution.confidence_score >= 0.85 ? '#10b981' : 
                                      solution.confidence_score >= 0.7 ? '#f59e0b' : '#ef4444';
                
                html += `
                    <div class="solution-item" data-flagged="${{solution.needs_review ? 'true' : 'false'}}" data-high-confidence="${{solution.confidence_score >= 0.85 ? 'true' : 'false'}}">
                        <div class="solution-header">
                            <h4>Question ${{solution.question_number}}</h4>
                            <div style="display: flex; gap: 0.5rem; align-items: center;">
                                <span class="status-badge ${{statusClass}}">${{statusText}}</span>
                                ${{solution.confidence_score > 0 ? `<span class="confidence-badge" style="background-color: ${{confidenceColor}}">${{(solution.confidence_score * 100).toFixed(1)}}%</span>` : ''}}
                            </div>
                        </div>
                        
                        ${{solution.question_text ? `
                            <div class="solution-section">
                                <strong>📝 Question:</strong>
                                <p>${{solution.question_text}}</p>
                            </div>
                        ` : ''}}
                        
                        ${{solution.options && Object.keys(solution.options).length > 0 ? `
                            <div class="solution-section">
                                <strong>📋 Options:</strong>
                                <ul>
                                    ${{Object.entries(solution.options).map(([key, value]) => 
                                        `<li><strong>${{key}}:</strong> ${{value}}</li>`
                                    ).join('')}}
                                </ul>
                            </div>
                        ` : ''}}
                        
                        ${{solution.correct_answer ? `
                            <div class="solution-section">
                                <strong>✅ Answer:</strong>
                                <span class="answer-highlight">${{solution.correct_answer}}</span>
                            </div>
                        ` : ''}}
                        
                        ${{solution.explanation ? `
                            <div class="solution-section">
                                <strong>💡 Explanation:</strong>
                                <p>${{solution.explanation}}</p>
                            </div>
                        ` : ''}}
                        
                        ${{solution.calculation_steps && solution.calculation_steps.length > 0 ? `
                            <div class="solution-section">
                                <strong>🔢 Calculation Steps:</strong>
                                <ol>
                                    ${{solution.calculation_steps.map(step => `<li>${{step}}</li>`).join('')}}
                                </ol>
                            </div>
                        ` : ''}}
                        
                        <div class="solution-section" style="background: #f8fafc;">
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; font-size: 0.9rem;">
                                ${{solution.topic ? `<div><strong>📚 Topic:</strong> ${{solution.topic}}</div>` : ''}}
                                ${{solution.difficulty ? `<div><strong>📊 Difficulty:</strong> ${{solution.difficulty}}</div>` : ''}}
                                ${{solution.processing_time ? `<div><strong>⏱️ Time:</strong> ${{solution.processing_time.toFixed(2)}}s</div>` : ''}}
                                ${{solution.api_usage?.cost ? `<div><strong>💰 Cost:</strong> ${{solution.api_usage.cost.toFixed(4)}}</div>` : ''}}
                                ${{solution.solved_at ? `<div><strong>🕐 Solved:</strong> ${{new Date(solution.solved_at).toLocaleTimeString()}}</div>` : ''}}
                            </div>
                        </div>
                        
                        ${{solution.needs_review && solution.flag_reason ? `
                            <div class="solution-section flag-reason">
                                <strong>⚠️ Review Required:</strong> ${{solution.flag_reason}}
                            </div>
                        ` : ''}}
                    </div>
                `;
            }});
            
            content.innerHTML = html;
        }}
        
        function closeSolutionsModal() {{
            document.getElementById('solutionsModal').style.display = 'none';
        }}
        
        function showOnlyFlagged() {{
            filterSolutions(item => item.dataset.flagged === 'true');
        }}
        
        function showOnlyHighConfidence() {{
            filterSolutions(item => item.dataset.highConfidence === 'true');
        }}
        
        function showAllSolutions() {{
            filterSolutions(() => true);
        }}
        
        function filterSolutions(condition) {{
            const items = document.querySelectorAll('.solution-item');
            items.forEach(item => {{
                if (condition(item)) {{
                    item.style.display = 'block';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}
        
        async function refreshSolutions() {{
            await viewSolutions();
        }}
        
        async function exportSolutions(format) {{
            try {{
                showNotification(`📤 Exporting as ${{format.toUpperCase()}}...`, 'info');
                
                const response = await fetch('/api/export-solutions', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ 
                        paper_folder: paperFolder,
                        format: format
                    }})
                }});
                
                if (response.ok) {{
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `${{paperFolder}}_solutions.${{format}}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    showNotification(`✅ Exported as ${{format.toUpperCase()}}`, 'success');
                }} else {{
                    throw new Error('Export failed');
                }}
            }} catch (error) {{
                showNotification(`❌ Export error: ${{error.message}}`, 'error');
            }}
        }}
        
        function updateProgress(progress) {{
            document.getElementById('totalQuestions').textContent = progress.total_questions || 0;
            document.getElementById('solvedCount').textContent = progress.solved_count || 0;
            document.getElementById('flaggedCount').textContent = progress.flagged_count || 0;
            document.getElementById('progressPercent').textContent = `${{(progress.completion_percentage || 0).toFixed(1)}}%`;
            
            if (progress.average_confidence !== undefined) {{
                document.getElementById('avgConfidence').textContent = `${{progress.average_confidence.toFixed(1)}}%`;
            }}
            
            // Update progress bar
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {{
                progressBar.style.width = `${{progress.completion_percentage || 0}}%`;
            }}
        }}
        
        // Enhanced keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeSolutionsModal();
            }} else if (e.ctrlKey && e.key === 'r') {{
                e.preventDefault();
                location.reload();
            }}
        }});
        
        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('solutionsModal');
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }}
        
        // Auto-refresh progress every 30 seconds during automation
        let progressInterval;
        
        function startProgressMonitoring() {{
            progressInterval = setInterval(async () => {{
                try {{
                    const response = await fetch('/api/get-progress', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ paper_folder: paperFolder }})
                    }});
                    
                    const data = await response.json();
                    if (data.success) {{
                        updateProgress(data.progress);
                    }}
                }} catch (error) {{
                    console.log('Progress update failed:', error);
                }}
            }}, 30000);
        }}
        
        function stopProgressMonitoring() {{
            if (progressInterval) {{
                clearInterval(progressInterval);
                progressInterval = null;
            }}
        }}
        
        // Initialize
        window.addEventListener('load', () => {{
            showNotification('🤖 Enhanced AI Solver loaded with Claude Sonnet 4!', 'success');
            startProgressMonitoring();
            
            // Auto-load image preview if few images
            setTimeout(() => {{
                checkAutomationStatus();
            }}, 1000);
        }});
        
        window.addEventListener('beforeunload', () => {{
            stopProgressMonitoring();
        }});
    </script>
</body>
</html>'''
        
        return html_content
        
    except Exception as e:
        return f"Error creating interface: {str(e)}", 500

@app.route('/api/get-images-preview', methods=['POST'])
def get_images_preview():
    """Get preview of all images in paper folder with enhanced detection"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        result = automated_solver.get_paper_images_with_details(paper_folder)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/get-solutions', methods=['POST'])
def get_solutions():
    """Get solutions from the solutions.json file with enhanced data"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        paper_path = QUESTION_BANKS_DIR / paper_folder
        solutions_file = paper_path / "solutions.json"
        
        if not solutions_file.exists():
            return jsonify({"success": False, "error": "Solutions file not found"})
        
        with open(solutions_file, 'r') as f:
            solutions_data = json.load(f)
        
        questions = solutions_data.get('questions', [])
        metadata = solutions_data.get('metadata', {})
        
        # Sort questions by question number
        questions.sort(key=lambda x: x.get('question_number', 999))
        
        return jsonify({
            "success": True,
            "solutions": questions,
            "metadata": metadata
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/export-solutions', methods=['POST'])
def export_solutions():
    """Export solutions in various formats with enhanced data"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        format_type = data.get('format', 'json')
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        paper_path = QUESTION_BANKS_DIR / paper_folder
        solutions_file = paper_path / "solutions.json"
        
        if not solutions_file.exists():
            return jsonify({"success": False, "error": "Solutions file not found"})
        
        with open(solutions_file, 'r') as f:
            solutions_data = json.load(f)
        
        if format_type == 'json':
            return send_file(
                str(solutions_file),
                as_attachment=True,
                download_name=f"{paper_folder}_solutions.json",
                mimetype='application/json'
            )
        
        elif format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Enhanced CSV headers
            writer.writerow([
                'Question Number', 'Question Text', 'Correct Answer', 
                'Explanation', 'Topic', 'Difficulty', 'Confidence Score',
                'Solved by AI', 'Needs Review', 'Flag Reason', 'Solved At',
                'Processing Time', 'API Cost', 'Model Used'
            ])
            
            # Enhanced CSV data
            for q in solutions_data.get('questions', []):
                writer.writerow([
                    q.get('question_number', ''),
                    q.get('question_text', ''),
                    q.get('correct_answer', ''),
                    q.get('explanation', ''),
                    q.get('topic', ''),
                    q.get('difficulty', ''),
                    q.get('confidence_score', 0),
                    q.get('solved_by_ai', False),
                    q.get('needs_review', False),
                    q.get('flag_reason', ''),
                    q.get('solved_at', ''),
                    q.get('processing_time', ''),
                    q.get('api_usage', {}).get('cost', ''),
                    solutions_data.get('metadata', {}).get('processing_stats', {}).get('model_used', CLAUDE_API_MODEL)
                ])
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                as_attachment=True,
                download_name=f"{paper_folder}_solutions.csv",
                mimetype='text/csv'
            )
        
        else:
            return jsonify({"success": False, "error": "Unsupported format"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/start-automation', methods=['POST'])
def start_automation():
    """Start automated solving process with enhanced tracking"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        batch_size = data.get('batch_size', 3)
        delay = data.get('delay', 2.0)
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        if not automated_solver.client:
            return jsonify({"success": False, "error": "Claude API not configured"})
        
        # Run automation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                automated_solver.process_paper_automated(paper_folder, batch_size, delay)
            )
            return jsonify(result)
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/get-progress', methods=['POST'])
def get_progress():
    """Get current solving progress with enhanced statistics"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        paper_path = QUESTION_BANKS_DIR / paper_folder
        solutions_file = paper_path / "solutions.json"
        
        if not solutions_file.exists():
            return jsonify({"success": False, "error": "Solutions file not found"})
        
        with open(solutions_file, 'r') as f:
            solutions_data = json.load(f)
        
        questions = solutions_data.get('questions', [])
        total_questions = len(questions)
        solved_questions = [q for q in questions if q.get('solved_by_ai', False)]
        solved_count = len(solved_questions)
        flagged_count = sum(1 for q in questions if q.get('needs_review', False))
        
        # Calculate average confidence
        if solved_questions:
            total_confidence = sum(q.get('confidence_score', 0) for q in solved_questions)
            average_confidence = (total_confidence / solved_count) * 100
        else:
            average_confidence = 0
        
        return jsonify({
            "success": True,
            "progress": {
                "total_questions": total_questions,
                "solved_count": solved_count,
                "flagged_count": flagged_count,
                "completion_percentage": (solved_count / total_questions * 100) if total_questions > 0 else 0,
                "average_confidence": average_confidence
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/check-api-status', methods=['GET'])
def check_api_status():
    """Check if Claude API is configured with enhanced info"""
    return jsonify({
        "success": True,
        "api_key_configured": bool(automated_solver.client),
        "key_preview": f"{ANTHROPIC_API_KEY[:8]}..." if ANTHROPIC_API_KEY else None,
        "model_info": CLAUDE_API_MODEL,
        "stats": automated_solver.stats
    })

# Image serving with enhanced support
@app.route('/images/<paper_folder>/<filename>')
def serve_paper_image(paper_folder, filename):
    """Serve images from paper folders with enhanced detection"""
    try:
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        
        # Try multiple possible image folder locations
        possible_folders = [
            paper_folder_path / "images",
            paper_folder_path / "extracted_images",
            paper_folder_path / "question_images",
            paper_folder_path
        ]
        
        for folder in possible_folders:
            if folder.exists():
                image_path = folder / filename
                if image_path.exists():
                    return send_from_directory(str(folder), filename)
        
        return f"Image not found: {filename}", 404
    except Exception as e:
        return f"Error serving image: {str(e)}", 500

@app.route('/')
def home():
    """Enhanced home page with comprehensive paper listing"""
    papers = []
    try:
        if QUESTION_BANKS_DIR.exists():
            for paper_folder in QUESTION_BANKS_DIR.iterdir():
                if paper_folder.is_dir():
                    solutions_file = paper_folder / "solutions.json"
                    if solutions_file.exists():
                        with open(solutions_file, 'r') as f:
                            solutions_data = json.load(f)
                            metadata = solutions_data.get('metadata', {})
                            questions = solutions_data.get('questions', [])
                            
                            if questions:
                                subject = metadata.get('subject', 'Unknown').title()
                                year = metadata.get('year', 'Unknown')
                                month = metadata.get('month', 'Unknown').title()
                                paper_code = metadata.get('paper_code', 'Unknown')
                                
                                total_count = len(questions)
                                solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
                                flagged_count = sum(1 for q in questions if q.get('needs_review', False))
                                
                                # Calculate average confidence
                                solved_questions = [q for q in questions if q.get('solved_by_ai', False)]
                                avg_confidence = 0
                                if solved_questions:
                                    total_confidence = sum(q.get('confidence_score', 0) for q in solved_questions)
                                    avg_confidence = (total_confidence / len(solved_questions)) * 100
                                
                                papers.append({
                                    "folder_name": paper_folder.name,
                                    "title": f"{subject} {year} {month} Paper {paper_code}",
                                    "total_questions": total_count,
                                    "solved_questions": solved_count,
                                    "flagged_questions": flagged_count,
                                    "completion_rate": round((solved_count / total_count) * 100, 1),
                                    "avg_confidence": round(avg_confidence, 1),
                                    "model_used": metadata.get('processing_stats', {}).get('model_used', 'N/A')
                                })
    except Exception as e:
        print(f"Error listing papers: {e}")
    
    api_configured = bool(automated_solver.client)
    
    papers_html = ""
    if papers:
        for paper in papers:
            status_color = "#10b981" if paper["completion_rate"] == 100 else "#f59e0b" if paper["completion_rate"] > 0 else "#ef4444"
            confidence_color = "#10b981" if paper["avg_confidence"] >= 85 else "#f59e0b" if paper["avg_confidence"] >= 70 else "#ef4444"
            
            papers_html += f'''
            <div class="paper-card">
                <div class="paper-info">
                    <h3>{paper["title"]}</h3>
                    <p><strong>Folder:</strong> {paper["folder_name"]}</p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.5rem; margin: 0.5rem 0;">
                        <p><strong>Progress:</strong> <span style="color: {status_color}">{paper["solved_questions"]}/{paper["total_questions"]} ({paper["completion_rate"]}%)</span></p>
                        <p><strong>Flagged:</strong> {paper["flagged_questions"]}</p>
                        <p><strong>Avg Confidence:</strong> <span style="color: {confidence_color}">{paper["avg_confidence"]}%</span></p>
                        <p><strong>Model:</strong> {paper["model_used"]}</p>
                    </div>
                </div>
                <div class="paper-actions">
                    <a href="/solver/{paper["folder_name"]}" class="btn">🤖 Enhanced AI Solver</a>
                </div>
            </div>
            '''
    else:
        papers_html = '<div class="no-papers">No papers found. Please extract questions first.</div>'
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>🤖 Enhanced AI Solver - Claude Sonnet 4</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: rgba(255,255,255,0.95); padding: 2rem; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); backdrop-filter: blur(10px); }}
        .header {{ text-align: center; margin-bottom: 2rem; }}
        .header h1 {{ color: #1e293b; margin-bottom: 0.5rem; font-size: 2.5rem; }}
        .header p {{ color: #64748b; font-size: 1.1rem; }}
        .api-status {{ padding: 1.5rem; margin: 1.5rem 0; border-radius: 12px; text-align: center; }}
        .api-ready {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); }}
        .api-not-ready {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }}
        .paper-card {{ background: white; border: 1px solid #e2e8f0; border-radius: 15px; padding: 2rem; margin: 1.5rem 0; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: all 0.3s ease; }}
        .paper-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); border-color: #6366f1; }}
        .paper-info h3 {{ margin: 0 0 1rem 0; color: #1e293b; font-size: 1.3rem; }}
        .paper-info p {{ margin: 0.25rem 0; color: #64748b; font-size: 0.95rem; }}
        .btn {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 1rem 2rem; border: none; border-radius: 10px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3); }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4); }}
        .no-papers {{ text-align: center; padding: 4rem; color: #64748b; font-size: 1.1rem; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }}
        .stat-card {{ background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 1.5rem; border-radius: 12px; text-align: center; }}
        .stat-card h4 {{ color: #6366f1; margin-bottom: 0.5rem; }}
        .stat-card div {{ font-size: 1.8rem; font-weight: bold; color: #1e293b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Enhanced AI Solver</h1>
            <p>Claude Sonnet 4 Automation • Advanced Image Detection • Quality Control</p>
            <p><small>Model: {CLAUDE_API_MODEL} • Confidence Threshold: {QUALITY_THRESHOLD_DISPLAY}</small></p>
        </div>
        
        <div class="api-status {'api-ready' if api_configured else 'api-not-ready'}">
            <h3>{'✅ Claude Sonnet 4 Ready' if api_configured else '⚠️ Claude API Not Configured'}</h3>
            <p>{'Advanced automation features available' if api_configured else 'Set ANTHROPIC_API_KEY environment variable'}</p>
            {'<p><small>Enhanced reasoning • Superior accuracy • Comprehensive error handling</small></p>' if api_configured else ''}
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h4>Total Papers</h4>
                <div>{len(papers)}</div>
            </div>
            <div class="stat-card">
                <h4>API Status</h4>
                <div>{'Ready' if api_configured else 'Not Ready'}</div>
            </div>
            <div class="stat-card">
                <h4>Model Version</h4>
                <div>Sonnet 4</div>
            </div>
        </div>
        
        {papers_html}
        
        <div style="text-align: center; margin-top: 3rem; padding: 2rem; background: #f8fafc; border-radius: 12px;">
            <h3>🚀 Enhanced Features</h3>
            <ul style="list-style: none; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; text-align: left;">
                <li>✅ Claude Sonnet 4 integration</li>
                <li>🔍 Advanced image detection</li>
                <li>📊 Real-time progress tracking</li>
                <li>💰 Cost tracking & optimization</li>
                <li>⚡ Batch processing with rate limits</li>
                <li>🎯 Quality control & confidence scoring</li>
                <li>📋 Enhanced solution viewer</li>
                <li>📤 Multi-format export (JSON, CSV)</li>
            </ul>
        </div>
    </div>
</body>
</html>'''

if __name__ == '__main__':
    print("🚀 Starting Complete Enhanced AI Solver...")
    print("=" * 70)
    print(f"🤖 Model: {CLAUDE_API_MODEL} (Claude Sonnet 4)")
    print(f"🔑 API Key: {'✅ Configured' if ANTHROPIC_API_KEY else '❌ Missing'}")
    print(f"📂 Question banks: {QUESTION_BANKS_DIR}")
    print(f"🌐 Interface: http://localhost:{FLASK_PORT}")
    print(f"🎯 Confidence threshold: {QUALITY_THRESHOLD_DISPLAY}")
    print(f"🔧 Features: All 1300+ lines with enhanced capabilities")
    print("=" * 70)
    print("🎉 Ready for Claude Sonnet 4 automation!")
    
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=True,
        threaded=True
    )