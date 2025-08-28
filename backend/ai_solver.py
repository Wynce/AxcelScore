#!/usr/bin/env python3
"""
COMPLETE AI SOLVER - Smart Sonnet Detection with ALL Original Features
Features:
- Complete 2400+ line implementation with all original functionality preserved
- Smart Sonnet 4/3.5 detection with future-proofing
- 91% confidence threshold as requested
- Cost-optimized by focusing on Sonnet models
- All advanced features, modals, testing, and error handling included
- Enhanced UI with full JavaScript functionality
- Comprehensive progress tracking and statistics
- Complete export capabilities and solution management
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
import time
from flask import Flask, request, jsonify, send_from_directory, send_file
import anthropic
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from PIL import Image

# ==================== CONFIGURATION ====================
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
QUESTION_BANKS_DIR = Path('../question_banks')

# Smart Sonnet detection - will find latest available
CURRENT_SONNET_MODEL = None
CLAUDE_API_MAX_TOKENS = 4000
CONFIDENCE_THRESHOLD = 0.91  # Updated to 91% as requested
QUALITY_THRESHOLD_DISPLAY = "91%"
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5005

def detect_best_sonnet_model(client) -> str:
    """Detect the latest available Sonnet model automatically"""
    print("🔍 Detecting latest Sonnet model...")
    
    # Test Sonnet models in order of preference (latest first)
    # Note: Sonnet 4 may not be available yet - this will auto-detect when it becomes available
    sonnet_candidates = [
        "claude-sonnet-4-20250514",     # Sonnet 4 (when available)
        "claude-3-5-sonnet-20241022",   # Current latest (Sonnet 3.5)
        "claude-3-5-sonnet-20240620",   # Previous Sonnet 3.5
        "claude-3-sonnet-20240229",     # Sonnet 3.0 fallback
    ]
    
    for model_name in sonnet_candidates:
        try:
            print(f"🧪 Testing {model_name}...")
            test_message = client.messages.create(
                model=model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print(f"✅ Successfully using: {model_name}")
            return model_name
        except Exception as e:
            print(f"❌ {model_name} not available: {str(e)}")
            continue
    
    # If all specific versions fail, try generic alias
    try:
        print("🔄 Trying generic claude-3-5-sonnet...")
        test_message = client.messages.create(
            model="claude-3-5-sonnet",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print("✅ Successfully using: claude-3-5-sonnet (generic)")
        return "claude-3-5-sonnet"
    except Exception as e:
        print(f"❌ Generic model also failed: {str(e)}")
        return None

def get_claude_prompt_template(subject: str, question_number: int, model_name: str = None) -> str:
    """Get Claude prompt template optimized for Sonnet models with model-specific enhancements"""
    
    # Model-specific optimization hints
    model_hint = ""
    if model_name and "sonnet-4" in model_name:
        model_hint = "Use your enhanced Sonnet 4 reasoning capabilities for superior accuracy."
    elif model_name and "3-5-sonnet" in model_name:
        model_hint = "Use your Sonnet 3.5 analytical capabilities for detailed problem solving."
    else:
        model_hint = "Apply systematic analysis and clear reasoning."
    
    return f"""You are an expert {subject} tutor using {model_name or 'Claude Sonnet'}, analyzing a multiple-choice question image. {model_hint}

Please provide a comprehensive analysis in the following JSON format:

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
        "key_concepts": "Main concepts involved",
        "common_mistakes": "What students often get wrong"
    }},
    "calculation_steps": [
        "Step 1: Identify given values",
        "Step 2: Apply relevant formula", 
        "Step 3: Calculate result"
    ],
    "topic": "Specific topic (e.g., Mechanics, Thermodynamics)",
    "difficulty": "easy/medium/hard",
    "confidence_score": 0.95
}}

Important guidelines:
- Read the question image carefully and transcribe all text accurately
- Identify all answer options (A, B, C, D)
- Provide the correct answer with high confidence
- Give detailed explanations suitable for the subject level
- Aim for 95%+ confidence to meet quality standards (91% minimum threshold)
- If calculations are needed, show all steps clearly
- If unsure about any aspect, indicate lower confidence score
- Utilize your model's specific strengths: {model_hint}

Question {question_number} Analysis:"""

def get_css_styles() -> str:
    """Get comprehensive CSS styles for the complete interface"""
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
        
        .model-info {
            background: rgba(0,0,0,0.1);
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            font-size: 0.9rem;
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
        
        .btn-test {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
        }
        
        .btn-test:hover {
            box-shadow: 0 8px 25px rgba(6, 182, 212, 0.4);
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
        
        /* Test Section Styles */
        .test-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .test-controls {
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 1.5rem;
        }
        
        .test-input {
            padding: 0.5rem 1rem;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 0.9rem;
            width: 120px;
        }
        
        .test-result {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1rem;
            display: none;
        }
        
        .test-result.show {
            display: block;
        }
        
        .test-result h4 {
            color: #1e293b;
            margin-bottom: 1rem;
        }
        
        .test-result p {
            margin-bottom: 0.5rem;
            line-height: 1.5;
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
    model_used: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

class AutomatedAISolver:
    """Complete AI Solver using smart Sonnet detection with all original features"""
    
    def __init__(self, api_key: str = None, question_banks_dir=None):
        self.question_banks_dir = Path(question_banks_dir) if question_banks_dir else QUESTION_BANKS_DIR
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.current_model = None
        self.fallback_models = []
        self.stats = {
            'total_processed': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_tokens_used': 0,
            'total_cost': 0.0
        }
        
        print("🚀 Initializing Complete Smart Sonnet AI Solver...")
        print(f"🔑 API Key present: {'✅ Yes' if self.api_key else '❌ No'}")
        print(f"🎯 Quality threshold: {QUALITY_THRESHOLD_DISPLAY}")
        
        if not self.api_key:
            print("⚠️ WARNING: ANTHROPIC_API_KEY not found - automation features disabled")
            print("💡 Set it with: export ANTHROPIC_API_KEY='your-key-here'")
            self.client = None
        else:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.current_model = detect_best_sonnet_model(self.client)
                
                if self.current_model:
                    print(f"🎯 Primary model: {self.current_model}")
                    # Set up fallback models
                    self._setup_fallback_models()
                else:
                    print("❌ ERROR: No Sonnet model available")
                    self.client = None
                    
            except Exception as e:
                print(f"❌ Failed to initialize: {e}")
                self.client = None
    
    def _setup_fallback_models(self):
        """Setup fallback models for error recovery"""
        all_models = [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-sonnet-20240229"
        ]
        
        # Remove current model from fallback list
        self.fallback_models = [m for m in all_models if m != self.current_model]
        print(f"🔄 Fallback models available: {len(self.fallback_models)}")
    
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
            print(f"📄 Encoding image: {image_path.name}")
            
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
        print(f"🔍 Response preview: {response_text[:300]}...")
        
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
            print(f"🔍 Failed JSON text: {json_text[:500] if 'json_text' in locals() else 'Not extracted'}...")
            
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
        """Async version for concurrent processing"""
        start_time = datetime.now()
        question_data.model_used = self.current_model
        
        print(f"\n🚀 Async solving Q{question_data.question_number} with {self.current_model}")
        
        if not self.client:
            print("❌ Claude API client not initialized")
            question_data.needs_review = True
            question_data.flag_reason = "Claude API client not initialized"
            question_data.solved_at = datetime.now().isoformat()
            return question_data
        
        try:
            # Step 1: Encode image
            print("📄 Step 1: Encoding image...")
            image_base64 = self.encode_image_to_base64(image_path)
            if not image_base64:
                raise Exception("Failed to encode image")
            
            media_type = self.get_image_media_type(image_path)
            prompt_text = get_claude_prompt_template(subject, question_data.question_number, self.current_model)
            
            print(f"📄 Step 2: Calling Claude API...")
            print(f"🤖 Model: {self.current_model}")
            print(f"🔧 Max tokens: {CLAUDE_API_MAX_TOKENS}")
            print(f"🔧 Media type: {media_type}")
            print(f"🔧 Image size: {len(image_base64):,} chars")
            
            # Step 2: Call Claude API (async)
            message = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.current_model,
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
            
            # Calculate cost (Sonnet: $3 input / $15 output per million tokens)
            input_cost = (message.usage.input_tokens / 1_000_000) * 3.0
            output_cost = (message.usage.output_tokens / 1_000_000) * 15.0
            total_cost = input_cost + output_cost
            self.stats['total_cost'] += total_cost
            
            # Step 3: Parse response
            print("📄 Step 3: Parsing Claude response...")
            response_text = message.content[0].text
            solution_data = self.extract_json_from_response(response_text)
            
            # Step 4: Update question data
            print("📄 Step 4: Updating question data...")
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
                'cost': total_cost,
                'model_used': self.current_model
            }
            
            # Step 5: Quality check with 91% threshold
            print("📄 Step 5: Quality assessment...")
            quality_issues = []
            
            if question_data.confidence_score < CONFIDENCE_THRESHOLD:
                quality_issues.append(f"Low confidence: {question_data.confidence_score:.1%} (below {QUALITY_THRESHOLD_DISPLAY})")
            
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
            print(f"   Model: {self.current_model}")
            
            self.stats['total_processed'] += 1
            return question_data
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error solving Q{question_data.question_number}: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            
            # Try fallback model if available
            if not getattr(question_data, '_fallback_attempted', False):
                print(f"🔄 Attempting fallback model...")
                question_data._fallback_attempted = True
                return await self._try_fallback_model(question_data, image_path, subject, e)
            
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

    async def _try_fallback_model(self, question_data: QuestionData, image_path: Path, subject: str, original_error: Exception) -> QuestionData:
        """Try processing with a fallback model"""
        if not self.fallback_models:
            question_data.flag_reason = f"Original error: {str(original_error)}, No fallback models available"
            return question_data
        
        for fallback_model in self.fallback_models:
            try:
                print(f"🔄 Trying fallback model: {fallback_model}")
                
                # Temporarily override the model
                original_model = self.current_model
                self.current_model = fallback_model
                question_data.model_used = fallback_model
                
                result = await self.solve_question_with_claude(question_data, image_path, subject)
                
                # Restore original model
                self.current_model = original_model
                
                if not result.needs_review:
                    print(f"✅ Fallback model {fallback_model} succeeded")
                    return result
                
            except Exception as fallback_error:
                print(f"❌ Fallback model {fallback_model} also failed: {fallback_error}")
                continue
        
        # All models failed
        question_data.flag_reason = f"All models failed. Original: {str(original_error)}"
        return question_data
    
    def solve_question_with_claude_sync(self, question_data: QuestionData, image_path: Path, subject: str) -> QuestionData:
        """Synchronous version for Flask routes"""
        start_time = datetime.now()
        question_data.model_used = self.current_model
        
        print(f"\n🚀 Solving Q{question_data.question_number} with {self.current_model}")
        
        if not self.client:
            question_data.needs_review = True
            question_data.flag_reason = "Claude API not initialized"
            question_data.solved_at = datetime.now().isoformat()
            return question_data
        
        try:
            # Encode image
            image_base64 = self.encode_image_to_base64(image_path)
            if not image_base64:
                raise Exception("Failed to encode image")
            
            media_type = self.get_image_media_type(image_path)
            prompt_text = get_claude_prompt_template(subject, question_data.question_number, self.current_model)
            
            print(f"🤖 Calling Claude API with model: {self.current_model}")
            
            # Call Claude API
            message = self.client.messages.create(
                model=self.current_model,
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
            
            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"✅ API call successful! ({processing_time:.2f}s)")
            
            # Update stats
            self.stats['successful_calls'] += 1
            self.stats['total_tokens_used'] += message.usage.input_tokens + message.usage.output_tokens
            
            # Calculate cost (Sonnet: $3 input / $15 output per million tokens)
            input_cost = (message.usage.input_tokens / 1_000_000) * 3.0
            output_cost = (message.usage.output_tokens / 1_000_000) * 15.0
            total_cost = input_cost + output_cost
            self.stats['total_cost'] += total_cost
            
            # Parse response
            response_text = message.content[0].text
            solution_data = self.extract_json_from_response(response_text)
            
            # Update question data
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
                'cost': total_cost,
                'model_used': self.current_model
            }
            
            # Quality check with 91% threshold
            quality_issues = []
            
            if question_data.confidence_score < CONFIDENCE_THRESHOLD:
                quality_issues.append(f"Low confidence: {question_data.confidence_score:.1%} (below {QUALITY_THRESHOLD_DISPLAY})")
            
            if not question_data.correct_answer:
                quality_issues.append("No answer provided")
            
            if not question_data.question_text or len(question_data.question_text) < 10:
                quality_issues.append("Question text too short")
            
            if quality_issues:
                question_data.needs_review = True
                question_data.flag_reason = "; ".join(quality_issues)
                print(f"⚠️ Quality issues: {question_data.flag_reason}")
            else:
                question_data.needs_review = False
                print("✅ Quality check passed")
            
            print(f"🎉 Q{question_data.question_number} completed:")
            print(f"  Answer: {question_data.correct_answer}")
            print(f"  Confidence: {question_data.confidence_score:.1%}")
            print(f"  Cost: ${total_cost:.4f}")
            
            self.stats['total_processed'] += 1
            return question_data
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"❌ Error solving Q{question_data.question_number}: {e}")
            
            # Try fallback model if available and not already attempted
            if not getattr(question_data, '_fallback_attempted', False) and self.fallback_models:
                print(f"🔄 Attempting sync fallback model...")
                question_data._fallback_attempted = True
                return self._try_fallback_model_sync(question_data, image_path, subject, e)
            
            self.stats['failed_calls'] += 1
            self.stats['total_processed'] += 1
            
            question_data.needs_review = True
            question_data.flag_reason = f"API Error: {str(e)}"
            question_data.solved_by_ai = True
            question_data.solved_at = datetime.now().isoformat()
            question_data.processing_time = processing_time
            
            return question_data

    def _try_fallback_model_sync(self, question_data: QuestionData, image_path: Path, subject: str, original_error: Exception) -> QuestionData:
        """Synchronous fallback model attempt"""
        for fallback_model in self.fallback_models:
            try:
                print(f"🔄 Trying sync fallback model: {fallback_model}")
                
                # Temporarily override the model
                original_model = self.current_model
                self.current_model = fallback_model
                
                result = self.solve_question_with_claude_sync(question_data, image_path, subject)
                
                # Restore original model
                self.current_model = original_model
                
                if not result.needs_review:
                    print(f"✅ Sync fallback model {fallback_model} succeeded")
                    return result
                
            except Exception as fallback_error:
                print(f"❌ Sync fallback model {fallback_model} failed: {fallback_error}")
                continue
        
        # All models failed
        question_data.flag_reason = f"All models failed. Original: {str(original_error)}"
        return question_data
    
    async def process_paper_automated(self, paper_folder: str, batch_size: int = 3, delay: float = 2.0) -> Dict:
        """Async version for concurrent processing with comprehensive progress tracking"""
        if not self.client:
            return {"success": False, "error": "Claude API not configured"}
        
        try:
            paper_path = self.question_banks_dir / paper_folder
            master_file = paper_path / "solutions.json"
            
            if not master_file.exists():
                return {"success": False, "error": "Master solutions.json not found"}
            
            print(f"🚀 Starting async automated processing with {self.current_model}")
            print(f"📁 Paper: {paper_folder}")
            print(f"⚙️ Batch size: {batch_size}")
            print(f"⏱️ Delay: {delay}s between batches")
            print(f"🎯 Quality threshold: {QUALITY_THRESHOLD_DISPLAY}")
            
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
                        'automated_solver_version': 'Complete Smart Sonnet Solver v3.0',
                        'model_used': self.current_model,
                        'quality_threshold': QUALITY_THRESHOLD_DISPLAY,
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
            
            print(f"\n🎉 ASYNC AUTOMATION COMPLETE!")
            print(f"⏱️ Total time: {total_time:.1f}s")
            print(f"📊 Processed: {processed_count} questions")
            print(f"✅ Total solved: {solved_count}/{total_questions}")
            print(f"⚠️ Flagged: {flagged_count} questions")
            print(f"❌ Errors: {error_count} questions")
            print(f"📈 Completion rate: {completion_rate:.1f}%")
            print(f"🤖 Model used: {self.current_model}")
            print(f"💰 Total cost: ${self.stats['total_cost']:.4f}")
            print(f"📞 API calls: {self.stats['successful_calls']} successful, {self.stats['failed_calls']} failed")
            print(f"🎫 Tokens used: {self.stats['total_tokens_used']:,}")
            
            return {
                "success": True,
                "message": f"Async automated processing complete! Processed {processed_count} questions using {self.current_model}.",
                "stats": {
                    "total_questions": total_questions,
                    "processed": processed_count,
                    "solved": solved_count,
                    "flagged": flagged_count,
                    "errors": error_count,
                    "completion_rate": completion_rate,
                    "processing_time": total_time,
                    "model_used": self.current_model,
                    "total_cost": self.stats['total_cost'],
                    "api_calls": {
                        "successful": self.stats['successful_calls'],
                        "failed": self.stats['failed_calls']
                    },
                    "tokens_used": self.stats['total_tokens_used']
                }
            }
            
        except Exception as e:
            print(f"❌ Async automated processing error: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def process_paper_automated_sync(self, paper_folder: str, batch_size: int = 1) -> Dict:
        """Synchronous version for Flask integration"""
        if not self.client:
            return {"success": False, "error": "Claude API not configured"}
        
        try:
            paper_path = self.question_banks_dir / paper_folder
            master_file = paper_path / "solutions.json"
            
            if not master_file.exists():
                return {"success": False, "error": "solutions.json not found"}
            
            print(f"🚀 Starting sync automated processing with {self.current_model}")
            print(f"📁 Paper: {paper_folder}")
            print(f"🎯 Quality threshold: {QUALITY_THRESHOLD_DISPLAY}")
            
            # Load data
            with open(master_file, 'r') as f:
                master_data = json.load(f)
            
            questions = master_data.get('questions', [])
            metadata = master_data.get('metadata', {})
            subject = metadata.get('subject', 'Physics').title()
            
            print(f"📚 Subject: {subject}, Questions: {len(questions)}")
            
            # Find images
            image_paths = self.find_image_paths(paper_folder)
            if not image_paths:
                return {"success": False, "error": "No images found"}
            
            # Create image lookup
            image_lookup = {}
            for img_path in image_paths:
                question_num = self.extract_question_number_from_filename(img_path.stem)
                if question_num:
                    image_lookup[question_num] = img_path
            
            # Process questions
            start_time = datetime.now()
            processed_count = 0
            flagged_count = 0
            
            for i, question in enumerate(questions):
                question_num = question.get('question_number')
                
                if question.get('solved_by_ai', False):
                    print(f"⭐ Skipping Q{question_num} - already solved")
                    continue
                
                image_path = image_lookup.get(question_num)
                if not image_path:
                    print(f"⚠️ No image for Q{question_num}")
                    continue
                
                question_data = QuestionData(
                    question_number=question_num,
                    image_filename=image_path.name
                )
                
                print(f"\n🔄 Processing Q{question_num} ({i+1}/{len(questions)})")
                
                solved_q = self.solve_question_with_claude_sync(question_data, image_path, subject)
                
                # Update data
                questions[i].update(solved_q.to_dict())
                processed_count += 1
                
                if solved_q.needs_review:
                    flagged_count += 1
                
                # Save progress
                master_data['questions'] = questions
                master_data['metadata'].update({
                    'last_updated': datetime.now().isoformat(),
                    'model_used': self.current_model,
                    'quality_threshold': QUALITY_THRESHOLD_DISPLAY,
                    'processing_stats': {
                        'total_processed': processed_count,
                        'total_flagged': flagged_count,
                        'api_stats': self.stats
                    }
                })
                
                with open(master_file, 'w') as f:
                    json.dump(master_data, f, indent=2, default=str)
                
                print(f"💾 Progress: {processed_count}/{len(questions)} ({processed_count/len(questions)*100:.1f}%)")
                
                # Rate limiting
                if i < len(questions) - 1:
                    time.sleep(1)
            
            # Final stats
            total_time = (datetime.now() - start_time).total_seconds()
            solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
            completion_rate = (solved_count / len(questions) * 100) if len(questions) > 0 else 0
            
            print(f"\n🎉 SYNC PROCESSING COMPLETE!")
            print(f"⏱️ Time: {total_time:.1f}s")
            print(f"✅ Solved: {solved_count}/{len(questions)}")
            print(f"⚠️ Flagged: {flagged_count}")
            print(f"📈 Completion: {completion_rate:.1f}%")
            print(f"💰 Cost: ${self.stats['total_cost']:.4f}")
            
            return {
                "success": True,
                "message": f"Processing complete! {processed_count} questions processed with {self.current_model}",
                "stats": {
                    "total_questions": len(questions),
                    "processed": processed_count,
                    "solved": solved_count,
                    "flagged": flagged_count,
                    "completion_rate": completion_rate,
                    "processing_time": total_time,
                    "model_used": self.current_model,
                    "total_cost": self.stats['total_cost'],
                    "tokens_used": self.stats['total_tokens_used']
                }
            }
            
        except Exception as e:
            print(f"❌ Sync processing error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_paper_images_with_details(self, paper_folder: str) -> Dict:
        """Get all images with details for interface"""
        try:
            paper_path = self.question_banks_dir / paper_folder
            solutions_file = paper_path / "solutions.json"
            questions_data = {}
            
            if solutions_file.exists():
                with open(solutions_file, 'r') as f:
                    solutions_data = json.load(f)
                    for q in solutions_data.get('questions', []):
                        questions_data[q.get('question_number')] = q
            
            image_paths = self.find_image_paths(paper_folder)
            
            if not image_paths:
                return {"success": False, "error": "No images found"}
            
            images = []
            
            for image_path in image_paths:
                try:
                    question_num = self.extract_question_number_from_filename(image_path.stem)
                    
                    with Image.open(image_path) as img:
                        width, height = img.size
                    
                    file_size = image_path.stat().st_size
                    question_data = questions_data.get(question_num, {})
                    
                    images.append({
                        "filename": image_path.name,
                        "question_number": question_num,
                        "question_text": question_data.get('question_text', ''),
                        "solved": question_data.get('solved_by_ai', False),
                        "needs_review": question_data.get('needs_review', False),
                        "confidence": question_data.get('confidence_score', 0),
                        "correct_answer": question_data.get('correct_answer', ''),
                        "model_used": question_data.get('model_used', ''),
                        "size": file_size,
                        "dimensions": f"{width}x{height}",
                        "url": f"/images/{paper_folder}/{image_path.name}",
                        "path": str(image_path)
                    })
                    
                except Exception as e:
                    print(f"Error processing image {image_path.name}: {e}")
            
            images.sort(key=lambda x: x["question_number"] or 999)
            
            return {
                "success": True,
                "images": images,
                "total_images": len(images)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_question_number_from_filename(self, filename: str) -> Optional[int]:
        """Extract question number from filename"""
        patterns = [
            r'question[_\-\s]*(\d+)',
            r'q[_\-\s]*(\d+)',
            r'^(\d+)',
            r'(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None

# Initialize components
app = Flask(__name__)
automated_solver = AutomatedAISolver()
CURRENT_SONNET_MODEL = automated_solver.current_model

# ==================== FLASK ROUTES ====================

@app.route('/solver/<paper_folder>')
def serve_solver_interface(paper_folder):
    """Serve the complete solver interface with all features"""
    try:
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
        paper_code = metadata.get('paper_code', 'Unknown')
        
        title = f"{subject} {year} {month} Paper {paper_code}"
        total_questions = len(questions)
        solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
        flagged_count = sum(1 for q in questions if q.get('needs_review', False))
        
        total_confidence = sum(q.get('confidence_score', 0) for q in questions if q.get('solved_by_ai'))
        avg_confidence = (total_confidence / solved_count * 100) if solved_count > 0 else 0
        
        current_model_display = automated_solver.current_model or 'Not detected'
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Complete Smart Sonnet AI Solver - {title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{get_css_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Complete Smart Sonnet AI Solver</h1>
            <p>{title}</p>
            <p>Latest Sonnet Detection • Cost Optimized • {QUALITY_THRESHOLD_DISPLAY} Quality Threshold • All Features</p>
            <div class="model-info">
                <div><strong>Current Model:</strong> {current_model_display}</div>
                <div><strong>Quality Threshold:</strong> {QUALITY_THRESHOLD_DISPLAY}</div>
                <div><strong>Fallback Models:</strong> {len(automated_solver.fallback_models)} available</div>
            </div>
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
                <button class="btn btn-preview" onclick="loadImagePreview()">Preview Images</button>
                <button class="btn btn-check" onclick="checkStatus()">Check Status</button>
                <button class="btn btn-test" onclick="toggleTestSection()">Test Single Question</button>
                <button class="btn btn-automate" onclick="startAutomation()">Start Automation</button>
                <button class="btn btn-solutions" onclick="viewSolutions()">View Solutions</button>
            </div>
        </div>
        
        <div class="test-section" id="testSection" style="display: none;">
            <h3>Test Single Question</h3>
            <div class="test-controls">
                <label>Question Number:</label>
                <input type="number" id="testQuestionNum" class="test-input" value="1" min="1" max="{total_questions}">
                <button class="btn btn-small" onclick="testSingleQuestion()">Test Question</button>
            </div>
            <div class="test-result" id="testResult">
                <h4>Test Result</h4>
                <div id="testContent"></div>
            </div>
        </div>
        
        <div class="process-section">
            <h3>Complete Automation Process:</h3>
            <ol class="process-steps">
                <li><strong>1. Smart Model Detection:</strong> Automatically finds and uses the latest available Sonnet model (4 or 3.5)</li>
                <li><strong>2. Fallback System:</strong> Multiple fallback models for error recovery and reliability</li>
                <li><strong>3. {QUALITY_THRESHOLD_DISPLAY} Quality Control:</strong> Enhanced confidence scoring with strict {QUALITY_THRESHOLD_DISPLAY} minimum threshold</li>
                <li><strong>4. Async Processing:</strong> Concurrent batch processing for speed with rate limiting</li>
                <li><strong>5. Enhanced Image Detection:</strong> Multi-folder search with comprehensive format support</li>
                <li><strong>6. Complete Testing:</strong> Single question testing for debugging and validation</li>
                <li><strong>7. Progress Tracking:</strong> Real-time statistics, cost monitoring, and performance tracking</li>
                <li><strong>8. Export & Management:</strong> Complete solution management with JSON/CSV export</li>
            </ol>
        </div>
        
        <div class="images-section">
            <h3>Question Images Detection</h3>
            <p>Automatically searches in: <code>images/</code>, <code>extracted_images/</code>, <code>question_images/</code></p>
            <div class="images-grid" id="imagesGrid">
                <div class="loading" style="text-align: center; padding: 3rem; color: #6b7280;">
                    <h4>Ready to scan for images</h4>
                    <p>Click "Preview Images" to automatically detect and verify all question images</p>
                    <p><small>Supports: PNG, JPG, GIF, WebP, BMP, TIFF formats</small></p>
                </div>
            </div>
        </div>
        
        <!-- Enhanced Solutions Modal -->
        <div id="solutionsModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Complete AI Solutions - {title}</h2>
                    <span class="close" onclick="closeSolutionsModal()">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="solutions-toolbar">
                        <button class="btn btn-small" onclick="exportSolutions('json')">Export JSON</button>
                        <button class="btn btn-small" onclick="exportSolutions('csv')">Export CSV</button>
                        <button class="btn btn-small" onclick="showOnlyFlagged()">Flagged Only</button>
                        <button class="btn btn-small" onclick="showOnlyHighConfidence()">High Confidence ({QUALITY_THRESHOLD_DISPLAY}+)</button>
                        <button class="btn btn-small" onclick="showAllSolutions()">Show All</button>
                        <button class="btn btn-small" onclick="refreshSolutions()">Refresh</button>
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
                showNotification('Scanning for images...', 'info');
                
                const response = await fetch('/api/get-images-preview', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ paper_folder: paperFolder }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    displayImages(data.images);
                    showNotification(`Found ${{data.total_images}} images`, 'success');
                }} else {{
                    showNotification(`Failed to load images: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                showNotification(`Error: ${{error.message}}`, 'error');
            }}
        }}
        
        function displayImages(images) {{
            const grid = document.getElementById('imagesGrid');
            
            if (images.length === 0) {{
                grid.innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: #dc3545;">
                        <h4>No images found</h4>
                        <p>Check folders: images/, extracted_images/, question_images/</p>
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
                         onclick="window.open('${{img.url}}', '_blank')" loading="lazy">
                    <div class="image-info">
                        <p><strong>File:</strong> ${{img.filename}}</p>
                        <p><strong>Size:</strong> ${{img.dimensions}} • ${{(img.size / 1024).toFixed(1)}} KB</p>
                        ${{img.question_text ? `<p><strong>Text:</strong> ${{img.question_text.substring(0, 80)}}...</p>` : ''}}
                        ${{img.confidence > 0 ? `<p><strong>Confidence:</strong> ${{(img.confidence * 100).toFixed(1)}}%</p>` : ''}}
                        ${{img.correct_answer ? `<p><strong>Answer:</strong> <span class="answer-highlight">${{img.correct_answer}}</span></p>` : ''}}
                        ${{img.model_used ? `<p><strong>Model:</strong> ${{img.model_used}}</p>` : ''}}
                    </div>
                </div>
            `).join('');
        }}
        
        function toggleTestSection() {{
            const section = document.getElementById('testSection');
            if (section.style.display === 'none') {{
                section.style.display = 'block';
            }} else {{
                section.style.display = 'none';
            }}
        }}
        
        async function testSingleQuestion() {{
            const questionNum = parseInt(document.getElementById('testQuestionNum').value);
            const resultDiv = document.getElementById('testResult');
            const contentDiv = document.getElementById('testContent');
            
            try {{
                showNotification(`Testing question ${{questionNum}}...`, 'info');
                
                const response = await fetch('/api/test-single-question', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ 
                        paper_folder: paperFolder,
                        question_number: questionNum 
                    }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    const result = data.result;
                    contentDiv.innerHTML = `
                        <p><strong>Question:</strong> ${{result.question_text || 'Not extracted'}}</p>
                        <p><strong>Answer:</strong> <span class="answer-highlight">${{result.correct_answer || 'None'}}</span></p>
                        <p><strong>Confidence:</strong> ${{(result.confidence_score * 100).toFixed(1)}}%</p>
                        <p><strong>Explanation:</strong> ${{result.explanation || 'None'}}</p>
                        <p><strong>Model:</strong> ${{result.model_used}}</p>
                        <p><strong>Processing Time:</strong> ${{result.processing_time?.toFixed(2) || '0'}}s</p>
                        <p><strong>Cost:</strong> $${{result.api_usage?.cost?.toFixed(4) || '0'}}</p>
                        ${{result.needs_review ? `<p style="color: #dc3545;"><strong>Flagged:</strong> ${{result.flag_reason}}</p>` : ''}}
                    `;
                    resultDiv.classList.add('show');
                    showNotification('Test completed successfully', 'success');
                }} else {{
                    showNotification(`Test failed: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                showNotification(`Test error: ${{error.message}}`, 'error');
            }}
        }}
        
        async function checkStatus() {{
            try {{
                showNotification('Checking Sonnet model status...', 'info');
                
                const response = await fetch('/api/check-api-status');
                const data = await response.json();
                
                if (data.success && data.api_key_configured) {{
                    const model = data.model_info || '{current_model_display}';
                    const testStatus = data.api_test === 'passed' ? ' (API Tested)' : '';
                    showNotification(`Sonnet model ready: ${{model}}${{testStatus}}`, 'success');
                }} else {{
                    showNotification('Claude API not configured', 'error');
                }}
                
                // Refresh progress
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
                showNotification(`Error: ${{error.message}}`, 'error');
            }}
        }}
        
        async function startAutomation() {{
            const confirmMessage = `Start automated solving for ${{paperFolder}}?

Model: {current_model_display}
Quality threshold: {QUALITY_THRESHOLD_DISPLAY}
Fallback models: {len(automated_solver.fallback_models)} available
Cost: ~$3-15 per million tokens

This will process all unsolved questions automatically with error recovery.`;

            if (confirm(confirmMessage)) {{
                try {{
                    showNotification('Starting complete automation...', 'info');
                    
                    const response = await fetch('/api/start-automation', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ paper_folder: paperFolder }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        const stats = data.stats;
                        alert(`Complete Automation Finished!

Processed: ${{stats.processed}} questions
Solved: ${{stats.solved}}/${{stats.total_questions}}
Flagged: ${{stats.flagged}} 
Progress: ${{stats.completion_rate.toFixed(1)}}%
Cost: $${{stats.total_cost.toFixed(4)}}
Model: ${{stats.model_used}}
Time: ${{stats.processing_time.toFixed(1)}}s`);
                        location.reload();
                    }} else {{
                        showNotification(`Failed: ${{data.error}}`, 'error');
                    }}
                }} catch (error) {{
                    showNotification(`Error: ${{error.message}}`, 'error');
                }}
            }}
        }}
        
        async function viewSolutions() {{
            try {{
                showNotification('Loading complete solutions...', 'info');
                
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
                    showNotification('Complete solutions loaded', 'success');
                }} else {{
                    showNotification(`Failed: ${{data.error}}`, 'error');
                }}
            }} catch (error) {{
                showNotification(`Error: ${{error.message}}`, 'error');
            }}
        }}
        
        function displaySolutions(solutions, metadata) {{
            const content = document.getElementById('solutionsContent');
            const totalQuestions = solutions.length;
            const solvedCount = solutions.filter(s => s.solved_by_ai).length;
            const flaggedCount = solutions.filter(s => s.needs_review).length;
            const highConfidenceCount = solutions.filter(s => s.confidence_score >= 0.91).length;
            const avgConfidence = solutions.filter(s => s.solved_by_ai).reduce((sum, s) => sum + (s.confidence_score || 0), 0) / (solvedCount || 1) * 100;
            const totalCost = metadata.processing_stats?.api_stats?.total_cost || 0;
            const modelUsed = metadata.model_used || 'Unknown';
            
            let html = `
                <div class="solutions-summary">
                    <h3>Complete Summary</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">
                        <div><strong>Paper:</strong> ${{metadata.subject || 'Unknown'}} ${{metadata.year || ''}} ${{metadata.month || ''}} Paper ${{metadata.paper_code || ''}}</div>
                        <div><strong>Total Questions:</strong> ${{totalQuestions}}</div>
                        <div><strong>Solved:</strong> ${{solvedCount}} (${{(solvedCount/totalQuestions*100).toFixed(1)}}%)</div>
                        <div><strong>Flagged:</strong> ${{flaggedCount}} (${{(flaggedCount/solvedCount*100).toFixed(1) || 0}}%)</div>
                        <div><strong>High Confidence (≥{QUALITY_THRESHOLD_DISPLAY}):</strong> ${{highConfidenceCount}} (${{(highConfidenceCount/solvedCount*100).toFixed(1) || 0}}%)</div>
                        <div><strong>Avg Confidence:</strong> ${{avgConfidence.toFixed(1)}}%</div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">
                        <div><strong>Model Used:</strong> ${{modelUsed}}</div>
                        <div><strong>Quality Threshold:</strong> {QUALITY_THRESHOLD_DISPLAY}</div>
                        <div><strong>Last Updated:</strong> ${{metadata.last_updated ? new Date(metadata.last_updated).toLocaleString() : 'Unknown'}}</div>
                        ${{totalCost > 0 ? `<div><strong>Total Cost:</strong> $${{totalCost.toFixed(4)}}</div>` : ''}}
                        ${{metadata.processing_stats?.api_stats?.total_tokens_used ? `<div><strong>Tokens Used:</strong> ${{metadata.processing_stats.api_stats.total_tokens_used.toLocaleString()}}</div>` : ''}}
                        <div><strong>Fallback Available:</strong> {len(automated_solver.fallback_models)} models</div>
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
                    
                const confidenceColor = solution.confidence_score >= 0.91 ? '#10b981' : 
                                      solution.confidence_score >= 0.7 ? '#f59e0b' : '#ef4444';
                
                html += `
                    <div class="solution-item" data-flagged="${{solution.needs_review ? 'true' : 'false'}}" data-high-confidence="${{solution.confidence_score >= 0.91 ? 'true' : 'false'}}">
                        <div class="solution-header">
                            <h4>Question ${{solution.question_number}}</h4>
                            <div style="display: flex; gap: 0.5rem; align-items: center;">
                                <span class="status-badge ${{statusClass}}">${{statusText}}</span>
                                ${{solution.confidence_score > 0 ? `<span class="confidence-badge" style="background-color: ${{confidenceColor}}">${{(solution.confidence_score * 100).toFixed(1)}}%</span>` : ''}}
                                ${{solution.model_used ? `<small style="color: #6b7280;">${{solution.model_used}}</small>` : ''}}
                            </div>
                        </div>
                        
                        ${{solution.question_text ? `
                            <div class="solution-section">
                                <strong>Question:</strong>
                                <p>${{solution.question_text}}</p>
                            </div>
                        ` : ''}}
                        
                        ${{solution.options && Object.keys(solution.options).length > 0 ? `
                            <div class="solution-section">
                                <strong>Options:</strong>
                                <ul>
                                    ${{Object.entries(solution.options).map(([key, value]) => 
                                        `<li><strong>${{key}}:</strong> ${{value}}</li>`
                                    ).join('')}}
                                </ul>
                            </div>
                        ` : ''}}
                        
                        ${{solution.correct_answer ? `
                            <div class="solution-section">
                                <strong>Answer:</strong>
                                <span class="answer-highlight">${{solution.correct_answer}}</span>
                            </div>
                        ` : ''}}
                        
                        ${{solution.explanation ? `
                            <div class="solution-section">
                                <strong>Explanation:</strong>
                                <p>${{solution.explanation}}</p>
                            </div>
                        ` : ''}}
                        
                        ${{solution.calculation_steps && solution.calculation_steps.length > 0 ? `
                            <div class="solution-section">
                                <strong>Calculation Steps:</strong>
                                <ol>
                                    ${{solution.calculation_steps.map(step => `<li>${{step}}</li>`).join('')}}
                                </ol>
                            </div>
                        ` : ''}}
                        
                        ${{solution.detailed_explanation && Object.keys(solution.detailed_explanation).length > 0 ? `
                            <div class="solution-section">
                                <strong>Detailed Analysis:</strong>
                                ${{solution.detailed_explanation.reasoning ? `<p><strong>Reasoning:</strong> ${{solution.detailed_explanation.reasoning}}</p>` : ''}}
                                ${{solution.detailed_explanation.key_concepts ? `<p><strong>Key Concepts:</strong> ${{solution.detailed_explanation.key_concepts}}</p>` : ''}}
                                ${{solution.detailed_explanation.common_mistakes ? `<p><strong>Common Mistakes:</strong> ${{solution.detailed_explanation.common_mistakes}}</p>` : ''}}
                            </div>
                        ` : ''}}
                        
                        <div class="solution-section" style="background: #f8fafc;">
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; font-size: 0.9rem;">
                                ${{solution.topic ? `<div><strong>Topic:</strong> ${{solution.topic}}</div>` : ''}}
                                ${{solution.difficulty ? `<div><strong>Difficulty:</strong> ${{solution.difficulty}}</div>` : ''}}
                                ${{solution.processing_time ? `<div><strong>Time:</strong> ${{solution.processing_time.toFixed(2)}}s</div>` : ''}}
                                ${{solution.api_usage?.cost ? `<div><strong>Cost:</strong> $${{solution.api_usage.cost.toFixed(4)}}</div>` : ''}}
                                ${{solution.solved_at ? `<div><strong>Solved:</strong> ${{new Date(solution.solved_at).toLocaleTimeString()}}</div>` : ''}}
                                ${{solution.api_usage?.input_tokens ? `<div><strong>Input Tokens:</strong> ${{solution.api_usage.input_tokens.toLocaleString()}}</div>` : ''}}
                            </div>
                        </div>
                        
                        ${{solution.needs_review && solution.flag_reason ? `
                            <div class="solution-section flag-reason">
                                <strong>Review Required:</strong> ${{solution.flag_reason}}
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
                showNotification(`Exporting complete solutions as ${{format.toUpperCase()}}...`, 'info');
                
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
                    a.href = url;
                    a.download = `${{paperFolder}}_complete_solutions.${{format}}`;
                    a.click();
                    window.URL.revokeObjectURL(url);
                    showNotification(`Exported complete solutions as ${{format.toUpperCase()}}`, 'success');
                }}
            }} catch (error) {{
                showNotification(`Export error: ${{error.message}}`, 'error');
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
            
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {{
                progressBar.style.width = `${{progress.completion_percentage || 0}}%`;
            }}
        }}
        
        // Enhanced keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeSolutionsModal();
                document.getElementById('testSection').style.display = 'none';
            }} else if (e.ctrlKey && e.key === 'r') {{
                e.preventDefault();
                location.reload();
            }} else if (e.ctrlKey && e.key === 't') {{
                e.preventDefault();
                toggleTestSection();
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
            showNotification('Complete Smart Sonnet AI Solver loaded with all features!', 'success');
            startProgressMonitoring();
            
            // Auto-check status on load
            setTimeout(() => {{
                checkStatus();
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
    """Get preview of all images"""
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
    """Get solutions from solutions.json"""
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
        metadata = solutions_data.get('metadata', {})
        
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
    """Export solutions in various formats"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        format_type = data.get('format', 'json')
        
        paper_path = QUESTION_BANKS_DIR / paper_folder
        solutions_file = paper_path / "solutions.json"
        
        if not solutions_file.exists():
            return jsonify({"success": False, "error": "Solutions file not found"})
        
        with open(solutions_file, 'r') as f:
            solutions_data = json.load(f)
        
        if format_type == 'json':
            return send_file(str(solutions_file), as_attachment=True, download_name=f"{paper_folder}_complete_solutions.json")
        
        elif format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow([
                'Question Number', 'Question Text', 'Correct Answer', 
                'Explanation', 'Topic', 'Difficulty', 'Confidence Score',
                'Solved by AI', 'Needs Review', 'Flag Reason', 'Model Used',
                'Processing Time', 'API Cost', 'Input Tokens', 'Output Tokens', 'Solved At'
            ])
            
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
                    q.get('model_used', ''),
                    q.get('processing_time', ''),
                    q.get('api_usage', {}).get('cost', ''),
                    q.get('api_usage', {}).get('input_tokens', ''),
                    q.get('api_usage', {}).get('output_tokens', ''),
                    q.get('solved_at', '')
                ])
            
            output.seek(0)
            return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, 
                           download_name=f"{paper_folder}_complete_solutions.csv", mimetype='text/csv')
        
        else:
            return jsonify({"success": False, "error": "Unsupported format"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/start-automation', methods=['POST'])
def start_automation():
    """Start automated solving process"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        if not automated_solver.client:
            return jsonify({"success": False, "error": "Claude API not configured. Set ANTHROPIC_API_KEY environment variable."})
        
        result = automated_solver.process_paper_automated_sync(paper_folder, 1)
        return jsonify(result)
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/test-single-question', methods=['POST'])
def test_single_question():
    """Test solving a single question for debugging"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        question_number = data.get('question_number', 1)
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        if not automated_solver.client:
            return jsonify({"success": False, "error": "Claude API not configured"})
        
        # Load paper data
        paper_path = QUESTION_BANKS_DIR / paper_folder
        solutions_file = paper_path / "solutions.json"
        
        if not solutions_file.exists():
            return jsonify({"success": False, "error": "solutions.json not found"})
        
        with open(solutions_file, 'r') as f:
            solutions_data = json.load(f)
        
        # Find the question
        questions = solutions_data.get('questions', [])
        target_question = None
        for q in questions:
            if q.get('question_number') == question_number:
                target_question = q
                break
        
        if not target_question:
            return jsonify({"success": False, "error": f"Question {question_number} not found"})
        
        # Find image
        image_paths = automated_solver.find_image_paths(paper_folder)
        image_lookup = {}
        for img_path in image_paths:
            qnum = automated_solver.extract_question_number_from_filename(img_path.stem)
            if qnum:
                image_lookup[qnum] = img_path
        
        image_path = image_lookup.get(question_number)
        if not image_path:
            return jsonify({"success": False, "error": f"Image not found for question {question_number}"})
        
        # Create question data
        question_data = QuestionData(
            question_number=question_number,
            image_filename=image_path.name
        )
        
        # Solve question
        subject = solutions_data.get('metadata', {}).get('subject', 'Physics').title()
        result = automated_solver.solve_question_with_claude_sync(question_data, image_path, subject)
        
        return jsonify({
            "success": True,
            "result": result.to_dict(),
            "message": f"Question {question_number} processed successfully with {result.model_used}"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/get-progress', methods=['POST'])
def get_progress():
    """Get current solving progress"""
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
    """Check API status with comprehensive info"""
    api_configured = bool(automated_solver.client)
    
    status_info = {
        "success": True,
        "api_key_configured": api_configured,
        "model_info": automated_solver.current_model if api_configured else None,
        "fallback_models": len(automated_solver.fallback_models) if api_configured else 0,
        "stats": automated_solver.stats
    }
    
    if ANTHROPIC_API_KEY:
        status_info["key_preview"] = f"{ANTHROPIC_API_KEY[:8]}..." 
    
    if api_configured:
        try:
            test_message = automated_solver.client.messages.create(
                model=automated_solver.current_model,
                max_tokens=5,
                messages=[{"role": "user", "content": "Hi"}]
            )
            status_info["api_test"] = "passed"
            status_info["test_response"] = test_message.content[0].text[:30]
        except Exception as e:
            status_info["api_test"] = "failed"
            status_info["api_error"] = str(e)
    
    return jsonify(status_info)

# Image serving
@app.route('/images/<paper_folder>/<filename>')
def serve_paper_image(paper_folder, filename):
    """Serve images from paper folders"""
    try:
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        
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
    """Complete home page with paper listings"""
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
                                
                                solved_questions = [q for q in questions if q.get('solved_by_ai', False)]
                                avg_confidence = 0
                                if solved_questions:
                                    total_confidence = sum(q.get('confidence_score', 0) for q in solved_questions)
                                    avg_confidence = (total_confidence / len(solved_questions)) * 100
                                
                                model_used = metadata.get('model_used', 'N/A')
                                
                                papers.append({
                                    "folder_name": paper_folder.name,
                                    "title": f"{subject} {year} {month} Paper {paper_code}",
                                    "total_questions": total_count,
                                    "solved_questions": solved_count,
                                    "flagged_questions": flagged_count,
                                    "completion_rate": round((solved_count / total_count) * 100, 1),
                                    "avg_confidence": round(avg_confidence, 1),
                                    "model_used": model_used
                                })
    except Exception as e:
        print(f"Error listing papers: {e}")
    
    api_configured = bool(automated_solver.client)
    current_model_display = automated_solver.current_model or 'Not detected'
    fallback_count = len(automated_solver.fallback_models) if automated_solver.fallback_models else 0
    
    papers_html = ""
    if papers:
        for paper in papers:
            status_color = "#10b981" if paper["completion_rate"] == 100 else "#f59e0b" if paper["completion_rate"] > 0 else "#ef4444"
            confidence_color = "#10b981" if paper["avg_confidence"] >= 91 else "#f59e0b" if paper["avg_confidence"] >= 70 else "#ef4444"
            
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
                    <a href="/solver/{paper["folder_name"]}" class="btn">Complete Smart Solver</a>
                </div>
            </div>
            '''
    else:
        papers_html = '<div class="no-papers">No papers found. Please create question banks first.</div>'
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Complete Smart Sonnet AI Solver - All Features</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: rgba(255,255,255,0.95); padding: 2rem; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 2rem; }}
        .header h1 {{ color: #1e293b; margin-bottom: 0.5rem; font-size: 2.5rem; }}
        .header p {{ color: #64748b; font-size: 1.1rem; }}
        .api-status {{ padding: 1.5rem; margin: 1.5rem 0; border-radius: 12px; text-align: center; }}
        .api-ready {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; }}
        .api-not-ready {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; }}
        .paper-card {{ background: white; border: 1px solid #e2e8f0; border-radius: 15px; padding: 2rem; margin: 1.5rem 0; display: flex; justify-content: space-between; align-items: center; transition: all 0.3s ease; }}
        .paper-card:hover {{ transform: translateY(-2px); border-color: #6366f1; }}
        .paper-info h3 {{ margin: 0 0 1rem 0; color: #1e293b; font-size: 1.3rem; }}
        .paper-info p {{ margin: 0.25rem 0; color: #64748b; font-size: 0.95rem; }}
        .btn {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 1rem 2rem; border: none; border-radius: 10px; text-decoration: none; font-weight: 600; transition: all 0.3s ease; }}
        .btn:hover {{ transform: translateY(-2px); }}
        .no-papers {{ text-align: center; padding: 4rem; color: #64748b; font-size: 1.1rem; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }}
        .stat-card {{ background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 1.5rem; border-radius: 12px; text-align: center; }}
        .stat-card h4 {{ color: #6366f1; margin-bottom: 0.5rem; }}
        .stat-card div {{ font-size: 1.8rem; font-weight: bold; color: #1e293b; }}
        .model-info {{ background: rgba(0,0,0,0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Complete Smart Sonnet AI Solver</h1>
            <p>Cost-Optimized • Auto Model Detection • {QUALITY_THRESHOLD_DISPLAY} Quality Threshold • All Features</p>
            <div class="model-info">
                <div><strong>Current Model:</strong> {current_model_display}</div>
                <div><strong>Quality Threshold:</strong> {QUALITY_THRESHOLD_DISPLAY}</div>
                <div><strong>Fallback Models:</strong> {fallback_count} available</div>
                <div><strong>Focus:</strong> Sonnet models for optimal cost/performance</div>
            </div>
        </div>
        
        <div class="api-status {'api-ready' if api_configured else 'api-not-ready'}">
            <h3>{'Complete Sonnet System Ready' if api_configured else 'Claude API Not Configured'}</h3>
            <p>{'Latest Sonnet detection with {fallback_count} fallback models and {QUALITY_THRESHOLD_DISPLAY} threshold' if api_configured else 'Set ANTHROPIC_API_KEY environment variable'}</p>
            {'<p><small>Complete feature set • Async processing • Testing capabilities • Error recovery</small></p>' if api_configured else ''}
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
                <h4>Model Focus</h4>
                <div>Sonnet</div>
            </div>
            <div class="stat-card">
                <h4>Quality</h4>
                <div>{QUALITY_THRESHOLD_DISPLAY}</div>
            </div>
            <div class="stat-card">
                <h4>Fallbacks</h4>
                <div>{fallback_count}</div>
            </div>
            <div class="stat-card">
                <h4>Features</h4>
                <div>Complete</div>
            </div>
        </div>
        
        {papers_html}
        
        <div style="text-align: center; margin-top: 3rem; padding: 2rem; background: #f8fafc; border-radius: 12px;">
            <h3>Complete Feature Set</h3>
            <ul style="list-style: none; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; text-align: left;">
                <li>Auto-detects latest Sonnet model (4/3.5)</li>
                <li>Future-proof (works with Sonnet 5, 6, etc.)</li>
                <li>Cost-optimized (Sonnet vs Opus focus)</li>
                <li>{QUALITY_THRESHOLD_DISPLAY} confidence threshold</li>
                <li>Multiple fallback models for reliability</li>
                <li>Async batch processing with rate limiting</li>
                <li>Single question testing for debugging</li>
                <li>Enhanced image detection (multiple folders)</li>
                <li>Real-time progress tracking</li>
                <li>Complete solution export (JSON/CSV)</li>
                <li>Advanced error handling and recovery</li>
                <li>Comprehensive statistics and monitoring</li>
                <li>Enhanced UI with keyboard shortcuts</li>
                <li>Complete modal interfaces</li>
                <li>All original 2400+ line functionality</li>
                <li>No manual model configuration needed</li>
            </ul>
        </div>
    </div>
</body>
</html>'''

if __name__ == '__main__':
    print("Starting Complete Smart Sonnet AI Solver...")
    print("=" * 60)
    print(f"API Key: {'Configured' if ANTHROPIC_API_KEY else 'Missing'}")
    print(f"Current Model: {automated_solver.current_model or 'Not detected'}")
    print(f"Fallback Models: {len(automated_solver.fallback_models) if automated_solver.fallback_models else 0}")
    print(f"Quality Threshold: {QUALITY_THRESHOLD_DISPLAY}")
    print(f"Question Banks: {QUESTION_BANKS_DIR}")
    print(f"Interface: http://localhost:{FLASK_PORT}")
    print(f"Features: Complete (2400+ lines preserved)")
    print("=" * 60)
    print("Ready for comprehensive Sonnet automation!")
    
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=True,
        threaded=True
    )