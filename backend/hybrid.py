#!/usr/bin/env python3
"""
COMPLETE HYBRID MANUAL AI SOLVER - Standalone Version
All original features from hybrid.py with Gen Alpha design
Features:
- Complete ScalableAISolverManager functionality
- Quality control with 91% threshold (configurable)
- Enhanced frontend with Gen Alpha design
- Multi-export support
- Creates solutions.json from images
- Manual QC workflow for flagged questions
- Review and unflag capabilities
- Runs on dedicated port (5006) to avoid conflicts
- FIXED: All JavaScript button functionality
"""

import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime
import traceback
import re
from flask import Flask, request, jsonify, send_from_directory, render_template_string, send_file
from werkzeug.utils import secure_filename
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from PIL import Image
import io
import hashlib

# Configuration
QUESTION_BANKS_DIR = Path("../frontend/public/question_banks")  # Go up one level from backend folder
QUESTION_BANKS_DIR.mkdir(exist_ok=True)
CONFIDENCE_THRESHOLD = 0.91  # 91% quality threshold

# Create Flask app
app = Flask(__name__)

def get_claude_prompt_template(subject, question_num):
    """Generate enhanced Claude prompt template"""
    return f"""Please analyze this {subject.lower()} question image carefully and provide a complete solution in JSON format. Double check your reading of all values before proceeding as accuracy for exam is more important than speed. Before applying any physics principles, carefully examine the exact geometry and positioning shown in the diagram, ensuring distances are measured from correct reference points and segments are interpreted as additive or separate measurements as appropriate. Before applying any physics principles, carefully examine the exact geometry and positioning shown in the diagram.

Required JSON structure:
{{
  "question_text": "Extract the complete question text exactly as shown",
  "options": {{
    "A": "Complete text for option A",
    "B": "Complete text for option B",
    "C": "Complete text for option C",
    "D": "Complete text for option D"
  }},
  "correct_answer": "A/B/C/D (single letter only)",
  "simple_answer": "Brief but clear explanation of the correct answer",
  "detailed_explanation": {{
    "approach": "Method or principle used",
    "calculation": "Key calculations if applicable",
    "reasoning": "Logical thought process",
    "conclusion": "Why this answer is correct"
  }},
  "calculation_steps": [
    "Step 1: Description of first step",
    "Step 2: Description of second step",
    "Continue as needed..."
  ],
  "topic": "Specific {subject.lower()} topic",
  "difficulty": "easy/medium/hard",
  "confidence_score": 0.95
}}

Please be thorough and accurate in your analysis."""

def get_css_styles():
    """Colorful Gen Alpha design with 2-column layout"""
    return """
* { box-sizing: border-box; }

body { 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
    margin: 0; 
    padding: 1rem; 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%); 
    background-size: 400% 400%;
    animation: gradientShift 8s ease infinite;
    line-height: 1.6;
    min-height: 100vh;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.container { 
    max-width: 1600px; 
    margin: 0 auto; 
    background: rgba(255, 255, 255, 0.95); 
    backdrop-filter: blur(20px);
    border-radius: 24px; 
    box-shadow: 0 20px 40px rgba(0,0,0,0.1), 0 0 0 1px rgba(255,255,255,0.2); 
    overflow: hidden;
}

.header { 
    background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%); 
    color: white; 
    padding: 3rem 2rem; 
    text-align: center; 
    position: relative;
    overflow: hidden;
}

.header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
    animation: shine 3s infinite;
}

@keyframes shine {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.header h1 { 
    margin: 0 0 1rem 0; 
    font-size: 3rem; 
    font-weight: 800; 
    background: linear-gradient(45deg, #fff, #f0f0f0);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    position: relative;
    z-index: 1;
}

.header p { 
    margin: 0.5rem 0; 
    opacity: 0.95; 
    font-size: 1.2rem;
    font-weight: 500;
    position: relative;
    z-index: 1;
}

.progress-section { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    padding: 2rem; 
    color: white;
}

.progress-bar-container {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 25px;
    padding: 0.5rem;
    margin-bottom: 2rem;
}

.progress-bar {
    height: 20px;
    background: linear-gradient(135deg, #56ab2f, #a8e6cf);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    transition: width 0.8s ease;
}

.progress-stats { 
    display: grid; 
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
    gap: 1.5rem; 
}

.stat-card { 
    background: rgba(255, 255, 255, 0.15); 
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1.5rem; 
    border-radius: 20px; 
    text-align: center; 
    transition: all 0.3s ease;
    cursor: pointer;
}

.stat-card:hover { 
    transform: translateY(-5px) scale(1.02); 
    background: rgba(255, 255, 255, 0.25);
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.stat-card h4 { 
    margin: 0 0 0.8rem 0; 
    color: rgba(255,255,255,0.9); 
    font-size: 0.95rem; 
    font-weight: 600; 
}

.stat-card div { 
    font-size: 2.2rem; 
    font-weight: 800; 
    color: white; 
    text-shadow: 0 2px 4px rgba(0,0,0,0.2); 
}

.controls-section { 
    padding: 2rem; 
    background: linear-gradient(135deg, #00f5ff 0%, #fc466b 100%); 
    text-align: center; 
}

.controls-grid {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 1.5rem;
}

.btn { 
    display: inline-block; 
    padding: 0.8rem 1.8rem; 
    border: none; 
    border-radius: 50px; 
    text-decoration: none; 
    font-weight: 700; 
    cursor: pointer; 
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    text-transform: uppercase;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    font-size: 0.9rem;
}

.btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    transition: left 0.5s;
}

.btn:hover::before {
    left: 100%;
}

.btn:hover { 
    transform: translateY(-3px) scale(1.05); 
    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
}

.batch-btn { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
.export-btn { background: linear-gradient(135deg, #00c6ff, #0072ff); color: white; }
.claude-btn { background: linear-gradient(135deg, #ff6b6b, #4ecdc4); color: white; }
.qc-btn { background: linear-gradient(135deg, #ffd700, #ffb347); color: #333; }

.questions-grid { 
    padding: 2rem; 
    background: linear-gradient(145deg, #f0f2f5 0%, #e8ebf0 100%);
}

.qc-filter-section {
    background: linear-gradient(135deg, #ffd700, #ffb347);
    padding: 1.5rem 2rem;
    display: flex;
    gap: 1rem;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
}

.filter-btn {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 25px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.filter-btn.active {
    background: #fff;
    color: #333;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.filter-btn:not(.active) {
    background: rgba(255,255,255,0.3);
    color: #333;
}

.question-card { 
    background: rgba(255, 255, 255, 0.9); 
    border: none; 
    border-radius: 24px; 
    margin: 2rem 0; 
    overflow: hidden; 
    backdrop-filter: blur(20px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.08), 0 5px 15px rgba(0,0,0,0.05);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.question-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 25px 50px rgba(0,0,0,0.12), 0 10px 25px rgba(0,0,0,0.08);
}

.question-header { 
    background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%); 
    padding: 1.5rem 2rem; 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    color: white;
    position: relative;
    overflow: hidden;
}

.question-header h3 { 
    margin: 0; 
    color: white; 
    font-size: 1.5rem;
    font-weight: 800;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    position: relative;
    z-index: 1;
}

.status-indicator { 
    padding: 0.6rem 1.2rem; 
    border-radius: 25px; 
    font-size: 0.85rem; 
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    position: relative;
    z-index: 1;
}

.status-indicator.solved { 
    background: linear-gradient(135deg, #56ab2f, #a8e6cf); 
    color: white; 
    box-shadow: 0 6px 20px rgba(86, 171, 47, 0.3);
}

.status-indicator.flagged { 
    background: linear-gradient(135deg, #f093fb, #f5576c); 
    color: white; 
    box-shadow: 0 6px 20px rgba(240, 147, 251, 0.3);
}

.status-indicator.reviewed { 
    background: linear-gradient(135deg, #ffd700, #ffb347); 
    color: #333; 
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.3);
}

.status-indicator.pending { 
    background: linear-gradient(135deg, #667eea, #764ba2); 
    color: white; 
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.question-content { 
    display: grid; 
    grid-template-columns: 1fr 1fr; 
    gap: 2rem; 
    padding: 2rem; 
    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
}

.image-section {
    display: flex;
    flex-direction: column;
}

.question-image { 
    width: 100%; 
    max-height: 500px; 
    object-fit: contain; 
    border: none; 
    border-radius: 20px; 
    margin-bottom: 1rem; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.question-image:hover {
    transform: scale(1.02);
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}

.image-controls { 
    display: flex; 
    gap: 1rem; 
    flex-wrap: wrap; 
    justify-content: center;
}

.btn-small { 
    padding: 0.6rem 1.2rem; 
    font-size: 0.85rem; 
    border: none; 
    border-radius: 25px; 
    cursor: pointer; 
    background: linear-gradient(135deg, #667eea, #764ba2); 
    color: white; 
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-small:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.claude-link { 
    background: linear-gradient(135deg, #ff6b6b, #4ecdc4) !important; 
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
}

.claude-link:hover {
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4) !important;
}

.solution-section { 
    display: flex; 
    flex-direction: column; 
    gap: 1.5rem; 
}

.qc-section {
    background: rgba(255, 215, 0, 0.1);
    border: 2px solid #ffd700;
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.qc-controls {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    align-items: center;
    margin-top: 1rem;
}

.qc-notes {
    width: 100%;
    padding: 0.8rem;
    border: 2px solid #ffd700;
    border-radius: 10px;
    font-size: 0.9rem;
    margin-top: 0.5rem;
    resize: vertical;
    min-height: 60px;
}

.solution-textarea { 
    width: 100%; 
    height: 320px; 
    padding: 1.5rem; 
    border: 3px solid transparent; 
    border-radius: 20px; 
    font-family: 'Monaco', 'Menlo', monospace; 
    font-size: 0.9rem; 
    resize: vertical; 
    background: linear-gradient(white, white) padding-box, linear-gradient(135deg, #667eea, #764ba2) border-box;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}

.solution-textarea:focus { 
    outline: none; 
    background: linear-gradient(white, white) padding-box, linear-gradient(135deg, #ff6b6b, #4ecdc4) border-box;
    box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    transform: translateY(-2px);
}

.solution-controls { 
    display: flex; 
    gap: 1rem; 
    flex-wrap: wrap; 
    justify-content: center;
}

.save-btn { 
    background: linear-gradient(135deg, #56ab2f, #a8e6cf); 
    color: white; 
    box-shadow: 0 6px 20px rgba(86, 171, 47, 0.3);
}

.validate-btn { 
    background: linear-gradient(135deg, #00c6ff, #0072ff); 
    color: white; 
    box-shadow: 0 6px 20px rgba(0, 198, 255, 0.3);
}

.clear-btn { 
    background: linear-gradient(135deg, #ff6b6b, #ffa07a); 
    color: white; 
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
}

.review-btn { 
    background: linear-gradient(135deg, #ffd700, #ffb347); 
    color: #333; 
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.3);
}

.unflag-btn { 
    background: linear-gradient(135deg, #56ab2f, #a8e6cf); 
    color: white; 
    box-shadow: 0 6px 20px rgba(86, 171, 47, 0.3);
}

.prompt-display { 
    background: rgba(255, 255, 255, 0.95); 
    border: 2px solid #667eea; 
    border-radius: 15px; 
    padding: 1.5rem; 
    margin-top: 1rem; 
    font-family: monospace; 
    font-size: 0.85rem; 
    line-height: 1.6; 
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    white-space: pre-wrap;
}

.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    font-weight: 600;
    z-index: 1000;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

.notification.success { background: rgba(86, 171, 47, 0.9); color: white; }
.notification.error { background: rgba(255, 107, 107, 0.9); color: white; }
.notification.warning { background: rgba(255, 193, 7, 0.9); color: #333; }
.notification.info { background: rgba(23, 162, 184, 0.9); color: white; }

.hidden { display: none !important; }

@media (max-width: 768px) {
    .question-content { 
        grid-template-columns: 1fr; 
    }
    .header h1 {
        font-size: 2rem;
    }
    .progress-stats {
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    .controls-grid {
        flex-direction: column;
        align-items: center;
    }
}
"""

def get_javascript_template(paper_folder, total_questions, subject):
    """Fixed JavaScript with proper button event handling"""
    return f"""
<script>
// Global variables
const paperFolder = '{paper_folder}';
const subject = '{subject}';
const totalQuestions = {total_questions};
let currentFilter = 'all';

// Utility functions
function getPromptTemplate(questionNum) {{
    return `Please analyze this ${{subject.toLowerCase()}} question image carefully and provide a complete solution in JSON format. Double check your reading of all values before proceeding as accuracy for exam is more important than speed. Before applying any physics principles, carefully examine the exact geometry and positioning shown in the diagram, ensuring distances are measured from correct reference points and segments are interpreted as additive or separate measurements as appropriate.

Required JSON structure:
{{
  "question_text": "Extract the complete question text exactly as shown",
  "options": {{
    "A": "Complete text for option A",
    "B": "Complete text for option B", 
    "C": "Complete text for option C",
    "D": "Complete text for option D"
  }},
  "correct_answer": "A/B/C/D (single letter only)",
  "simple_answer": "Brief but clear explanation of the correct answer",
  "detailed_explanation": {{
    "approach": "Method or principle used",
    "calculation": "Key calculations if applicable", 
    "reasoning": "Logical thought process",
    "conclusion": "Why this answer is correct"
  }},
  "calculation_steps": [
    "Step 1: Description of first step",
    "Step 2: Description of second step",
    "Continue as needed..."
  ],
  "topic": "Specific ${{subject.toLowerCase()}} topic",
  "difficulty": "easy/medium/hard",
  "confidence_score": 0.95
}}

Please be thorough and accurate in your analysis.`;
}}

function showNotification(message, type = 'info') {{
    // Remove existing notifications
    const existing = document.querySelectorAll('.notification');
    existing.forEach(n => n.remove());
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification ${{type}}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {{
        if (notification.parentElement) {{
            notification.remove();
        }}
    }}, 4000);
}}

// Global function declarations (hoisted)
window.copyPrompt = function(questionNum) {{
    console.log(`Copy prompt called for question ${{questionNum}}`);
    try {{
        const prompt = getPromptTemplate(questionNum);
        
        // Use modern clipboard API if available
        if (navigator.clipboard && window.isSecureContext) {{
            navigator.clipboard.writeText(prompt).then(() => {{
                showNotification(`Prompt for Question ${{questionNum}} copied!`, 'success');
            }}).catch(err => {{
                console.error('Clipboard API failed:', err);
                fallbackCopy(prompt);
            }});
        }} else {{
            fallbackCopy(prompt);
        }}
    }} catch (e) {{
        console.error('Copy prompt error:', e);
        showNotification('Error copying prompt', 'error');
    }}
}};

window.togglePrompt = function(questionNum) {{
    console.log(`Toggle prompt called for question ${{questionNum}}`);
    try {{
        const display = document.getElementById(`prompt-display-${{questionNum}}`);
        const textDiv = document.getElementById(`prompt-text-${{questionNum}}`);
        
        if (!display) {{
            console.error('Prompt display element not found');
            showNotification('Error: Prompt display not found', 'error');
            return;
        }}
        
        const isHidden = display.style.display === 'none' || display.style.display === '';
        
        if (isHidden) {{
            display.style.display = 'block';
            if (textDiv) {{
                textDiv.textContent = getPromptTemplate(questionNum);
            }} else {{
                display.innerHTML = `<pre>${{getPromptTemplate(questionNum)}}</pre>`;
            }}
            showNotification(`Showing prompt for Question ${{questionNum}}`, 'info');
        }} else {{
            display.style.display = 'none';
            showNotification(`Hidden prompt for Question ${{questionNum}}`, 'info');
        }}
    }} catch (e) {{
        console.error('Toggle prompt error:', e);
        showNotification('Error toggling prompt', 'error');
    }}
}};

window.saveSolution = async function(questionNum) {{
    console.log(`Save solution called for question ${{questionNum}}`);
    try {{
        const textarea = document.getElementById(`solution-${{questionNum}}`);
        if (!textarea) {{
            showNotification('Solution textarea not found', 'error');
            return;
        }}
        
        const jsonText = textarea.value.trim();
        if (!jsonText) {{
            showNotification('Please enter solution first', 'warning');
            return;
        }}
        
        // Validate JSON
        let parsed;
        try {{
            parsed = JSON.parse(jsonText);
        }} catch (e) {{
            showNotification('Invalid JSON format', 'error');
            return;
        }}
        
        showNotification('Saving solution...', 'info');
        
        const response = await fetch('/api/save-solution', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                paper_folder: paperFolder,
                question_number: questionNum,
                solution: parsed
            }})
        }});
        
        const result = await response.json();
        
        if (result.success) {{
            const quality = result.quality_status || {{}};
            let message = `Question ${{questionNum}} saved successfully!`;
            
            if (quality.auto_flagged) {{
                message += ` (Flagged: ${{quality.flag_reason}})`;
                updateQuestionStatus(questionNum, 'flagged');
                showNotification(message, 'warning');
            }} else {{
                updateQuestionStatus(questionNum, 'solved');
                showNotification(message, 'success');
            }}
            
            refreshProgress();
        }} else {{
            showNotification(`Save failed: ${{result.error}}`, 'error');
        }}
    }} catch (e) {{
        console.error('Save solution error:', e);
        showNotification(`Error: ${{e.message}}`, 'error');
    }}
}};

window.validateJSON = function(questionNum) {{
    console.log(`Validate JSON called for question ${{questionNum}}`);
    try {{
        const textarea = document.getElementById(`solution-${{questionNum}}`);
        if (!textarea) {{
            showNotification('Solution textarea not found', 'error');
            return false;
        }}
        
        const jsonText = textarea.value.trim();
        if (!jsonText) {{
            showNotification('Please enter JSON response first', 'warning');
            return false;
        }}
        
        const parsed = JSON.parse(jsonText);
        const required = ['question_text', 'options', 'correct_answer', 'simple_answer'];
        const missing = required.filter(field => !parsed[field]);
        
        if (missing.length > 0) {{
            showNotification(`Missing fields: ${{missing.join(', ')}}`, 'error');
            return false;
        }}
        
        const options = parsed.options || {{}};
        if (Object.keys(options).length < 4) {{
            showNotification(`Incomplete options: only ${{Object.keys(options).length}} found`, 'warning');
            return false;
        }}
        
        if (!['A', 'B', 'C', 'D'].includes(parsed.correct_answer)) {{
            showNotification('Correct answer must be A, B, C, or D', 'error');
            return false;
        }}
        
        showNotification('JSON is valid!', 'success');
        return true;
    }} catch (e) {{
        console.error('JSON validation error:', e);
        showNotification(`Invalid JSON: ${{e.message}}`, 'error');
        return false;
    }}
}};

window.clearSolution = function(questionNum) {{
    console.log(`Clear solution called for question ${{questionNum}}`);
    try {{
        if (confirm('Clear this solution?')) {{
            const textarea = document.getElementById(`solution-${{questionNum}}`);
            if (textarea) {{
                textarea.value = '';
                showNotification('Solution cleared', 'info');
            }}
        }}
    }} catch (e) {{
        console.error('Clear solution error:', e);
        showNotification('Error clearing solution', 'error');
    }}
}};

window.reviewQuestion = async function(questionNum) {{
    console.log(`Review question called for question ${{questionNum}}`);
    try {{
        const notesTextarea = document.getElementById(`qc-notes-${{questionNum}}`);
        const reviewNotes = notesTextarea ? notesTextarea.value.trim() : '';
        
        showNotification('Marking as reviewed...', 'info');
        
        const response = await fetch('/api/review-question', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                paper_folder: paperFolder,
                question_number: questionNum,
                review_notes: reviewNotes
            }})
        }});
        
        const result = await response.json();
        
        if (result.success) {{
            updateQuestionStatus(questionNum, 'reviewed');
            showNotification(`Question ${{questionNum}} marked as reviewed!`, 'success');
            refreshProgress();
        }} else {{
            showNotification(`Review failed: ${{result.error}}`, 'error');
        }}
    }} catch (e) {{
        console.error('Review question error:', e);
        showNotification(`Error: ${{e.message}}`, 'error');
    }}
}};

window.unflagQuestion = async function(questionNum) {{
    console.log(`Unflag question called for question ${{questionNum}}`);
    try {{
        if (!confirm('Are you sure you want to unflag this question? This will override automatic quality checks.')) {{
            return;
        }}
        
        const notesTextarea = document.getElementById(`qc-notes-${{questionNum}}`);
        const reviewNotes = notesTextarea ? notesTextarea.value.trim() : '';
        
        showNotification('Unflagging question...', 'info');
        
        const response = await fetch('/api/unflag-question', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                paper_folder: paperFolder,
                question_number: questionNum,
                review_notes: reviewNotes
            }})
        }});
        
        const result = await response.json();
        
        if (result.success) {{
            updateQuestionStatus(questionNum, 'solved');
            showNotification(`Question ${{questionNum}} unflagged successfully!`, 'success');
            refreshProgress();
        }} else {{
            showNotification(`Unflag failed: ${{result.error}}`, 'error');
        }}
    }} catch (e) {{
        console.error('Unflag question error:', e);
        showNotification(`Error: ${{e.message}}`, 'error');
    }}
}};

window.openImage = function(imageUrl) {{
    try {{
        window.open(imageUrl, '_blank');
    }} catch (e) {{
        console.error('Error opening image:', e);
        showNotification('Error opening image', 'error');
    }}
}};

// Helper functions
function fallbackCopy(text) {{
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {{
        const successful = document.execCommand('copy');
        if (successful) {{
            showNotification('Prompt copied to clipboard!', 'success');
        }} else {{
            showNotification('Failed to copy prompt', 'error');
        }}
    }} catch (err) {{
        showNotification('Failed to copy prompt', 'error');
    }}
    
    document.body.removeChild(textArea);
}}

function updateQuestionStatus(questionNum, status) {{
    try {{
        const statusEl = document.getElementById(`status-${{questionNum}}`);
        if (!statusEl) {{
            console.error('Status element not found for question', questionNum);
            return;
        }}
        
        statusEl.className = `status-indicator ${{status}}`;
        
        switch(status) {{
            case 'solved':
                statusEl.textContent = 'Solved';
                break;
            case 'flagged':
                statusEl.textContent = 'Flagged';
                break;
            case 'reviewed':
                statusEl.textContent = 'Reviewed';
                break;
            default:
                statusEl.textContent = 'Pending';
        }}
    }} catch (e) {{
        console.error('Update question status error:', e);
    }}
}}

// Filter and control functions
window.filterQuestions = function(filter) {{
    try {{
        currentFilter = filter;
        const cards = document.querySelectorAll('.question-card');
        
        // Update filter button states
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.classList.remove('active');
            if (btn.textContent.toLowerCase().includes(filter.toLowerCase()) || 
                (filter === 'all' && btn.textContent.toLowerCase().includes('all'))) {{
                btn.classList.add('active');
            }}
        }});
        
        let visibleCount = 0;
        
        cards.forEach(card => {{
            const questionNum = card.id.replace('question-', '');
            const statusEl = document.getElementById(`status-${{questionNum}}`);
            
            let status = 'pending';
            if (statusEl) {{
                const statusClasses = statusEl.className;
                if (statusClasses.includes('flagged')) status = 'flagged';
                else if (statusClasses.includes('reviewed')) status = 'reviewed';
                else if (statusClasses.includes('solved')) status = 'solved';
            }}
            
            let shouldShow = false;
            switch(filter) {{
                case 'all': shouldShow = true; break;
                case 'flagged': shouldShow = (status === 'flagged'); break;
                case 'reviewed': shouldShow = (status === 'reviewed'); break;
                case 'solved': shouldShow = (status === 'solved'); break;
                case 'pending': shouldShow = (status === 'pending'); break;
            }}
            
            if (shouldShow) {{
                card.classList.remove('hidden');
                visibleCount++;
            }} else {{
                card.classList.add('hidden');
            }}
        }});
        
        showNotification(`Showing ${{visibleCount}} ${{filter}} questions`, 'info');
    }} catch (e) {{
        console.error('Filter questions error:', e);
        showNotification('Error filtering questions', 'error');
    }}
}};

window.refreshProgress = async function() {{
    try {{
        const response = await fetch('/api/get-progress', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ paper_folder: paperFolder }})
        }});
        
        const result = await response.json();
        
        if (result.success) {{
            const progress = result.progress;
            
            // Update progress elements safely
            const updateElement = (id, value) => {{
                const element = document.getElementById(id);
                if (element) element.textContent = value;
            }};
            
            updateElement('totalQuestions', progress.total_questions);
            updateElement('solvedCount', progress.solved_count);
            updateElement('approvedCount', progress.high_confidence_count || 0);
            updateElement('flaggedCount', progress.flagged_count || 0);
            updateElement('reviewedCount', progress.reviewed_count || 0);
            updateElement('avgConfidence', Math.round((progress.average_confidence || 0) * 100) + '%');
            
            const progressBar = document.getElementById('progressBar');
            if (progressBar) {{
                const percentage = Math.round(progress.completion_percentage || 0);
                progressBar.style.width = percentage + '%';
                progressBar.textContent = percentage + '% Complete';
            }}
        }}
    }} catch (e) {{
        console.error('Refresh progress error:', e);
        showNotification('Error refreshing progress', 'error');
    }}
}};

window.exportSolutions = async function() {{
    try {{
        showNotification('Creating export...', 'info');
        
        const response = await fetch('/api/export-solutions', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ paper_folder: paperFolder }})
        }});
        
        const result = await response.json();
        
        if (result.success) {{
            showNotification('Export completed!', 'success');
            setTimeout(() => {{
                const stats = result.statistics || {{}};
                alert(`Export created successfully!\\nFile: ${{result.export_filename}}\\nSolved: ${{stats.solved_questions}}/${{stats.total_questions}}`);
            }}, 500);
        }} else {{
            showNotification(`Export failed: ${{result.error}}`, 'error');
        }}
    }} catch (e) {{
        console.error('Export solutions error:', e);
        showNotification(`Error: ${{e.message}}`, 'error');
    }}
}};

window.getBatchPrompts = function() {{
    try {{
        let allPrompts = `BATCH PROMPTS FOR ${{paperFolder.toUpperCase()}}\\n`;
        allPrompts += `============================================================\\n\\n`;
        
        for (let i = 1; i <= totalQuestions; i++) {{
            allPrompts += `QUESTION ${{i}}:\\n`;
            allPrompts += getPromptTemplate(i);
            allPrompts += `\\n\\n========================================\\n\\n`;
        }}
        
        if (navigator.clipboard && window.isSecureContext) {{
            navigator.clipboard.writeText(allPrompts).then(() => {{
                showNotification(`All ${{totalQuestions}} prompts copied!`, 'success');
                setTimeout(() => {{
                    alert(`Batch Prompts Copied!\\n\\n${{totalQuestions}} prompts copied to clipboard.`);
                }}, 500);
            }}).catch(() => {{
                fallbackCopy(allPrompts);
            }});
        }} else {{
            fallbackCopy(allPrompts);
        }}
    }} catch (e) {{
        console.error('Get batch prompts error:', e);
        showNotification('Error getting batch prompts', 'error');
    }}
}};

// Event listeners and initialization
document.addEventListener('DOMContentLoaded', function() {{
    console.log('DOM Content Loaded - initializing...');
    showNotification('AxcelScore Hybrid Solver loaded!', 'success');
    refreshProgress();
}});

// Fallback for older browsers
window.addEventListener('load', function() {{
    console.log('Window loaded - fallback initialization...');
    if (!document.querySelector('.notification')) {{
        showNotification('AxcelScore Hybrid Solver loaded!', 'success');
        refreshProgress();
    }}
}});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {{
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {{
        e.preventDefault();
        const focused = document.activeElement;
        if (focused && focused.id && focused.id.startsWith('solution-')) {{
            const questionNum = parseInt(focused.id.replace('solution-', ''));
            if (!isNaN(questionNum)) {{
                saveSolution(questionNum);
            }}
        }}
    }}
    
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {{
        e.preventDefault();
        refreshProgress();
    }}
}});

console.log('JavaScript loaded successfully');
</script>
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
    auto_flagged: bool = False
    needs_review: bool = False
    flag_reason: str = ""
    manually_reviewed: bool = False
    reviewer_notes: str = ""
    review_timestamp: str = ""

class ScalableAISolverManager:
    """Complete Scalable AI Solver Manager with QC workflow"""
    
    def __init__(self, question_banks_dir=None):
        self.question_banks_dir = Path(question_banks_dir) if question_banks_dir else QUESTION_BANKS_DIR
        self.current_paper_path = None
        self.solver_data = {}
        
    def extract_subject_from_folder(self, folder_name):
        """Extract subject from folder name"""
        folder_lower = folder_name.lower()
        if 'physics' in folder_lower:
            return 'Physics'
        elif 'chemistry' in folder_lower:
            return 'Chemistry'
        elif 'biology' in folder_lower:
            return 'Biology'
        elif 'math' in folder_lower:
            return 'Mathematics'
        return 'Physics'  # default

    def extract_year_from_folder(self, folder_name):
        """Extract year from folder name"""
        import re
        match = re.search(r'(\d{4})', folder_name)
        return match.group(1) if match else '2025'

    def extract_month_from_folder(self, folder_name):
        """Extract month from folder name"""
        folder_lower = folder_name.lower()
        if 'may' in folder_lower:
            return 'May'
        elif 'oct' in folder_lower:
            return 'October'
        elif 'mar' in folder_lower:
            return 'March'
        return 'May'  # default

    def extract_paper_code_from_folder(self, folder_name):
        """Extract paper code from folder name"""
        parts = folder_name.split('_')
        return parts[-1] if parts else '13'
        
    def initialize_solver(self, paper_folder):
        """Initialize AI solver - Creates solutions.json from images"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            
            if not paper_folder_path.exists():
                return {"success": False, "error": f"Paper folder not found: {paper_folder}"}
            
            # Enhanced folder priority system
            images_folder = paper_folder_path / "images"
            extracted_images_folder = paper_folder_path / "extracted_images"
            
            active_images_folder = None
            if images_folder.exists():
                active_images_folder = images_folder
                print(f"Using primary images folder: {images_folder}")
            elif extracted_images_folder.exists():
                active_images_folder = extracted_images_folder
                print(f"Using fallback extracted_images folder: {extracted_images_folder}")
            else:
                return {"success": False, "error": "No images folder found"}
            
            # Get image files
            image_files = list(active_images_folder.glob("question_*_enhanced.png"))
            if not image_files:
                # Try other patterns
                image_files = list(active_images_folder.glob("*.png")) + list(active_images_folder.glob("*.jpg"))
            
            if not image_files:
                return {"success": False, "error": "No question images found"}
            
            image_files.sort()
            
            # CREATE solutions.json if it doesn't exist
            solutions_file = paper_folder_path / "solutions.json"
            if not solutions_file.exists():
                # Create from scratch based on images
                master_data = {
                    "metadata": {
                        "paper_folder": paper_folder,
                        "subject": self.extract_subject_from_folder(paper_folder),
                        "year": self.extract_year_from_folder(paper_folder),
                        "month": self.extract_month_from_folder(paper_folder),
                        "paper_code": self.extract_paper_code_from_folder(paper_folder),
                        "created_at": datetime.now().isoformat(),
                        "workflow": "hybrid_manual_gen_alpha",
                        "total_questions": len(image_files)
                    },
                    "questions": []
                }
                
                # Create question entries from images
                for i, img_file in enumerate(image_files, 1):
                    master_data["questions"].append({
                        "question_number": i,
                        "image_filename": img_file.name,
                        "question_text": "",
                        "options": {},
                        "correct_answer": "",
                        "explanation": "",
                        "detailed_explanation": {},
                        "calculation_steps": [],
                        "topic": "",
                        "difficulty": "medium",
                        "confidence_score": 0.0,
                        "solved_by_ai": False,
                        "auto_flagged": False,
                        "needs_review": False,
                        "flag_reason": "",
                        "manually_reviewed": False,
                        "reviewer_notes": "",
                        "review_timestamp": "",
                        "created_at": datetime.now().isoformat()
                    })
                
                # Save the initial structure
                with open(solutions_file, 'w') as f:
                    json.dump(master_data, f, indent=2)
                
                print(f"Created solutions.json with {len(image_files)} questions")
            else:
                # Load existing file and add missing QC fields if needed
                with open(solutions_file, 'r') as f:
                    master_data = json.load(f)
                
                # Upgrade existing questions with QC fields if missing
                updated = False
                for question in master_data.get('questions', []):
                    if 'manually_reviewed' not in question:
                        question.update({
                            'manually_reviewed': False,
                            'reviewer_notes': "",
                            'review_timestamp': ""
                        })
                        updated = True
                
                if updated:
                    with open(solutions_file, 'w') as f:
                        json.dump(master_data, f, indent=2)
                    print(f"Updated solutions.json with QC fields")
            
            questions = master_data.get('questions', [])
            total_questions = len(questions)
            solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
            flagged_count = sum(1 for q in questions if q.get('auto_flagged', False))
            reviewed_count = sum(1 for q in questions if q.get('manually_reviewed', False))
            high_confidence_count = sum(1 for q in questions if q.get('confidence_score', 0) >= CONFIDENCE_THRESHOLD)
            
            self.current_paper_path = paper_folder_path
            
            # Enhanced solver data structure
            metadata = master_data.get('metadata', {})
            self.solver_data = {
                "paper_path": str(paper_folder_path),
                "paper_folder": paper_folder,
                "metadata": metadata,
                "questions": questions,
                "images_folder": str(active_images_folder),
                "total_questions": total_questions,
                "solved_count": solved_count,
                "flagged_count": flagged_count,
                "reviewed_count": reviewed_count,
                "high_confidence_count": high_confidence_count,
                "initialized_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "message": f"Hybrid AI Solver initialized! Found {solved_count}/{total_questions} questions solved.",
                "data": {
                    "total_questions": total_questions,
                    "solved_count": solved_count,
                    "flagged_count": flagged_count,
                    "reviewed_count": reviewed_count,
                    "high_confidence_count": high_confidence_count,
                    "completion_rate": round((solved_count / total_questions) * 100, 1),
                    "quality_rate": round((high_confidence_count / max(solved_count, 1)) * 100, 1) if solved_count > 0 else 0,
                    "subject": metadata.get('subject', 'Unknown'),
                    "year": metadata.get('year', '2025'),
                    "month": metadata.get('month', 'Unknown'),
                    "paper_code": metadata.get('paper_code', '1'),
                    "images_folder": str(active_images_folder),
                    "paper_folder": paper_folder
                }
            }
            
        except Exception as e:
            print(f"AI Solver initialization error: {str(e)}")
            traceback.print_exc()
            return {"success": False, "error": f"Initialization failed: {str(e)}"}
    
    def save_solution(self, paper_folder, question_number, solution_json):
        """Save solution with enhanced quality control"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            master_solutions_file = paper_folder_path / "solutions.json"
            
            if not master_solutions_file.exists():
                return {"success": False, "error": "Master solutions.json file not found"}
            
            with open(master_solutions_file, 'r') as f:
                master_data = json.load(f)
            
            # Parse and validate solution
            if isinstance(solution_json, str):
                solution = json.loads(solution_json)
            else:
                solution = solution_json
            
            # Enhanced metadata
            solution['question_number'] = question_number
            solution['saved_at'] = datetime.now().isoformat()
            solution['solver_version'] = "Hybrid Gen Alpha v2.0"
            solution['solved_by_ai'] = True
            
            # Enhanced quality control
            confidence = solution.get('confidence_score', 0)
            
            # Comprehensive validation
            required_fields = [
                'question_text', 'options', 'correct_answer', 
                'simple_answer', 'detailed_explanation', 
                'topic', 'confidence_score'
            ]
            
            missing_fields = [field for field in required_fields if not solution.get(field)]
            
            # Enhanced auto-flagging with 91% threshold
            flag_reasons = []
            if confidence < CONFIDENCE_THRESHOLD:
                flag_reasons.append(f"Low confidence: {confidence:.1%} (< 91%)")
            if missing_fields:
                flag_reasons.append(f"Missing fields: {', '.join(missing_fields)}")
            
            # Options validation
            options = solution.get("options", {})
            if len(options) < 4:
                flag_reasons.append(f"Incomplete options: only {len(options)} found")
            
            # Set flagging status
            solution['auto_flagged'] = len(flag_reasons) > 0
            solution['needs_review'] = len(flag_reasons) > 0
            solution['flag_reason'] = '; '.join(flag_reasons) if flag_reasons else None
            solution['quality_threshold'] = '91%'
            
            # Update question in master data
            question_found = False
            if 'questions' in master_data:
                for i, question in enumerate(master_data['questions']):
                    if question.get('question_number') == question_number:
                        master_data['questions'][i].update({
                            'question_text': solution.get('question_text'),
                            'options': solution.get('options'),
                            'correct_answer': solution.get('correct_answer'),
                            'explanation': solution.get('simple_answer'),
                            'detailed_explanation': solution.get('detailed_explanation'),
                            'calculation_steps': solution.get('calculation_steps'),
                            'topic': solution.get('topic'),
                            'difficulty': solution.get('difficulty'),
                            'confidence_score': confidence,
                            'solved_by_ai': True,
                            'saved_at': solution['saved_at'],
                            'auto_flagged': solution['auto_flagged'],
                            'needs_review': solution['needs_review'],
                            'flag_reason': solution['flag_reason']
                        })
                        question_found = True
                        break
            
            if not question_found:
                return {"success": False, "error": f"Question {question_number} not found in master file"}
            
            # Update comprehensive metadata
            master_data['metadata'].update({
                'last_updated': datetime.now().isoformat(),
                'ai_solver_version': 'Hybrid Gen Alpha v2.0',
                'solving_in_progress': True
            })
            
            # Calculate enhanced statistics
            solved_questions = sum(1 for q in master_data['questions'] if q.get('solved_by_ai'))
            total_questions = len(master_data['questions'])
            flagged_questions = sum(1 for q in master_data['questions'] if q.get('auto_flagged'))
            reviewed_questions = sum(1 for q in master_data['questions'] if q.get('manually_reviewed'))
            high_confidence = sum(1 for q in master_data['questions'] if q.get('confidence_score', 0) >= CONFIDENCE_THRESHOLD)
            avg_confidence = sum(q.get('confidence_score', 0) for q in master_data['questions'] if q.get('solved_by_ai')) / max(solved_questions, 1)
            
            master_data['metadata'].update({
                'progress_stats': {
                    'total_questions': total_questions,
                    'solved_questions': solved_questions,
                    'completion_rate': round((solved_questions / total_questions) * 100, 1),
                    'flagged_questions': flagged_questions,
                    'reviewed_questions': reviewed_questions,
                    'high_confidence_questions': high_confidence,
                    'average_confidence': round(avg_confidence, 3)
                }
            })
            
            # Save back to master file
            with open(master_solutions_file, 'w') as f:
                json.dump(master_data, f, indent=2)
            
            print(f"Updated master solutions.json: Question {question_number} saved")
            print(f"Progress: {solved_questions}/{total_questions} ({master_data['metadata']['progress_stats']['completion_rate']}%)")
            
            return {
                "success": True,
                "message": f"Solution for Question {question_number} saved successfully",
                "progress": master_data['metadata']['progress_stats'],
                "quality_status": {
                    "confidence": confidence,
                    "auto_flagged": solution['auto_flagged'],
                    "needs_review": solution['needs_review'],
                    "flag_reason": solution['flag_reason']
                }
            }
            
        except Exception as e:
            print(f"Error in save_solution: {str(e)}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def review_question(self, paper_folder, question_number, review_notes=""):
        """Mark question as manually reviewed"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            master_solutions_file = paper_folder_path / "solutions.json"
            
            if not master_solutions_file.exists():
                return {"success": False, "error": "Master solutions file not found"}
            
            with open(master_solutions_file, 'r') as f:
                master_data = json.load(f)
            
            # Find and update the question
            question_found = False
            if 'questions' in master_data:
                for i, question in enumerate(master_data['questions']):
                    if question.get('question_number') == question_number:
                        master_data['questions'][i].update({
                            'manually_reviewed': True,
                            'reviewer_notes': review_notes,
                            'review_timestamp': datetime.now().isoformat()
                        })
                        question_found = True
                        break
            
            if not question_found:
                return {"success": False, "error": f"Question {question_number} not found"}
            
            # Update metadata
            master_data['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save back to file
            with open(master_solutions_file, 'w') as f:
                json.dump(master_data, f, indent=2)
            
            return {
                "success": True,
                "message": f"Question {question_number} marked as reviewed"
            }
            
        except Exception as e:
            print(f"Error in review_question: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def unflag_question(self, paper_folder, question_number, review_notes=""):
        """Unflag a question (manual override)"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            master_solutions_file = paper_folder_path / "solutions.json"
            
            if not master_solutions_file.exists():
                return {"success": False, "error": "Master solutions file not found"}
            
            with open(master_solutions_file, 'r') as f:
                master_data = json.load(f)
            
            # Find and update the question
            question_found = False
            if 'questions' in master_data:
                for i, question in enumerate(master_data['questions']):
                    if question.get('question_number') == question_number:
                        master_data['questions'][i].update({
                            'auto_flagged': False,
                            'needs_review': False,
                            'flag_reason': None,
                            'manually_reviewed': True,
                            'reviewer_notes': review_notes or "Manually unflagged",
                            'review_timestamp': datetime.now().isoformat()
                        })
                        question_found = True
                        break
            
            if not question_found:
                return {"success": False, "error": f"Question {question_number} not found"}
            
            # Update metadata
            master_data['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save back to file
            with open(master_solutions_file, 'w') as f:
                json.dump(master_data, f, indent=2)
            
            return {
                "success": True,
                "message": f"Question {question_number} unflagged successfully"
            }
            
        except Exception as e:
            print(f"Error in unflag_question: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_progress(self, paper_folder):
        """Get comprehensive progress with all metrics including QC"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            master_solutions_file = paper_folder_path / "solutions.json"
            
            if not master_solutions_file.exists():
                return {"success": False, "error": "Master solutions file not found"}
            
            with open(master_solutions_file, 'r') as f:
                master_data = json.load(f)
            
            questions = master_data.get('questions', [])
            total_questions = len(questions)
            
            # Comprehensive metrics including QC
            solved_count = sum(1 for q in questions if q.get('solved_by_ai'))
            flagged_count = sum(1 for q in questions if q.get('auto_flagged'))
            reviewed_count = sum(1 for q in questions if q.get('manually_reviewed'))
            high_confidence_count = sum(1 for q in questions if q.get('confidence_score', 0) >= CONFIDENCE_THRESHOLD)
            
            # Average confidence calculation
            solved_questions = [q for q in questions if q.get('solved_by_ai')]
            avg_confidence = sum(q.get('confidence_score', 0) for q in solved_questions) / max(len(solved_questions), 1)
            
            return {
                "success": True,
                "progress": {
                    "total_questions": total_questions,
                    "solved_count": solved_count,
                    "flagged_count": flagged_count,
                    "reviewed_count": reviewed_count,
                    "high_confidence_count": high_confidence_count,
                    "completion_percentage": (solved_count / total_questions * 100) if total_questions > 0 else 0,
                    "quality_percentage": (high_confidence_count / max(solved_count, 1) * 100) if solved_count > 0 else 0,
                    "average_confidence": avg_confidence
                }
            }
            
        except Exception as e:
            print(f"Error in get_progress: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def export_solutions(self, paper_folder):
        """Enhanced export with comprehensive backup"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            master_solutions_file = paper_folder_path / "solutions.json"
            
            if not master_solutions_file.exists():
                return {"success": False, "error": "No master solutions file found"}
            
            with open(master_solutions_file, 'r') as f:
                master_data = json.load(f)
            
            # Create comprehensive export
            export_data = dict(master_data)
            export_data['export_info'] = {
                "export_date": datetime.now().isoformat(),
                "format_version": "hybrid_gen_alpha_v2.0",
                "export_type": "complete_backup",
                "exported_from": "master_solutions_json"
            }
            
            # Save timestamped backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"{paper_folder}_hybrid_backup_{timestamp}.json"
            export_path = paper_folder_path / export_filename
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            # Calculate comprehensive statistics including QC
            questions = master_data.get('questions', [])
            solved_count = sum(1 for q in questions if q.get('solved_by_ai'))
            total_count = len(questions)
            flagged_count = sum(1 for q in questions if q.get('auto_flagged'))
            reviewed_count = sum(1 for q in questions if q.get('manually_reviewed'))
            high_quality_count = sum(1 for q in questions if q.get('solved_by_ai', False) and not q.get('auto_flagged', False))
            
            return {
                "success": True,
                "export_path": str(export_path),
                "export_filename": export_filename,
                "backup_type": "complete_master_backup",
                "statistics": {
                    "total_questions": total_count,
                    "solved_questions": solved_count,
                    "flagged_questions": flagged_count,
                    "reviewed_questions": reviewed_count,
                    "completion_rate": round((solved_count / total_count) * 100, 1) if total_count > 0 else 0,
                    "quality_rate": round((high_quality_count / max(solved_count, 1)) * 100, 1) if solved_count > 0 else 0
                }
            }
            
        except Exception as e:
            print(f"Error in export_solutions: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_simplified_interface(self, paper_folder):
        """Generate complete Gen Alpha interface with QC workflow"""
        try:
            if not self.solver_data or self.solver_data.get('paper_folder') != paper_folder:
                init_result = self.initialize_solver(paper_folder)
                if not init_result["success"]:
                    return init_result
            
            metadata = self.solver_data["metadata"]
            questions = self.solver_data["questions"]
            subject = metadata.get('subject', 'Physics').title()
            year = metadata.get('year', '2025')
            month = metadata.get('month', 'Unknown').title()
            paper_code = metadata.get('paper_code', '1')
            
            title = f"{subject} {year} {month} Paper {paper_code}"
            total_questions = len(questions)
            solved_count = self.solver_data.get("solved_count", 0)
            flagged_count = self.solver_data.get("flagged_count", 0)
            reviewed_count = self.solver_data.get("reviewed_count", 0)
            high_confidence_count = self.solver_data.get("high_confidence_count", 0)
            
            # Generate comprehensive questions HTML with QC features
            questions_html = ""
            for question in questions:
                question_num = question.get("question_number")
                filename = question.get("image_filename")
                
                # Smart image URL generation
                if "images" in self.solver_data["images_folder"]:
                    image_url = f"/images/{paper_folder}/{filename}"
                else:
                    image_url = f"/images/{paper_folder}/extracted_images/{filename}"
                
                # Enhanced status determination with QC
                is_solved = question.get('solved_by_ai', False)
                is_flagged = question.get('auto_flagged', False)
                is_reviewed = question.get('manually_reviewed', False)
                confidence = question.get('confidence_score', 0)
                flag_reason = question.get('flag_reason', '')
                reviewer_notes = question.get('reviewer_notes', '')
                
                # Determine display status
                if is_reviewed and not is_flagged:
                    status_class = "reviewed"
                    status_text = "Reviewed"
                elif is_flagged:
                    status_class = "flagged"
                    status_text = f"Flagged ({int(confidence * 100)}%)"
                elif is_solved:
                    status_class = "solved"
                    status_text = f"Solved ({int(confidence * 100)}%)"
                else:
                    status_class = "pending"
                    status_text = "Pending"
                
                # Pre-fill existing solutions
                existing_solution = ""
                if is_solved:
                    try:
                        solution_data = {
                            "question_text": question.get("question_text", ""),
                            "options": question.get("options", {}),
                            "correct_answer": question.get("correct_answer", ""),
                            "simple_answer": question.get("explanation", ""),
                            "calculation_steps": question.get("calculation_steps", []),
                            "detailed_explanation": question.get("detailed_explanation", {}),
                            "topic": question.get("topic", ""),
                            "difficulty": question.get("difficulty", ""),
                            "confidence_score": confidence
                        }
                        existing_solution = json.dumps(solution_data, indent=2)
                    except:
                        existing_solution = ""
                
                # QC section for flagged or reviewed questions
                qc_section = ""
                if is_flagged or is_reviewed:
                    qc_section = f'''
                    <div class="qc-section">
                        <h4>Quality Control</h4>
                        {f'<p><strong>Flag Reason:</strong> {flag_reason}</p>' if flag_reason else ''}
                        {f'<p><strong>Review Notes:</strong> {reviewer_notes}</p>' if reviewer_notes else ''}
                        <textarea id="qc-notes-{question_num}" placeholder="Add review notes..." class="qc-notes">{reviewer_notes}</textarea>
                        <div class="qc-controls">
                            <button onclick="reviewQuestion({question_num})" class="btn-small review-btn">Mark Reviewed</button>
                            {f'<button onclick="unflagQuestion({question_num})" class="btn-small unflag-btn">Unflag</button>' if is_flagged else ''}
                        </div>
                    </div>'''
                
                questions_html += f'''
                <div class="question-card" id="question-{question_num}">
                    <div class="question-header">
                        <h3>Question {question_num}</h3>
                        <div class="status-indicator {status_class}" id="status-{question_num}">
                            {status_text}
                        </div>
                    </div>
                    <div class="question-content">
                        <div class="image-section">
                            <img src="{image_url}" alt="Question {question_num}" class="question-image" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                            <div style="display:none; padding: 2rem; text-align: center; color: #dc3545; border: 1px solid #dc3545; border-radius: 8px;">
                                Image not found<br>
                                <small>{filename}</small>
                            </div>
                            <div class="image-controls">
                                <button onclick="openImage('{image_url}')" class="btn-small">Full Size</button>
                                <button onclick="copyPrompt({question_num})" class="btn-small">Copy Prompt</button>
                                <a href="https://claude.ai" target="_blank" class="btn-small claude-link">Claude.ai</a>
                                <button onclick="togglePrompt({question_num})" class="btn-small">View Prompt</button>
                            </div>
                        </div>
                        <div class="solution-section">
                            {qc_section}
                            <div class="prompt-area">
                                <div id="prompt-display-{question_num}" class="prompt-display" style="display: none;">
                                    <div class="prompt-text" id="prompt-text-{question_num}"></div>
                                </div>
                            </div>
                            <div class="solution-input-area">
                                <textarea id="solution-{question_num}" placeholder="Paste Claude.ai JSON response here..." class="solution-textarea">{existing_solution}</textarea>
                                <div class="solution-controls">
                                    <button onclick="saveSolution({question_num})" class="btn-small save-btn">Save</button>
                                    <button onclick="validateJSON({question_num})" class="btn-small validate-btn">Validate</button>
                                    <button onclick="clearSolution({question_num})" class="btn-small clear-btn">Clear</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>'''
            
            # Complete HTML with Gen Alpha design and QC workflow
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>AxcelScore Hybrid Solver - {title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>{get_css_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AxcelScore Hybrid Solver</h1>
            <p>{title} - {total_questions} Questions</p>
            <p>Manual Workflow • Quality Control • 91% Threshold • Full Export</p>
        </div>
        
        <div class="progress-section">
            <div class="progress-bar-container">
                <div class="progress-bar" id="progressBar" style="width: {round((solved_count / total_questions) * 100, 1) if total_questions > 0 else 0}%">{round((solved_count / total_questions) * 100, 1) if total_questions > 0 else 0}% Complete</div>
            </div>
            <div class="progress-stats">
                <div class="stat-card">
                    <h4>Total</h4>
                    <div id="totalQuestions">{total_questions}</div>
                </div>
                <div class="stat-card">
                    <h4>Solved</h4>
                    <div id="solvedCount">{solved_count}</div>
                </div>
                <div class="stat-card">
                    <h4>High Quality (≥91%)</h4>
                    <div id="approvedCount">{high_confidence_count}</div>
                </div>
                <div class="stat-card">
                    <h4>Flagged</h4>
                    <div id="flaggedCount">{flagged_count}</div>
                </div>
                <div class="stat-card">
                    <h4>Reviewed</h4>
                    <div id="reviewedCount">{reviewed_count}</div>
                </div>
                <div class="stat-card">
                    <h4>Avg Confidence</h4>
                    <div id="avgConfidence">{int(sum(q.get('confidence_score', 0) for q in questions if q.get('solved_by_ai')) / max(solved_count, 1) * 100) if solved_count > 0 else 0}%</div>
                </div>
            </div>
        </div>
        
        <div class="controls-section">
            <h3>Control Center</h3>
            <div class="controls-grid">
                <button class="btn batch-btn" onclick="getBatchPrompts()">Get All Prompts</button>
                <button class="btn export-btn" onclick="exportSolutions()">Create Backup</button>
                <button class="btn" onclick="refreshProgress()">Refresh Progress</button>
                <a href="https://claude.ai" target="_blank" class="btn claude-btn">Open Claude.ai</a>
            </div>
        </div>
        
        <div class="qc-filter-section">
            <h3>Quality Control Filters</h3>
            <button class="filter-btn active" onclick="filterQuestions('all')">All Questions</button>
            <button class="filter-btn" onclick="filterQuestions('flagged')">Flagged Only</button>
            <button class="filter-btn" onclick="filterQuestions('reviewed')">Reviewed Only</button>
            <button class="filter-btn" onclick="filterQuestions('solved')">Solved Only</button>
            <button class="filter-btn" onclick="filterQuestions('pending')">Pending Only</button>
        </div>
        
        <div class="questions-grid">
            {questions_html}
        </div>
    </div>
    {get_javascript_template(paper_folder, total_questions, subject)}
</body>
</html>'''
            
            return {"success": True, "html_content": html_content}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize components
scalable_solver = ScalableAISolverManager()

# Flask Routes
@app.route('/solver/<paper_folder>')
def serve_scalable_solver(paper_folder):
    try:
        result = scalable_solver.generate_simplified_interface(paper_folder)
        if result["success"]:
            return result["html_content"]
        else:
            return f"Error: {result['error']}", 500
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/save-solution', methods=['POST'])
def save_solution():
    try:
        data = request.get_json()
        result = scalable_solver.save_solution(
            data.get('paper_folder'),
            data.get('question_number'), 
            data.get('solution')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/review-question', methods=['POST'])
def review_question():
    try:
        data = request.get_json()
        result = scalable_solver.review_question(
            data.get('paper_folder'),
            data.get('question_number'),
            data.get('review_notes', '')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/unflag-question', methods=['POST'])
def unflag_question():
    try:
        data = request.get_json()
        result = scalable_solver.unflag_question(
            data.get('paper_folder'),
            data.get('question_number'),
            data.get('review_notes', '')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/get-progress', methods=['POST'])
def get_progress():
    try:
        data = request.get_json()
        result = scalable_solver.get_progress(data.get('paper_folder'))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/export-solutions', methods=['POST'])
def export_solutions():
    try:
        data = request.get_json()
        result = scalable_solver.export_solutions(data.get('paper_folder'))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/images/<paper_folder>/<filename>')
def serve_paper_image(paper_folder, filename):
    try:
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        images_dir = paper_folder_path / "images"
        if images_dir.exists():
            return send_from_directory(str(images_dir), filename)
        
        extracted_images_dir = paper_folder_path / "extracted_images"
        if extracted_images_dir.exists():
            return send_from_directory(str(extracted_images_dir), filename)
        
        return f"Image not found: {filename}", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/images/<paper_folder>/extracted_images/<filename>')
def serve_extracted_image(paper_folder, filename):
    try:
        extracted_images_dir = QUESTION_BANKS_DIR / paper_folder / "extracted_images"
        if extracted_images_dir.exists():
            return send_from_directory(str(extracted_images_dir), filename)
        return f"Image not found: {filename}", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/')
def home():
    papers = []
    if QUESTION_BANKS_DIR.exists():
        for paper_folder in QUESTION_BANKS_DIR.iterdir():
            if paper_folder.is_dir():
                # Look for images folder first (primary detection method)
                images_folder = paper_folder / "images"
                extracted_images_folder = paper_folder / "extracted_images"
                
                has_images = images_folder.exists() or extracted_images_folder.exists()
                
                if has_images:
                    # Count total images
                    total_images = 0
                    if images_folder.exists():
                        total_images += len([f for f in images_folder.glob("*") if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']])
                    if extracted_images_folder.exists():
                        total_images += len([f for f in extracted_images_folder.glob("*") if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']])
                    
                    # Check if solutions.json exists
                    solutions_file = paper_folder / "solutions.json"
                    solved_count = 0
                    
                    if solutions_file.exists():
                        try:
                            with open(solutions_file, 'r') as f:
                                data = json.load(f)
                                questions = data.get('questions', [])
                                solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
                        except:
                            solved_count = 0
                    
                    papers.append({
                        "folder_name": paper_folder.name,
                        "total_questions": total_images,
                        "solved_count": solved_count,
                        "completion_rate": round((solved_count/total_images)*100, 1) if total_images > 0 else 0,
                        "has_images_folder": images_folder.exists(),
                        "has_extracted_folder": extracted_images_folder.exists()
                    })
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>AxcelScore Hybrid Solver</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            margin: 0; 
            padding: 2rem; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%); 
            background-size: 400% 400%;
            animation: gradientShift 8s ease infinite;
            min-height: 100vh; 
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .container { 
            max-width: 1200px; margin: 0 auto; 
            background: rgba(255, 255, 255, 0.95); 
            backdrop-filter: blur(20px);
            padding: 2rem; border-radius: 24px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .paper-card { 
            background: rgba(255, 255, 255, 0.9); 
            border: none; border-radius: 20px; 
            padding: 1.5rem; margin: 1rem 0; display: flex; 
            justify-content: space-between; align-items: center; 
            transition: all 0.3s ease; 
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .paper-card:hover { 
            transform: translateY(-5px) scale(1.02); 
            box-shadow: 0 20px 40px rgba(0,0,0,0.15); 
        }
        .btn { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; padding: 0.8rem 1.5rem; 
            border-radius: 25px; text-decoration: none; font-weight: 700; 
            transition: all 0.3s ease; text-transform: uppercase;
            letter-spacing: 0.5px; box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        }
        .btn:hover { 
            transform: translateY(-2px) scale(1.05); 
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .folder-info { font-size: 0.8rem; color: #666; margin-top: 0.5rem; }
        h1 { color: #2c3e50; margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 800; }
        .subtitle { color: #555; margin-bottom: 2rem; font-size: 1.2rem; }
        .warning-box {
            background: linear-gradient(135deg, #ff6b6b, #ffa07a);
            color: white; padding: 1.5rem; border-radius: 15px;
            margin: 1rem 0; text-align: center;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AxcelScore Hybrid Solver</h1>
        <p class="subtitle">Manual Workflow for AI-Assisted Question Solving</p>
        <div class="warning-box">
            <strong>Hybrid AI Solver Dashboard</strong><br>
            Advanced question solving with quality control and progress tracking
        </div>
        <p style="font-size: 0.9rem; color: #666;">Automatically detects papers by scanning for image folders</p>'''
    
    if papers:
        for paper in papers:
            folder_status = []
            if paper["has_images_folder"]:
                folder_status.append("images/")
            if paper["has_extracted_folder"]:
                folder_status.append("extracted_images/")
            
            html += f'''
            <div class="paper-card">
                <div>
                    <h3>{paper["folder_name"].replace('_', ' ').title()}</h3>
                    <p>{paper["solved_count"]}/{paper["total_questions"]} solved ({paper["completion_rate"]}%)</p>
                    <div class="folder-info">Found: {" + ".join(folder_status)}</div>
                </div>
                <a href="/solver/{paper["folder_name"]}" class="btn">Start Solving</a>
            </div>'''
    else:
        html += '''
        <div style="text-align: center; padding: 3rem; color: #666;">
            <h3>No Papers Found</h3>
            <p>No folders with images/ directories detected.</p>
            <p>Expected structure: question_banks/[paper_name]/images/</p>
        </div>'''
    
    html += '''
    </div>
</body>
</html>'''
    
    return html

if __name__ == '__main__':
    print("Starting AxcelScore Hybrid Solver - Standalone Version...")
    print("=" * 70)
    print(f"Question banks: {QUESTION_BANKS_DIR}")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD * 100}%")
    print(f"Port: 5006 (standalone)")
    print("Interface: http://localhost:5006")
    print("=" * 70)
    
    # Ensure directories exist
    QUESTION_BANKS_DIR.mkdir(exist_ok=True)
    
    app.run(
        host='0.0.0.0',
        port=5006,
        debug=True
    )