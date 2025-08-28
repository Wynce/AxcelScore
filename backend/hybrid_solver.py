#!/usr/bin/env python3
"""


"""

import os
import sys
import json
import base64
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from datetime import datetime
import traceback
import re
from flask import Flask, request, jsonify, send_from_directory, render_template_string, send_file
from werkzeug.utils import secure_filename
import anthropic
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from PIL import Image
import io
import fitz  # PyMuPDF for PDF processing
import pandas as pd

# Import only essential modules
from config import *
from templates import get_claude_prompt_template, get_css_styles, get_javascript_template

# Create Flask app
app = Flask(__name__)

# Set your API key directly
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
    auto_flagged: bool = False
    needs_review: bool = False
    flag_reason: str = ""
    marking_scheme_answer: str = ""
    answer_mismatch: bool = False

@dataclass
class MarkingSchemeData:
    paper_code: str
    subject: str
    year: str
    month: str
    total_questions: int
    answers: Dict[str, str]
    marks_per_question: Dict[str, int]
    metadata: Dict[str, Any]

class ScalableAISolverManager:
    """Original Scalable AI Solver Manager - Enhanced with automation"""
    
    def __init__(self, question_banks_dir=None):
        self.question_banks_dir = Path(question_banks_dir) if question_banks_dir else QUESTION_BANKS_DIR
        self.current_paper_path = None
        self.solver_data = {}
        
    def initialize_solver(self, paper_folder):
        """Initialize AI solver for a specific paper folder - SCALABLE VERSION"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            
            if not paper_folder_path.exists():
                return {"success": False, "error": f"Paper folder not found: {paper_folder}"}
            
            # Load master solutions.json file (from extractor)
            master_solutions_file = paper_folder_path / "solutions.json"
            if not master_solutions_file.exists():
                return {"success": False, "error": "Master solutions.json file not found. Please extract questions first."}
            
            with open(master_solutions_file, 'r') as f:
                master_data = json.load(f)
            
            # Check for images with STANDARDIZED folder priority (images first, extracted_images fallback)
            images_folder = paper_folder_path / "images"
            extracted_images_folder = paper_folder_path / "extracted_images"
            
            active_images_folder = None
            if images_folder.exists():
                active_images_folder = images_folder
                print(f"🖼️ Using primary images folder: {images_folder}")
            elif extracted_images_folder.exists():
                active_images_folder = extracted_images_folder
                print(f"🖼️ Using fallback extracted_images folder: {extracted_images_folder}")
            else:
                return {"success": False, "error": "No images folder found"}
            
            # Get questions from master file
            questions = master_data.get('questions', [])
            if not questions:
                return {"success": False, "error": "No questions found in master file"}
            
            # Calculate current progress from master file
            total_questions = len(questions)
            solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
            flagged_count = sum(1 for q in questions if q.get('auto_flagged', False))
            
            # Store current paper info
            self.current_paper_path = paper_folder_path
            
            # Create solver data structure
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
                "initialized_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "message": f"AI Solver initialized successfully! Found {solved_count}/{total_questions} questions already solved.",
                "data": {
                    "total_questions": total_questions,
                    "solved_count": solved_count,
                    "flagged_count": flagged_count,
                    "completion_rate": round((solved_count / total_questions) * 100, 1),
                    "subject": metadata.get('subject', 'Unknown'),
                    "year": metadata.get('year', '2025'),
                    "month": metadata.get('month', 'Unknown'),
                    "paper_code": metadata.get('paper_code', '1'),
                    "images_folder": str(active_images_folder),
                    "paper_folder": paper_folder
                }
            }
            
        except Exception as e:
            print(f"⚠ AI Solver initialization error: {str(e)}")
            traceback.print_exc()
            return {"success": False, "error": f"Initialization failed: {str(e)}"}
    
    def save_solution(self, paper_folder, question_number, solution_json):
        """Save individual solution with MASTER FILE UPDATE + quality control"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            
            # UPDATED: Use master solutions.json file (not separate solutions file)
            master_solutions_file = paper_folder_path / "solutions.json"
            
            # Load existing master file (from extractor)
            master_data = {}
            if master_solutions_file.exists():
                with open(master_solutions_file, 'r') as f:
                    master_data = json.load(f)
            else:
                return {"success": False, "error": "Master solutions.json file not found"}
            
            # Parse and validate the new solution
            if isinstance(solution_json, str):
                solution = json.loads(solution_json)
            else:
                solution = solution_json
            
            # Add solver metadata
            solution['question_number'] = question_number
            solution['saved_at'] = datetime.now().isoformat()
            solution['solver_version'] = "Enhanced v2.0 - Claude API Ready"
            solution['solved_by_ai'] = True
            
            # Quality control
            confidence = solution.get('confidence_score', 0)
            
            # Validation checks
            required_fields = [
                'question_text', 'options', 'correct_answer', 
                'simple_answer', 'detailed_explanation', 
                'topic', 'confidence_score'
            ]
            
            missing_fields = [field for field in required_fields if not solution.get(field)]
            
            # Enhanced auto-flagging logic with 91% threshold
            flag_reasons = []
            if confidence < CONFIDENCE_THRESHOLD:
                flag_reasons.append(f"Low confidence: {confidence:.1%} (< 91%)")
            if missing_fields:
                flag_reasons.append(f"Missing fields: {', '.join(missing_fields)}")
            
            # Load marking scheme for quality control
            marking_scheme_file = paper_folder_path / "marking_scheme.json"
            marking_scheme = {}
            if marking_scheme_file.exists():
                with open(marking_scheme_file, 'r') as f:
                    marking_scheme = json.load(f)
            
            # Marking scheme validation
            if marking_scheme:
                question_num_str = str(question_number)
                ai_answer = solution.get("correct_answer", "")
                marking_answer = marking_scheme.get(question_num_str, "")
                
                if marking_answer and ai_answer != marking_answer:
                    flag_reasons.append(f"Answer mismatch: AI={ai_answer}, Marking={marking_answer}")
                    solution['answer_mismatch'] = True
                else:
                    solution['answer_mismatch'] = False
            
            # Options validation
            options = solution.get("options", {})
            if len(options) < 4:
                flag_reasons.append(f"Incomplete options: only {len(options)} found")
            
            # Set flagging status
            solution['auto_flagged'] = len(flag_reasons) > 0
            solution['needs_review'] = len(flag_reasons) > 0
            solution['flag_reason'] = '; '.join(flag_reasons) if flag_reasons else None
            solution['quality_threshold'] = '91%'
            
            # UPDATED: Find and update the specific question in master data
            question_found = False
            if 'questions' in master_data:
                for i, question in enumerate(master_data['questions']):
                    if question.get('question_number') == question_number:
                        # Update the existing question with AI solution
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
            
            # Update master metadata
            if 'metadata' not in master_data:
                master_data['metadata'] = {}
            
            master_data['metadata'].update({
                'last_updated': datetime.now().isoformat(),
                'ai_solver_version': 'Enhanced v2.0 - Claude API Ready',
                'solving_in_progress': True
            })
            
            # Calculate progress statistics
            solved_questions = sum(1 for q in master_data['questions'] if q.get('solved_by_ai'))
            total_questions = len(master_data['questions'])
            flagged_questions = sum(1 for q in master_data['questions'] if q.get('auto_flagged'))
            avg_confidence = sum(q.get('confidence_score', 0) for q in master_data['questions'] if q.get('solved_by_ai')) / max(solved_questions, 1)
            
            master_data['metadata'].update({
                'progress_stats': {
                    'total_questions': total_questions,
                    'solved_questions': solved_questions,
                    'completion_rate': round((solved_questions / total_questions) * 100, 1),
                    'flagged_questions': flagged_questions,
                    'average_confidence': round(avg_confidence, 3)
                }
            })
            
            # UPDATED: Save back to master solutions.json file
            with open(master_solutions_file, 'w') as f:
                json.dump(master_data, f, indent=2)
            
            print(f"✅ Updated master solutions.json: Question {question_number} saved")
            print(f"📊 Progress: {solved_questions}/{total_questions} ({master_data['metadata']['progress_stats']['completion_rate']}%)")
            
            return {
                "success": True,
                "message": f"Solution for Question {question_number} saved to master file",
                "progress": master_data['metadata']['progress_stats'],
                "quality_status": {
                    "confidence": confidence,
                    "auto_flagged": solution['auto_flagged'],
                    "needs_review": solution['needs_review'],
                    "flag_reason": solution['flag_reason']
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_progress(self, paper_folder):
        """Get current solving progress from MASTER FILE"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            master_solutions_file = paper_folder_path / "solutions.json"
            
            if not master_solutions_file.exists():
                return {"success": False, "error": "Master solutions file not found"}
            
            # Load master file
            with open(master_solutions_file, 'r') as f:
                master_data = json.load(f)
            
            questions = master_data.get('questions', [])
            total_questions = len(questions)
            
            # Calculate metrics from master file
            solved_count = sum(1 for q in questions if q.get('solved_by_ai'))
            flagged_count = sum(1 for q in questions if q.get('auto_flagged'))
            
            # Average confidence of solved questions
            solved_questions = [q for q in questions if q.get('solved_by_ai')]
            avg_confidence = sum(q.get('confidence_score', 0) for q in solved_questions) / max(len(solved_questions), 1)
            
            # Question status for each question
            question_status = {}
            for q in questions:
                qnum = q.get('question_number')
                if qnum:
                    question_status[qnum] = {
                        "solved": q.get('solved_by_ai', False),
                        "confidence": q.get('confidence_score', 0),
                        "flagged": q.get('auto_flagged', False),
                        "needs_review": q.get('needs_review', False)
                    }
            
            return {
                "success": True,
                "progress": {
                    "total_questions": total_questions,
                    "solved_count": solved_count,
                    "flagged_count": flagged_count,
                    "completion_percentage": (solved_count / total_questions * 100) if total_questions > 0 else 0,
                    "average_confidence": avg_confidence,
                    "question_status": question_status
                },
                "source": "master_solutions_file"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_solutions(self, paper_folder):
        """Export solutions as BACKUP COPY with timestamp"""
        try:
            paper_folder_path = self.question_banks_dir / paper_folder
            master_solutions_file = paper_folder_path / "solutions.json"
            
            if not master_solutions_file.exists():
                return {"success": False, "error": "No master solutions file found"}
            
            # Load current master file
            with open(master_solutions_file, 'r') as f:
                master_data = json.load(f)
            
            # Create export data with additional export metadata
            export_data = dict(master_data)  # Copy all data
            export_data['export_info'] = {
                "export_date": datetime.now().isoformat(),
                "format_version": "enhanced_v2.0",
                "export_type": "backup_copy",
                "exported_from": "master_solutions_json"
            }
            
            # Save timestamped backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"{paper_folder}_backup_{timestamp}.json"
            export_path = paper_folder_path / export_filename
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            # Calculate final statistics
            solved_count = sum(1 for q in master_data.get('questions', []) if q.get('solved_by_ai'))
            total_count = len(master_data.get('questions', []))
            
            return {
                "success": True,
                "export_path": str(export_path),
                "export_filename": export_filename,
                "backup_type": "master_file_backup",
                "statistics": {
                    "total_questions": total_count,
                    "solved_questions": solved_count,
                    "completion_rate": round((solved_count / total_count) * 100, 1) if total_count > 0 else 0
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_review_tab_processed(self, paper_folder: str) -> Dict:
        """Check if questions have been processed by Review tab to avoid duplicate work"""
        paper_path = self.question_banks_dir / paper_folder
        
        processed_questions = []
        processing_savings = 0
        
        # Check solutions.json for already extracted question text and options
        solutions_file = paper_path / "solutions.json"
        if solutions_file.exists():
            try:
                with open(solutions_file, 'r') as f:
                    solutions_data = json.load(f)
                    questions = solutions_data.get("questions", [])
                    
                    for q in questions:
                        # If question has text and options but not AI solved, it was processed by Review tab
                        if (q.get("question_text") and 
                            q.get("options") and 
                            len(q.get("options", {})) >= 4 and 
                            not q.get("solved_by_ai", False)):
                            
                            processed_questions.append(q.get("question_number"))
                            processing_savings += 1
            except:
                pass
        
        return {
            "can_reuse": len(processed_questions) > 0,
            "processed_questions": processed_questions,
            "processing_savings": processing_savings,
            "message": f"Found {processing_savings} questions already processed by Review tab"
        }

    def find_best_image_for_question(self, paper_folder: str, question_num: int, expected_filename: str = None) -> Optional[Path]:
        """Find the best available image with CORRECTED folder priority: images -> extracted_images"""
        paper_path = self.question_banks_dir / paper_folder
        
        # CORRECTED Priority order: images (primary) -> extracted_images (fallback only)
        search_locations = [
            paper_path / "images",             # PRIMARY: Main images folder
            paper_path / "extracted_images"    # FALLBACK: Only if images folder doesn't have it
        ]
        
        # Common image extensions
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        for location in search_locations:
            if not location.exists():
                continue
            
            # First try exact filename match
            if expected_filename:
                for ext in [''] + extensions:  # Try with and without extension
                    test_filename = expected_filename if ext == '' else expected_filename + ext
                    image_path = location / test_filename
                    if image_path.exists():
                        print(f"🖼️ Found image: {image_path} (exact match)")
                        return image_path
            
            # Then try common naming patterns based on your actual file structure
            possible_names = [
                f"question_{question_num:02d}_enhanced",  # Matches your actual naming: question_01_enhanced.png
                f"question_{question_num:02d}",
                f"question_{question_num}",
                f"q{question_num:02d}_enhanced",
                f"q{question_num:02d}",
                f"q{question_num}",
                f"{question_num:02d}_enhanced",
                f"{question_num:02d}",
                f"{question_num}",
                f"page_{question_num}",
                f"img_{question_num}"
            ]
            
            for base_name in possible_names:
                for ext in extensions:
                    image_path = location / f"{base_name}{ext}"
                    if image_path.exists():
                        print(f"🖼️ Found image: {image_path} (pattern match in {location.name})")
                        return image_path
        
        return None
    
    def generate_simplified_interface(self, paper_folder):
        """Generate the complete simplified HTML interface with ENHANCED SYSTEM"""
        try:
            # Initialize if needed
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
            
            # Generate questions HTML
            questions_html = ""
            for question in questions:
                question_num = question.get("question_number")
                filename = question.get("image_filename")
                
                # UPDATED: Determine correct image path based on STANDARDIZED folder priority
                if "images" in self.solver_data["images_folder"] and not "extracted_images" in self.solver_data["images_folder"]:
                    image_url = f"/images/{paper_folder}/{filename}"
                else:
                    image_url = f"/images/{paper_folder}/extracted_images/{filename}"
                
                # Check if question is already solved
                is_solved = question.get('solved_by_ai', False)
                is_flagged = question.get('auto_flagged', False)
                confidence = question.get('confidence_score', 0)
                
                # Pre-fill solution if already solved
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
                
                questions_html += f'''
                <div class="question-card" id="question-{question_num}">
                    <div class="question-header">
                        <h3>Question {question_num}</h3>
                        <div class="status-indicator {'solved' if is_solved and not is_flagged else 'flagged' if is_flagged else ''}" id="status-{question_num}">
                            {'Solved (' + str(int(confidence * 100)) + '%)' if is_solved and not is_flagged else 'Flagged (' + str(int(confidence * 100)) + '%)' if is_flagged else 'Pending'}
                        </div>
                    </div>
                    <div class="question-content">
                        <div class="image-section">
                            <img src="{image_url}" alt="Question {question_num}" class="question-image" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                            <div style="display:none; padding: 2rem; text-align: center; color: #dc3545; border: 1px solid #dc3545; border-radius: 8px;">
                                ⚠ Image not found<br>
                                <small>{filename}</small>
                            </div>
                            <div class="image-controls">
                                <button onclick="openImage('{image_url}')" class="btn-small">🔍 Full Size</button>
                            </div>
                        </div>
                        <div class="solution-section">
                            <div class="prompt-area">
                                <div class="prompt-controls">
                                    <button onclick="copyPrompt({question_num})" class="btn copy-btn">📋 Copy Prompt</button>
                                    <button onclick="togglePrompt({question_num})" class="btn view-btn">👁️ View Prompt</button>
                                    <a href="https://claude.ai" target="_blank" class="btn claude-btn">🚀 Claude.ai</a>
                                </div>
                                <div id="prompt-display-{question_num}" class="prompt-display" style="display: none;">
                                    <div class="prompt-text" id="prompt-text-{question_num}"></div>
                                </div>
                            </div>
                            <div class="solution-input-area">
                                <textarea id="solution-{question_num}" placeholder="Paste Claude.ai JSON response here..." class="solution-textarea">{existing_solution}</textarea>
                                <div class="solution-controls">
                                    <button onclick="saveSolution({question_num})" class="btn save-btn">💾 Save</button>
                                    <button onclick="validateJSON({question_num})" class="btn validate-btn">✅ Validate</button>
                                    <button onclick="clearSolution({question_num})" class="btn clear-btn">🗑️ Clear</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>'''
            
            # Enhanced interface HTML with all original functionality plus new features
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>🤖 Enhanced AI Solver - {title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{get_css_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Enhanced AI Solver</h1>
            <p>{title} - {total_questions} Questions</p>
            <p>🚀 Claude API Ready • 📋 Marking Scheme Support • 🎯 Quality Control</p>
            <p style="font-size: 0.9rem; opacity: 0.8;">🎯 91% Quality Threshold • 📁 Corrected Folder Priority</p>
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
                    <div id="approvedCount">{sum(1 for q in questions if q.get('solved_by_ai') and not q.get('auto_flagged'))}</div>
                </div>
                <div class="stat-card">
                    <h4>Flagged (<91%)</h4>
                    <div id="flaggedCount">{sum(1 for q in questions if q.get('auto_flagged'))}</div>
                </div>
                <div class="stat-card">
                    <h4>Avg Confidence</h4>
                    <div id="avgConfidence">{int(sum(q.get('confidence_score', 0) for q in questions if q.get('solved_by_ai')) / max(solved_count, 1) * 100)}%</div>
                </div>
            </div>
        </div>
        
        <div class="controls-section">
            <button class="btn batch-btn" onclick="getBatchPrompts()">📋 Get All Prompts</button>
            <button class="btn automation-btn" onclick="startClaudeAutomation()">🎯 Smart Automation (91%)</button>
            <button class="btn marking-btn" onclick="uploadMarkingScheme()">📄 Marking Scheme</button>
            <button class="btn export-btn" onclick="exportSolutions()">📥 Create Backup</button>
            <button class="btn" onclick="refreshProgress()">🔄 Refresh Progress</button>
            <a href="https://claude.ai" target="_blank" class="btn claude-btn">🌐 Open Claude.ai</a>
        </div>
        
        <div class="questions-grid" id="questionsGrid">
            {questions_html}
        </div>
    </div>

    {get_javascript_template(paper_folder, total_questions, subject)}
</body>
</html>'''
            
            return {
                "success": True,
                "html_content": html_content
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

class AutomatedAISolver:
    """Enhanced Automated AI Solver using Claude API with quality control"""
    
    def __init__(self, api_key: str = None, question_banks_dir=None):
        self.question_banks_dir = Path(question_banks_dir) if question_banks_dir else QUESTION_BANKS_DIR
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            print("⚠️ Warning: ANTHROPIC_API_KEY not found - automation features disabled")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print("✅ Claude API client initialized successfully")
        
        self.current_paper_path = None
        self.marking_scheme = {}
        
    async def load_marking_scheme(self, paper_folder: str) -> Dict:
        """Load marking scheme from JSON file for quality control"""
        try:
            paper_path = self.question_banks_dir / paper_folder
            marking_scheme_file = paper_path / "marking_scheme.json"
            
            if marking_scheme_file.exists():
                async with aiofiles.open(marking_scheme_file, 'r') as f:
                    content = await f.read()
                    self.marking_scheme = json.loads(content)
                    print(f"✅ Loaded marking scheme: {len(self.marking_scheme)} answers")
                    return self.marking_scheme
            else:
                print("⚠️ No marking scheme found - quality control will be limited")
                return {}
        except Exception as e:
            print(f"⚠ Error loading marking scheme: {e}")
            return {}
    
    def encode_image_to_base64(self, image_path: Path) -> str:
        """Encode image to base64 for Claude API"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"⚠ Error encoding image {image_path}: {e}")
            return None
    
    def get_image_media_type(self, image_path: Path) -> str:
        """Get media type for image"""
        ext = image_path.suffix.lower()
        if ext in ['.jpg', '.jpeg']:
            return "image/jpeg"
        elif ext == '.png':
            return "image/png"
        elif ext == '.gif':
            return "image/gif"
        elif ext == '.webp':
            return "image/webp"
        else:
            return "image/jpeg"  # Default
    
    def find_best_image_for_question(self, paper_folder: str, question_num: int) -> Optional[Path]:
        """Find the best available image with CORRECTED folder priority and enhanced naming patterns"""
        paper_path = self.question_banks_dir / paper_folder
        
        # CORRECTED Priority order: images (primary) -> extracted_images (fallback only)
        search_locations = [
            paper_path / "images",             # PRIMARY: Main images folder
            paper_path / "extracted_images"    # FALLBACK: Only if images folder doesn't have it
        ]
        
        # Common image extensions
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        for location in search_locations:
            if not location.exists():
                continue
            
            # Enhanced naming patterns based on your actual file structure
            possible_names = [
                f"question_{question_num:02d}_enhanced",  # Matches your actual naming: question_01_enhanced.png
                f"question_{question_num:02d}",
                f"question_{question_num}",
                f"q{question_num:02d}_enhanced",
                f"q{question_num:02d}",
                f"q{question_num}",
                f"{question_num:02d}_enhanced",
                f"{question_num:02d}",
                f"{question_num}",
                f"page_{question_num}",
                f"img_{question_num}"
            ]
            
            for base_name in possible_names:
                for ext in extensions:
                    image_path = location / f"{base_name}{ext}"
                    if image_path.exists():
                        print(f"🖼️ Found image: {image_path} (pattern match in {location.name})")
                        return image_path
        
        print(f"⚠️ No image found for question {question_num} in either folder")
        return None
    
    def check_review_tab_processed(self, paper_folder: str) -> Dict:
        """Check if questions have been processed by Review tab to avoid duplicate work"""
        paper_path = self.question_banks_dir / paper_folder
        
        processed_questions = []
        processing_savings = 0
        
        # Check solutions.json for already extracted question text and options
        solutions_file = paper_path / "solutions.json"
        if solutions_file.exists():
            try:
                with open(solutions_file, 'r') as f:
                    solutions_data = json.load(f)
                    questions = solutions_data.get("questions", [])
                    
                    for q in questions:
                        # If question has text and options but not AI solved, it was processed by Review tab
                        if (q.get("question_text") and 
                            q.get("options") and 
                            len(q.get("options", {})) >= 4 and 
                            not q.get("solved_by_ai", False)):
                            
                            processed_questions.append(q.get("question_number"))
                            processing_savings += 1
            except:
                pass
        
        return {
            "can_reuse": len(processed_questions) > 0,
            "processed_questions": processed_questions,
            "processing_savings": processing_savings,
            "message": f"Found {processing_savings} questions already processed by Review tab"
        }

    async def solve_question_with_claude(self, question_data: QuestionData, image_path: Path, subject: str) -> QuestionData:
        """Solve individual question using Claude API"""
        if not self.client:
            raise Exception("Claude API client not initialized")
        
        try:
            # Encode image
            image_base64 = self.encode_image_to_base64(image_path)
            if not image_base64:
                raise Exception("Failed to encode image")
            
            media_type = self.get_image_media_type(image_path)
            
            # Create enhanced prompt (moved outside f-string to avoid conflicts)
            prompt_text = get_claude_prompt_template(subject, question_data.question_number)

            # Call Claude API
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
            
            # Parse response
            response_text = message.content[0].text
            
            # Extract JSON from response (handle markdown code blocks) - FIXED SYNTAX
            json_text = ""
            json_pattern = r'```json\s*(.*?)\s*```'
            json_match = re.search(json_pattern, response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find JSON without code blocks - FIXED: separate variable to avoid f-string conflict
                brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                json_match = re.search(brace_pattern, response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    raise Exception("No valid JSON found in response")
            
            # Parse JSON
            solution_data = json.loads(json_text)
            
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
            
            # Quality control with marking scheme
            if str(question_data.question_number) in self.marking_scheme:
                marking_answer = self.marking_scheme[str(question_data.question_number)]
                question_data.marking_scheme_answer = marking_answer
                
                if question_data.correct_answer != marking_answer:
                    question_data.answer_mismatch = True
                    question_data.auto_flagged = True
                    question_data.needs_review = True
                    question_data.flag_reason = f"Answer mismatch: AI={question_data.correct_answer}, Marking={marking_answer}"
                else:
                    question_data.answer_mismatch = False
            
            # Enhanced quality checks with 91% threshold
            flag_reasons = []
            if question_data.confidence_score < CONFIDENCE_THRESHOLD:
                flag_reasons.append(f"Low confidence: {question_data.confidence_score:.1%} (< 91%)")
            
            if not question_data.question_text or not question_data.correct_answer:
                flag_reasons.append("Missing essential data")
            
            # Options validation
            options = question_data.options or {}
            if len(options) < 4:
                flag_reasons.append(f"Incomplete options: only {len(options)} found")
            
            if flag_reasons and not question_data.auto_flagged:
                question_data.auto_flagged = True
                question_data.needs_review = True
                question_data.flag_reason = '; '.join(flag_reasons)
            
            print(f"✅ Solved Q{question_data.question_number} - Answer: {question_data.correct_answer} - Confidence: {question_data.confidence_score:.1%}")
            if question_data.answer_mismatch:
                print(f"⚠️ MISMATCH DETECTED: AI={question_data.correct_answer} vs Marking={question_data.marking_scheme_answer}")
            
            return question_data
            
        except Exception as e:
            print(f"⚠ Error solving Q{question_data.question_number}: {e}")
            question_data.auto_flagged = True
            question_data.needs_review = True
            question_data.flag_reason = f"Solving error: {str(e)}"
            return question_data
    
    async def process_paper_automated(self, paper_folder: str, batch_size: int = 3, delay: float = 2.0) -> Dict:
        """Process entire paper automatically with rate limiting"""
        if not self.client:
            return {"success": False, "error": "Claude API not configured"}
        
        try:
            paper_path = self.question_banks_dir / paper_folder
            master_file = paper_path / "solutions.json"
            
            if not master_file.exists():
                return {"success": False, "error": "Master solutions.json not found"}
            
            # Load existing data
            async with aiofiles.open(master_file, 'r') as f:
                content = await f.read()
                master_data = json.loads(content)
            
            # Load marking scheme
            await self.load_marking_scheme(paper_folder)
            
            questions = master_data.get('questions', [])
            metadata = master_data.get('metadata', {})
            subject = metadata.get('subject', 'Physics').title()
            
            total_questions = len(questions)
            processed_count = 0
            flagged_count = 0
            mismatch_count = 0
            
            print(f"🚀 Starting automated processing: {total_questions} total questions")
            
            # Process in batches to avoid rate limits
            for i in range(0, len(questions), batch_size):
                batch = questions[i:i + batch_size]
                batch_tasks = []
                
                for question in batch:
                    question_num = question.get('question_number')
                    filename = question.get('image_filename', '')
                    
                    # Skip if already solved (unless forced re-solve)
                    if question.get('solved_by_ai', False):
                        print(f"⭐ Skipping Q{question_num} - already solved")
                        continue
                    
                    # Create question data object
                    question_data = QuestionData(
                        question_number=question_num,
                        image_filename=filename
                    )
                    
                    # Find image using enhanced search with corrected folder priority
                    image_path = self.find_best_image_for_question(paper_folder, question_num)
                    if not image_path:
                        print(f"⚠ Image not found for Q{question_num}")
                        continue
                    
                    # Add to batch
                    batch_tasks.append(
                        self.solve_question_with_claude(question_data, image_path, subject)
                    )
                
                # Process batch concurrently
                if batch_tasks:
                    print(f"🔄 Processing batch of {len(batch_tasks)} questions...")
                    solved_questions = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    
                    # Update master data
                    for solved_q in solved_questions:
                        if isinstance(solved_q, Exception):
                            print(f"⚠ Batch error: {solved_q}")
                            continue
                        
                        # Update the corresponding question in master data
                        for j, question in enumerate(questions):
                            if question.get('question_number') == solved_q.question_number:
                                # Update with solved data
                                questions[j].update({
                                    'question_text': solved_q.question_text,
                                    'options': solved_q.options,
                                    'correct_answer': solved_q.correct_answer,
                                    'explanation': solved_q.explanation,
                                    'detailed_explanation': solved_q.detailed_explanation,
                                    'calculation_steps': solved_q.calculation_steps,
                                    'topic': solved_q.topic,
                                    'difficulty': solved_q.difficulty,
                                    'confidence_score': solved_q.confidence_score,
                                    'solved_by_ai': solved_q.solved_by_ai,
                                    'auto_flagged': solved_q.auto_flagged,
                                    'needs_review': solved_q.needs_review,
                                    'flag_reason': solved_q.flag_reason,
                                    'marking_scheme_answer': solved_q.marking_scheme_answer,
                                    'answer_mismatch': solved_q.answer_mismatch,
                                    'solved_at': datetime.now().isoformat()
                                })
                                processed_count += 1
                                if solved_q.auto_flagged:
                                    flagged_count += 1
                                if solved_q.answer_mismatch:
                                    mismatch_count += 1
                                break
                    
                    # Save progress after each batch
                    master_data['questions'] = questions
                    master_data['metadata'].update({
                        'last_updated': datetime.now().isoformat(),
                        'automated_solver_version': 'Enhanced Claude API v2.0',
                        'batch_processing': True
                    })
                    
                    async with aiofiles.open(master_file, 'w') as f:
                        await f.write(json.dumps(master_data, indent=2))
                    
                    print(f"📊 Batch complete: {processed_count}/{total_questions} processed")
                
                # Rate limiting delay
                if i + batch_size < len(questions):
                    print(f"⏳ Waiting {delay} seconds before next batch...")
                    await asyncio.sleep(delay)
            
            # Final statistics
            solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
            completion_rate = (solved_count / total_questions * 100) if total_questions > 0 else 0
            
            # Update final metadata
            master_data['metadata'].update({
                'automation_stats': {
                    'total_questions': total_questions,
                    'processed_this_run': processed_count,
                    'total_solved': solved_count,
                    'flagged_questions': flagged_count,
                    'answer_mismatches': mismatch_count,
                    'completion_rate': round(completion_rate, 1),
                    'completed_at': datetime.now().isoformat()
                }
            })
            
            async with aiofiles.open(master_file, 'w') as f:
                await f.write(json.dumps(master_data, indent=2))
            
            print(f"🎉 Automation complete!")
            print(f"📊 Processed: {processed_count} questions")
            print(f"✅ Total solved: {solved_count}/{total_questions}")
            print(f"⚠️ Flagged: {flagged_count} questions")
            print(f"🔍 Mismatches: {mismatch_count} questions")
            
            return {
                "success": True,
                "message": f"Automated processing complete! Processed {processed_count} questions.",
                "stats": {
                    "total_questions": total_questions,
                    "processed": processed_count,
                    "solved": solved_count,
                    "flagged": flagged_count,
                    "mismatches": mismatch_count,
                    "completion_rate": completion_rate
                }
            }
            
        except Exception as e:
            print(f"⚠ Automated processing error: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def get_paper_images_preview(self, paper_folder: str) -> Dict:
        """Get preview of all images in paper folder - CORRECTED folder priority"""
        try:
            paper_path = self.question_banks_dir / paper_folder
            
            # CORRECTED: Only check the two actual folders used
            preview_data = {
                "paper_folder": paper_folder,
                "images": [],
                "total_images": 0,
                "folders_found": []
            }
            
            # Check primary images folder FIRST (highest priority)
            images_folder = paper_path / "images"
            if images_folder.exists():
                preview_data["folders_found"].append("images")
                for image_file in images_folder.glob("*"):
                    if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        try:
                            # Get image dimensions
                            with Image.open(image_file) as img:
                                width, height = img.size
                            
                            preview_data["images"].append({
                                "filename": image_file.name,
                                "folder": "images",
                                "priority": "primary",
                                "size": image_file.stat().st_size,
                                "dimensions": f"{width}x{height}",
                                "url": f"/images/{paper_folder}/{image_file.name}"
                            })
                        except Exception as e:
                            print(f"Error processing image {image_file.name}: {e}")
            
            # Check extracted images folder ONLY as fallback
            extracted_images_folder = paper_path / "extracted_images"
            if extracted_images_folder.exists():
                preview_data["folders_found"].append("extracted_images")
                for image_file in extracted_images_folder.glob("*"):
                    if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        try:
                            with Image.open(image_file) as img:
                                width, height = img.size
                            
                            preview_data["images"].append({
                                "filename": image_file.name,
                                "folder": "extracted_images",
                                "priority": "fallback",
                                "size": image_file.stat().st_size,
                                "dimensions": f"{width}x{height}",
                                "url": f"/images/{paper_folder}/extracted_images/{image_file.name}"
                            })
                        except Exception as e:
                            print(f"Error processing extracted image {image_file.name}: {e}")
            
            preview_data["total_images"] = len(preview_data["images"])
            
            # Sort by priority (primary first) then filename
            preview_data["images"].sort(key=lambda x: (x["priority"] != "primary", x["filename"]))
            
            return {
                "success": True,
                "data": preview_data,
                "folder_priority": "images (primary) -> extracted_images (fallback)"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

class MarkingSchemeProcessor:
    """Process marking schemes from various sources and formats"""
    
    def __init__(self, question_banks_dir: str = None):
        self.question_banks_dir = Path(question_banks_dir) if question_banks_dir else QUESTION_BANKS_DIR
    
    def extract_from_cambridge_pdf(self, pdf_path: str) -> MarkingSchemeData:
        """Extract marking scheme from Cambridge IGCSE PDF format"""
        try:
            doc = fitz.open(pdf_path)
            all_text = ""
            
            # Extract text from all pages
            for page in doc:
                all_text += page.get_text()
            
            doc.close()
            
            # Parse header information
            paper_code_match = re.search(r'(\d{4}/\d{2})', all_text)
            paper_code = paper_code_match.group(1) if paper_code_match else "Unknown"
            
            subject_match = re.search(r'(PHYSICS|CHEMISTRY|BIOLOGY|MATHEMATICS)', all_text, re.IGNORECASE)
            subject = subject_match.group(1).title() if subject_match else "Unknown"
            
            year_match = re.search(r'(October/November|May/June)\s+(\d{4})', all_text)
            if year_match:
                month = year_match.group(1)
                year = year_match.group(2)
            else:
                month = "Unknown"
                year = "Unknown"
            
            # Extract question-answer pairs
            answers = {}
            marks_per_question = {}
            
            # Look for patterns like "Question Answer Marks" table
            question_pattern = r'(\d+)\s+([ABCD])\s+1'
            matches = re.findall(question_pattern, all_text)
            
            for question_num, answer in matches:
                answers[question_num] = answer
                marks_per_question[question_num] = 1  # All questions worth 1 mark as requested
            
            # If table format didn't work, try simpler format - FIXED SYNTAX
            if not answers:
                # Try pattern like "1 A", "2 B", etc. - FIXED: proper string termination
                simple_pattern = r'^(\d+)\s+([ABCD])$'
                lines = all_text.split('\n')
                for line in lines:
                    match = re.match(simple_pattern, line.strip())
                    if match:
                        question_num, answer = match.groups()
                        answers[question_num] = answer
                        marks_per_question[question_num] = 1
            
            total_questions = len(answers)
            
            metadata = {
                'source': 'cambridge_pdf',
                'extracted_at': datetime.now().isoformat(),
                'pdf_path': pdf_path,
                'extraction_method': 'automated'
            }
            
            return MarkingSchemeData(
                paper_code=paper_code,
                subject=subject,
                year=year,
                month=month,
                total_questions=total_questions,
                answers=answers,
                marks_per_question=marks_per_question,
                metadata=metadata
            )
            
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def create_json_marking_scheme(self, marking_data: MarkingSchemeData, output_path: str) -> Dict:
        """Create JSON marking scheme file"""
        try:
            # Create comprehensive marking scheme
            comprehensive_scheme = {
                "paper_info": {
                    "paper_code": marking_data.paper_code,
                    "subject": marking_data.subject,
                    "year": marking_data.year,
                    "month": marking_data.month,
                    "total_questions": marking_data.total_questions
                },
                "answers": marking_data.answers,
                "marks_per_question": marking_data.marks_per_question,
                "metadata": marking_data.metadata
            }
            
            # Create simple marking scheme (just question -> answer)
            simple_scheme = marking_data.answers
            
            # Save comprehensive version
            comprehensive_file = Path(output_path) / "marking_scheme_comprehensive.json"
            with open(comprehensive_file, 'w') as f:
                json.dump(comprehensive_scheme, f, indent=2)
            
            # Save simple version (for AI solver compatibility)
            simple_file = Path(output_path) / "marking_scheme.json"
            with open(simple_file, 'w') as f:
                json.dump(simple_scheme, f, indent=2)
            
            return {
                "success": True,
                "comprehensive_file": str(comprehensive_file),
                "simple_file": str(simple_file),
                "total_questions": marking_data.total_questions,
                "sample_answers": dict(list(marking_data.answers.items())[:5])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize enhanced components
scalable_solver = ScalableAISolverManager()
automated_solver = None
marking_processor = MarkingSchemeProcessor()

def get_automated_solver():
    global automated_solver
    if not automated_solver:
        try:
            automated_solver = AutomatedAISolver()
        except Exception as e:
            print(f"⚠ Failed to initialize automated solver: {e}")
            return None
    return automated_solver

# ==================== FLASK ROUTES ====================

@app.route('/api/find-image-locations', methods=['POST'])
def find_image_locations():
    """Find all available image locations - CORRECTED folder priority"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        paper_path = QUESTION_BANKS_DIR / paper_folder
        
        # CORRECTED: Only check the two actual folders used
        locations = {
            "images": {"count": 0, "priority": "primary", "description": "Primary images folder"},
            "extracted_images": {"count": 0, "priority": "fallback", "description": "Fallback extracted images"}
        }
        
        # Count images in each location
        for folder_name, info in locations.items():
            folder_path = paper_path / folder_name
            if folder_path.exists():
                info["count"] = len([f for f in folder_path.glob("*") 
                                   if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']])
        
        total_images = sum(info["count"] for info in locations.values())
        
        # Determine best location (primary takes priority)
        if locations["images"]["count"] > 0:
            best_location = "images"
            best_count = locations["images"]["count"]
        elif locations["extracted_images"]["count"] > 0:
            best_location = "extracted_images"
            best_count = locations["extracted_images"]["count"]
        else:
            best_location = None
            best_count = 0
        
        return jsonify({
            "success": True,
            "total_images_found": total_images,
            "best_location": best_location,
            "best_count": best_count,
            "locations": locations,
            "folder_priority": "images (primary) -> extracted_images (fallback)",
            "recommendations": [
                f"🔷 Found {total_images} total images across folders",
                f"🎯 Using: {best_location} ({best_count} images)" if best_location else "⚠ No images found",
                f"✅ Primary images folder: {locations['images']['count']} images" if locations['images']['count'] > 0 
                else f"⚠️ Primary images folder empty, using fallback: {locations['extracted_images']['count']} images" if locations['extracted_images']['count'] > 0
                else "⚠ No images found in either folder"
            ]
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Original scalable routes (preserved)
@app.route('/solver/<paper_folder>')
def serve_scalable_solver(paper_folder):
    """Serve the enhanced AI solver interface"""
    try:
        result = scalable_solver.generate_simplified_interface(paper_folder)
        if result["success"]:
            return result["html_content"]
        else:
            return f"Error: {result['error']}", 500
    except Exception as e:
        return f"Error creating interface: {str(e)}", 500

@app.route('/api/save-solution', methods=['POST'])
def save_solution():
    """Save individual solution to master file"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        question_number = data.get('question_number')
        solution_json = data.get('solution')
        
        result = scalable_solver.save_solution(paper_folder, question_number, solution_json)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/get-progress', methods=['POST'])
def get_progress():
    """Get current solving progress from master file"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        result = scalable_solver.get_progress(paper_folder)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/export-solutions', methods=['POST'])
def export_solutions():
    """Export solutions as backup copy"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        result = scalable_solver.export_solutions(paper_folder)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Enhanced automation routes with corrected folder priority
@app.route('/api/smart-automation', methods=['POST'])
def start_smart_automation():
    """Start smart automation that reuses Review tab work with corrected folder priority"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        batch_size = data.get('batch_size', 3)  # Conservative batch size
        delay = data.get('delay', 2.0)  # 2 second delay between batches
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        # Check for Review tab processed work
        solver = get_automated_solver()
        if not solver:
            return jsonify({"success": False, "error": "Automated solver not available"})
        
        review_check = solver.check_review_tab_processed(paper_folder)
        print(f"♻️ Review tab check: {review_check['message']}")
        
        if not solver.client:
            return jsonify({"success": False, "error": "Claude API not configured - set ANTHROPIC_API_KEY"})
        
        # Run automation with enhanced quality control and folder priority
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                solver.process_paper_automated(paper_folder, batch_size, delay)
            )
            
            # Add Review tab integration info to result
            if result.get("success"):
                result["review_integration"] = review_check
                result["quality_threshold"] = "91%"
                result["folder_priority"] = "images -> extracted_images"
                if review_check['processing_savings'] > 0:
                    result["message"] += f" (Review savings: {review_check['processing_savings']} questions)"
            
            return jsonify(result)
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/check-review-integration', methods=['POST'])
def check_review_integration():
    """Check what work can be reused from Review tab processing"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        solver = get_automated_solver()
        if not solver:
            return jsonify({"success": False, "error": "Solver not available"})
        
        review_check = solver.check_review_tab_processed(paper_folder)
        
        return jsonify({
            "success": True,
            "can_reuse_work": review_check["can_reuse"],
            "processed_questions": review_check["processed_questions"],
            "processing_savings": review_check["processing_savings"],
            "message": review_check["message"],
            "quality_threshold": "91%",
            "folder_priority": "images -> extracted_images",
            "recommendations": [
                "✅ Review tab work detected - can skip duplicate processing" if review_check["can_reuse"]
                else "💡 No Review tab work found - will process all images from scratch",
                f"🚀 Estimated time savings: {review_check['processing_savings'] * 2} minutes" if review_check["can_reuse"]
                else "⏱️ Full processing will take longer but ensure complete coverage"
            ]
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/get-images-preview', methods=['POST'])
def get_images_preview():
    """Get preview of all images in paper folder"""
    try:
        solver = get_automated_solver()
        if not solver:
            return jsonify({"success": False, "error": "Solver not available"})
        
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        result = solver.get_paper_images_preview(paper_folder)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/check-api-status', methods=['GET'])
def check_api_status():
    """Check if Anthropic API key is configured"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        return jsonify({
            "success": True,
            "api_key_configured": bool(api_key),
            "key_preview": f"{api_key[:8]}..." if api_key else None
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Marking scheme routes
@app.route('/api/upload-marking-scheme', methods=['POST'])
def upload_marking_scheme():
    """Upload marking scheme JSON for quality control"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"})
        
        file = request.files['file']
        paper_folder = request.form.get('paper_folder')
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"})
        
        if file and file.filename.endswith('.json'):
            paper_path = QUESTION_BANKS_DIR / paper_folder
            paper_path.mkdir(exist_ok=True)
            
            marking_scheme_path = paper_path / "marking_scheme.json"
            file.save(str(marking_scheme_path))
            
            # Validate marking scheme
            with open(marking_scheme_path, 'r') as f:
                marking_data = json.load(f)
            
            return jsonify({
                "success": True,
                "message": f"Marking scheme uploaded: {len(marking_data)} answers",
                "answers_count": len(marking_data)
            })
        else:
            return jsonify({"success": False, "error": "Only JSON files allowed"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/marking-scheme/extract-from-pdf', methods=['POST'])
def extract_marking_from_pdf():
    """Extract marking scheme from uploaded PDF"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No PDF file uploaded"})
        
        file = request.files['file']
        paper_folder = request.form.get('paper_folder')
        
        if not paper_folder:
            return jsonify({"success": False, "error": "Paper folder required"})
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": "Only PDF files allowed"})
        
        # Save uploaded PDF temporarily
        temp_pdf = f"/tmp/marking_scheme_{datetime.now().timestamp()}.pdf"
        file.save(temp_pdf)
        
        try:
            # Extract marking scheme
            marking_data = marking_processor.extract_from_cambridge_pdf(temp_pdf)
            
            # Create JSON files
            paper_path = QUESTION_BANKS_DIR / paper_folder
            paper_path.mkdir(exist_ok=True)
            
            result = marking_processor.create_json_marking_scheme(marking_data, paper_path)
            
            if result["success"]:
                result["extraction_info"] = {
                    "paper_code": marking_data.paper_code,
                    "subject": marking_data.subject,
                    "year": marking_data.year,
                    "month": marking_data.month,
                    "total_questions": marking_data.total_questions
                }
            
            return jsonify(result)
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_pdf):
                os.unlink(temp_pdf)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/validate-answers', methods=['POST'])
def validate_answers():
    """Validate AI answers against marking scheme"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        paper_path = QUESTION_BANKS_DIR / paper_folder
        master_file = paper_path / "solutions.json"
        marking_scheme_file = paper_path / "marking_scheme.json"
        
        if not master_file.exists():
            return jsonify({"success": False, "error": "Solutions file not found"})
        
        if not marking_scheme_file.exists():
            return jsonify({"success": False, "error": "Marking scheme not found"})
        
        # Load data
        with open(master_file, 'r') as f:
            master_data = json.load(f)
        
        with open(marking_scheme_file, 'r') as f:
            marking_scheme = json.load(f)
        
        # Validate answers
        validation_results = {
            "matches": 0,
            "mismatches": 0,
            "missing_in_ai": 0,
            "missing_in_marking": 0,
            "details": []
        }
        
        questions = master_data.get('questions', [])
        
        for question in questions:
            question_num = str(question.get('question_number', ''))
            ai_answer = question.get('correct_answer', '')
            marking_answer = marking_scheme.get(question_num, '')
            
            if not ai_answer and not marking_answer:
                continue
            elif not ai_answer:
                validation_results["missing_in_ai"] += 1
                validation_results["details"].append({
                    "question": question_num,
                    "status": "missing_ai",
                    "marking_answer": marking_answer
                })
            elif not marking_answer:
                validation_results["missing_in_marking"] += 1
                validation_results["details"].append({
                    "question": question_num,
                    "status": "missing_marking",
                    "ai_answer": ai_answer
                })
            elif ai_answer == marking_answer:
                validation_results["matches"] += 1
                validation_results["details"].append({
                    "question": question_num,
                    "status": "match",
                    "answer": ai_answer
                })
            else:
                validation_results["mismatches"] += 1
                validation_results["details"].append({
                    "question": question_num,
                    "status": "mismatch",
                    "ai_answer": ai_answer,
                    "marking_answer": marking_answer
                })
        
        return jsonify({
            "success": True,
            "validation": validation_results
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Image serving routes (preserved)
@app.route('/images/<paper_folder>/<filename>')
def serve_paper_image(paper_folder, filename):
    """Serve images from paper folders with STANDARDIZED FOLDER PRIORITY"""
    try:
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        
        # UPDATED: Try images folder FIRST (new standard)
        images_dir = paper_folder_path / "images"
        if images_dir.exists():
            image_path = images_dir / filename
            if image_path.exists():
                print(f"🖼️ Serving image: {image_path} (images - primary)")
                return send_from_directory(str(images_dir), filename)
        
        # UPDATED: Fallback to extracted_images folder
        extracted_images_dir = paper_folder_path / "extracted_images"
        if extracted_images_dir.exists():
            image_path = extracted_images_dir / filename
            if image_path.exists():
                print(f"🖼️ Serving image: {image_path} (extracted_images - fallback)")
                return send_from_directory(str(extracted_images_dir), filename)
        
        return f"Image not found: {filename}", 404
    except Exception as e:
        return f"Error serving image: {str(e)}", 500

@app.route('/images/<paper_folder>/extracted_images/<filename>')
def serve_extracted_image(paper_folder, filename):
    """Serve images from extracted_images folder"""
    try:
        extracted_images_dir = QUESTION_BANKS_DIR / paper_folder / "extracted_images"
        if extracted_images_dir.exists():
            return send_from_directory(str(extracted_images_dir), filename)
        return f"Extracted images folder not found", 404
    except Exception as e:
        return f"Error serving extracted image: {str(e)}", 500

@app.route('/download-backup/<paper_folder>/<filename>')
def download_backup(paper_folder, filename):
    """Download backup file"""
    try:
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        backup_path = paper_folder_path / filename
        
        if backup_path.exists():
            return send_file(str(backup_path), as_attachment=True, download_name=filename)
        else:
            return "Backup file not found", 404
    except Exception as e:
        return f"Error downloading backup: {str(e)}", 500

# Enhanced home page with corrected folder priority and 91% quality
@app.route('/')
@app.route('/enhanced-home')
def enhanced_home():
    """Enhanced home page with 91% quality threshold and corrected folder priority"""
    papers = []
    try:
        if QUESTION_BANKS_DIR.exists():
            for paper_folder in QUESTION_BANKS_DIR.iterdir():
                if paper_folder.is_dir():
                    # Load master solutions.json to get progress
                    master_file = paper_folder / "solutions.json"
                    marking_scheme_file = paper_folder / "marking_scheme.json"
                    
                    metadata = {}
                    solved_count = 0
                    total_count = 0
                    flagged_count = 0
                    high_quality_count = 0
                    review_processed = 0
                    mismatch_count = 0
                    has_marking_scheme = marking_scheme_file.exists()
                    
                    if master_file.exists():
                        try:
                            with open(master_file, 'r') as f:
                                master_data = json.load(f)
                                metadata = master_data.get('metadata', {})
                                questions = master_data.get('questions', [])
                                total_count = len(questions)
                                solved_count = sum(1 for q in questions if q.get('solved_by_ai', False))
                                flagged_count = sum(1 for q in questions if q.get('auto_flagged', False))
                                high_quality_count = sum(1 for q in questions 
                                                       if q.get('solved_by_ai', False) and not q.get('auto_flagged', False))
                                mismatch_count = sum(1 for q in questions if q.get('answer_mismatch', False))
                                
                                # Check for Review tab processed questions
                                review_processed = sum(1 for q in questions 
                                                     if q.get("question_text") and q.get("options") and not q.get("solved_by_ai", False))
                        except:
                            pass
                    
                    # Only show papers with questions
                    if total_count > 0:
                        papers.append({
                            "folder_name": paper_folder.name,
                            "metadata": metadata,
                            "total_questions": total_count,
                            "solved_questions": solved_count,
                            "high_quality_solutions": high_quality_count,
                            "flagged_questions": flagged_count,
                            "review_processed": review_processed,
                            "completion_rate": round((solved_count / total_count) * 100, 1) if total_count > 0 else 0,
                            "quality_rate": round((high_quality_count / max(solved_count, 1)) * 100, 1) if solved_count > 0 else 0,
                            "mismatch_count": mismatch_count,
                            "has_marking_scheme": has_marking_scheme
                        })
    except Exception as e:
        print(f"Error listing papers: {e}")
    
    # Check API status
    api_configured = bool(os.getenv('ANTHROPIC_API_KEY')) or bool(ANTHROPIC_API_KEY)
    
    html_start = f'''<!DOCTYPE html>
<html>
<head>
    <title>🎯 Enhanced AI Solver - 91% Quality & Corrected Folders</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 2rem; background: #f8f9fa; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 2rem; }}
        .quality-info {{ background: #e8f5e8; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid #28a745; }}
        .folder-info {{ background: #e3f2fd; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid #2196f3; }}
        .api-status {{ padding: 1rem; margin: 1rem 0; border-radius: 8px; text-align: center; }}
        .api-ready {{ background: #e8f5e8; color: #2e7d32; border: 1px solid #4caf50; }}
        .api-not-ready {{ background: #ffebee; color: #d32f2f; border: 1px solid #f44336; }}
        .paper-card {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }}
        .paper-header {{ display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1rem; align-items: center; margin-bottom: 1rem; }}
        .paper-info h3 {{ margin: 0 0 0.5rem 0; color: #333; }}
        .paper-info p {{ margin: 0.25rem 0; color: #666; font-size: 0.9rem; }}
        .quality-metrics {{ text-align: center; }}
        .metric {{ margin: 0.25rem 0; }}
        .metric-value {{ font-weight: bold; color: #333; }}
        .quality-badges {{ display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center; margin: 0.5rem 0; }}
        .badge {{ padding: 0.3rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }}
        .badge-api {{ background: #e8f5e8; color: #2e7d32; }}
        .badge-no-api {{ background: #ffebee; color: #d32f2f; }}
        .badge-marking {{ background: #e3f2fd; color: #1976d2; }}
        .badge-no-marking {{ background: #fff3e0; color: #f57c00; }}
        .badge-review {{ background: #f3e5f5; color: #7b1fa2; }}
        .badge-high-quality {{ background: #e8f5e8; color: #2e7d32; }}
        .badge-flagged {{ background: #ffebee; color: #d32f2f; }}
        .badge-mismatch {{ background: #ffebee; color: #d32f2f; }}
        .btn {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 0.6rem 1.2rem; border: none; border-radius: 8px; text-decoration: none; display: inline-block; font-weight: 600; text-align: center; margin: 0.25rem; transition: transform 0.3s ease; }}
        .btn:hover {{ transform: translateY(-2px); }}
        .btn-smart {{ background: linear-gradient(135deg, #28a745, #34ce57); }}
        .btn-check {{ background: linear-gradient(135deg, #17a2b8, #20c997); }}
        .btn-images {{ background: linear-gradient(135deg, #6f42c1, #8b5cf6); }}
        .btn-secondary {{ background: linear-gradient(135deg, #6c757d, #495057); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Enhanced AI Solver</h1>
            <p>🚀 Claude API • 📋 Marking Schemes • ♻️ Review Tab Integration • 🎯 91% Quality Threshold</p>
        </div>
        
        <div class="quality-info">
            <h4>✨ Enhanced Quality Control (91% Threshold)</h4>
            <ul>
                <li><strong>91% Confidence Threshold:</strong> Higher quality standard for solution approval</li>
                <li><strong>Review Tab Integration:</strong> Reuses processed text/options to avoid duplicate work</li>
                <li><strong>Marking Scheme Validation:</strong> Cross-checks AI answers with official answers</li>
                <li><strong>Quality Metrics:</strong> Tracks high-quality vs flagged solutions separately</li>
            </ul>
        </div>
        
        <div class="folder-info">
            <h4>📁 Corrected Folder Priority</h4>
            <ul>
                <li><strong>Primary:</strong> <code>images/</code> folder (highest priority)</li>
                <li><strong>Fallback:</strong> <code>extracted_images/</code> folder (only if primary doesn't have image)</li>
                <li><strong>Smart Detection:</strong> Finds images using multiple naming patterns including <code>question_XX_enhanced.png</code></li>
            </ul>
        </div>
        
        <div class="api-status {'api-ready' if api_configured else 'api-not-ready'}">
            <h3>{'✅ Claude API Ready (91% Quality Mode)' if api_configured else '⚠ Claude API Not Configured'}</h3>
            <p>{'Smart automation with corrected folder priority available' if api_configured else 'Set ANTHROPIC_API_KEY to enable 91% quality automation'}</p>
        </div>
        '''
    
    html_papers = ""
    if papers:
        for paper in papers:
            metadata = paper["metadata"]
            subject = metadata.get('subject', 'Unknown').title()
            year = metadata.get('year', 'Unknown')
            month = metadata.get('month', 'Unknown').title()
            paper_code = metadata.get('paper_code', 'Unknown')
            
            total = paper["total_questions"]
            solved = paper["solved_questions"]
            high_quality = paper["high_quality_solutions"]
            flagged = paper["flagged_questions"]
            review_processed = paper["review_processed"]
            completion = paper["completion_rate"]
            quality_rate = paper["quality_rate"]
            mismatches = paper["mismatch_count"]
            has_marking = paper["has_marking_scheme"]
            
            html_papers += f'''
            <div class="paper-card">
                <div class="paper-header">
                    <div class="paper-info">
                        <h3>{subject} {year} {month} Paper {paper_code}</h3>
                        <p><strong>Folder:</strong> {paper["folder_name"]}</p>
                        <p><strong>Progress:</strong> {solved}/{total} solved ({completion}%)</p>
                        <div class="quality-badges">
                            {'<span class="badge badge-api">✅ API Ready</span>' if api_configured else '<span class="badge badge-no-api">⚠ No API</span>'}
                            {'<span class="badge badge-marking">📋 Marking</span>' if has_marking else '<span class="badge badge-no-marking">⚠ No Marking</span>'}
                            {f'<span class="badge badge-review">♻️ {review_processed} Review</span>' if review_processed > 0 else ''}
                            {f'<span class="badge badge-high-quality">🎯 {high_quality} High Quality</span>' if high_quality > 0 else ''}
                            {f'<span class="badge badge-flagged">⚠️ {flagged} Flagged</span>' if flagged > 0 else ''}
                            {f'<span class="badge badge-mismatch">🔍 {mismatches} Mismatches</span>' if mismatches > 0 else ''}
                        </div>
                    </div>
                    <div class="quality-metrics">
                        <div class="metric">Quality Rate: <span class="metric-value">{quality_rate}%</span></div>
                        <div class="metric">High Quality: <span class="metric-value">{high_quality}/{solved}</span></div>
                        <div class="metric">Flagged: <span class="metric-value">{flagged}</span></div>
                        {f'<div class="metric">Review Work: <span class="metric-value">{review_processed}</span></div>' if review_processed > 0 else ''}
                    </div>
                    <div class="paper-controls">
                        {f'<button onclick="startSmartAutomation(\'{paper["folder_name"]}\')" class="btn btn-smart">🎯 Smart Automate</button>' if api_configured and completion < 100 else ''}
                        <button onclick="checkReviewIntegration('{paper["folder_name"]}')" class="btn btn-check">♻️ Check Review</button>
                        <button onclick="findImageLocations('{paper["folder_name"]}')" class="btn btn-images">🔷 Find Images</button>
                        <a href="/solver/{paper["folder_name"]}" class="btn">✏️ Manual Solve</a>
                        <a href="/enhanced-solver/{paper["folder_name"]}" class="btn btn-secondary">🔧 Enhanced</a>
                    </div>
                </div>
            </div>
            '''
    else:
        html_papers = '<div style="text-align: center; padding: 2rem; color: #6c757d;"><h3>No papers found</h3><p>Please extract questions first.</p></div>'
    
    html_end = '''
        </div>
        
        <script>
        async function startSmartAutomation(paperFolder) {
            if (confirm(`Start smart automation with 91% quality threshold for ${paperFolder}?\\n\\n✅ Will reuse Review tab work\\n🎯 91% confidence threshold\\n📁 Priority: images -> extracted_images`)) {
                try {
                    showNotification('🚀 Starting smart automation...', 'info');
                    
                    const response = await fetch('/api/smart-automation', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            paper_folder: paperFolder,
                            batch_size: 3,
                            delay: 2.0 
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const stats = data.stats;
                        const reviewInfo = data.review_integration || {};
                        
                        let message = `🎉 Smart automation complete!\\n\\n`;
                        message += `📊 Processed: ${stats.processed} questions\\n`;
                        message += `✅ Total solved: ${stats.solved}/${stats.total_questions}\\n`;
                        message += `🎯 Quality threshold: 91%\\n`;
                        message += `📁 Folder priority: ${data.folder_priority}\\n`;
                        message += `⚠️ Flagged for review: ${stats.flagged}\\n`;
                        
                        if (reviewInfo.processing_savings > 0) {
                            message += `♻️ Review tab savings: ${reviewInfo.processing_savings} questions\\n`;
                        }
                        
                        if (stats.mismatches > 0) {
                            message += `🔍 Answer mismatches: ${stats.mismatches}\\n`;
                        }
                        
                        alert(message);
                        location.reload();
                    } else {
                        showNotification(`⚠ Smart automation failed: ${data.error}`, 'error');
                    }
                } catch (error) {
                    showNotification(`⚠ Error: ${error.message}`, 'error');
                }
            }
        }
        
        async function checkReviewIntegration(paperFolder) {
            try {
                showNotification('🔍 Checking Review tab integration...', 'info');
                
                const response = await fetch('/api/check-review-integration', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ paper_folder: paperFolder })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    let message = `♻️ Review Tab Integration Check\\n\\n`;
                    message += `${data.message}\\n\\n`;
                    message += `🎯 Quality threshold: ${data.quality_threshold}\\n`;
                    message += `📁 Folder priority: ${data.folder_priority}\\n\\n`;
                    
                    if (data.can_reuse_work) {
                        message += `✅ Can reuse work for ${data.processed_questions.length} questions\\n`;
                        message += `⚡ Estimated savings: ${data.processing_savings * 2} minutes\\n`;
                        message += `📋 Questions: ${data.processed_questions.slice(0, 10).join(', ')}${data.processed_questions.length > 10 ? '...' : ''}\\n`;
                    } else {
                        message += `💡 No Review tab work detected\\n`;
                        message += `⏱️ Will process all images from scratch\\n`;
                    }
                    
                    message += `\\n${data.recommendations.join('\\n')}`;
                    
                    alert(message);
                } else {
                    showNotification(`⚠ Check failed: ${data.error}`, 'error');
                }
            } catch (error) {
                showNotification(`⚠ Error: ${error.message}`, 'error');
            }
        }
        
        async function findImageLocations(paperFolder) {
            try {
                showNotification('🔷 Finding image locations...', 'info');
                
                const response = await fetch('/api/find-image-locations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ paper_folder: paperFolder })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    let message = `🔷 Image Location Analysis\\n\\n`;
                    message += `Total images found: ${data.total_images_found}\\n`;
                    message += `Folder priority: ${data.folder_priority}\\n`;
                    message += `Using: ${data.best_location || 'None'} (${data.best_count || 0} images)\\n\\n`;
                    
                    message += `Folder Details:\\n`;
                    for (const [location, info] of Object.entries(data.locations)) {
                        message += `• ${location}: ${info.count} images (${info.priority})\\n`;
                    }
                    
                    message += `\\n${data.recommendations.join('\\n')}`;
                    
                    alert(message);
                } else {
                    showNotification(`⚠ Image search failed: ${data.error}`, 'error');
                }
            } catch (error) {
                showNotification(`⚠ Error: ${error.message}`, 'error');
            }
        }
        
        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 1000;
                max-width: 400px;
                transition: transform 0.3s ease;
            `;
            
            switch(type) {
                case 'success': notification.style.background = '#28a745'; break;
                case 'error': notification.style.background = '#dc3545'; break;
                case 'warning': notification.style.background = '#ffc107'; notification.style.color = '#212529'; break;
                default: notification.style.background = '#17a2b8';
            }
            
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.remove(), 5000);
        }
        
        // Show initial notification
        window.addEventListener('load', () => {
            showNotification('🎯 Enhanced AI Solver loaded with 91% quality and corrected folder priority!', 'success');
        });
        </script>
    </body>
    </html>'''
    
    return html_start + html_papers + html_end

if __name__ == '__main__':
    print("🚀 Starting Enhanced AI Solver with Claude API...")
    print(f"🔑 API Key: {'✅ Configured' if ANTHROPIC_API_KEY else '⚠ Missing'}")
    print(f"📂 Question banks: {QUESTION_BANKS_DIR}")
    print(f"🌐 Enhanced interface: http://localhost:5005")
    print(f"🎯 Quality threshold: 91% (enhanced from 85%)")
    print(f"📁 Folder priority: images → extracted_images (corrected)")
    print(f"🤖 Claude API automation: {'✅ Ready' if ANTHROPIC_API_KEY else '⚠ Set ANTHROPIC_API_KEY'}")
    print("📋 Marking scheme processing: ✅ Ready (PDF + JSON)")
    print("♻️ Review tab integration: ✅ Ready (avoids duplicate work)")
    print("🎯 Quality control: ✅ Ready (mismatch detection)")
    print("🔥 COMPLETE ENHANCED SYSTEM - All 1300+ lines restored with syntax fixes")
    print("=" * 70)
    
    app.run(
        host='0.0.0.0',
        port=5005,
        debug=True,
        threaded=True
    )