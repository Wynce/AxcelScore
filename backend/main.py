#!/usr/bin/env python3
"""
Complete main.py - AI Tutor Interface with Enhanced AI Solver Integration
Upload • Extract • Review • Solve workflow - COMPLETE VERSION WITH STANDARDIZED FOLDER STRUCTURE
"""

from flask import Flask, request, jsonify, send_from_directory, render_template_string, send_file, abort, make_response
from flask_cors import CORS
from PIL import Image
import os
import tempfile
from pathlib import Path
import json
from datetime import datetime
import shutil
import re
import io
import subprocess
import sys
import threading
import time
import signal
import atexit
import traceback
import hashlib

# Import the review module
from review import ReviewManager, create_review_html_tab, get_review_css

app = Flask(__name__)
CORS(app)

# Configuration - Proper separation for frontend integration
BASE_DIR = Path("/Users/wynceaxcel/Apps/axcelscore/backend")
TUTOR_APP_ROOT = Path("/Users/wynceaxcel/Apps/axcelscore")
UPLOAD_FOLDER = BASE_DIR / "uploads"
QUESTION_BANKS_DIR = TUTOR_APP_ROOT / "question_banks"  # Shared with frontend
UPLOAD_FOLDER.mkdir(exist_ok=True)
QUESTION_BANKS_DIR.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Initialize Review Manager
review_manager = ReviewManager(QUESTION_BANKS_DIR)

# Global variables to track current file and metadata
CURRENT_FILE_PATH = None
CURRENT_EXAM_METADATA = {}
CURRENT_PAPER_FOLDER = None

# Module management
class ModuleManager:
    """Manages extractor.py as subprocess module"""
    
    def __init__(self):
        self.processes = {}
        self.module_status = {
            'extractor': {'available': False, 'path': None}
        }
        self.check_modules()
        
    def check_modules(self):
        """Check if required modules exist in backend directory"""
        # Check for extractor.py in backend
        extractor_paths = [
        BASE_DIR / "extractor.py",
        Path.cwd() / "extractor.py",
        TUTOR_APP_ROOT / "extractor.py",  # ADD THIS LINE
        Path("/Users/wynceaxcel/Apps/axcelscore/extractor.py")  # ADD THIS LINE
        ]
        
        for path in extractor_paths:
            if path.exists():
                self.module_status['extractor']['available'] = True
                self.module_status['extractor']['path'] = path
                break
                
        print(f"🔧 Extractor available: {'✅ Yes' if self.module_status['extractor']['available'] else '❌ No'}")
    
    def run_extractor(self, pdf_path, exam_metadata):
        """
        UPDATED VERSION - Run extractor.py directly with STANDARDIZED FOLDER STRUCTURE
        Uses images/ as primary, extracted_images/ as fallback
        """
        if not self.module_status['extractor']['available']:
            raise Exception("Extractor module not found")
        
        try:
            # Create paper-specific folder
            subject = exam_metadata.get('subject', 'physics').lower()
            year = exam_metadata.get('year', 2024)
            month = exam_metadata.get('month', 'Mar').lower()
            paper_code = exam_metadata.get('paper_code', '13')
            
            paper_folder_name = f"{subject}_{year}_{month}_{paper_code}"
            paper_folder_path = QUESTION_BANKS_DIR / paper_folder_name
            paper_folder_path.mkdir(parents=True, exist_ok=True)
            
            print(f"DEBUG: Paper folder: {paper_folder_path}")
            
            # UPDATED: Add extractor path to Python path for direct import
            extractor_parent = self.module_status['extractor']['path'].parent
            if str(extractor_parent) not in sys.path:
                sys.path.insert(0, str(extractor_parent))
            
            # UPDATED: Import the correct class name
            print("DEBUG: Importing EnhancedPDFExtractor...")
            try:
                # Clear any cached imports to ensure fresh import
                if 'extractor' in sys.modules:
                    del sys.modules['extractor']
                
                from extractor import EnhancedPDFExtractor
                print("DEBUG: EnhancedPDFExtractor imported successfully")
            except ImportError as e:
                error_msg = f"Failed to import EnhancedPDFExtractor: {e}"
                print(f"ERROR: {error_msg}")
                return {"success": False, "error": error_msg}
            
            # Copy PDF to paper folder
            pdf_dest = paper_folder_path / "exam.pdf"
            print(f"DEBUG: Copying PDF from {pdf_path} to {pdf_dest}")
            shutil.copy2(pdf_path, pdf_dest)
            
            # UPDATED: Initialize extractor with correct base_dir parameter
            print("DEBUG: Initializing EnhancedPDFExtractor...")
            extractor = EnhancedPDFExtractor(base_dir=str(paper_folder_path))
            print("DEBUG: EnhancedPDFExtractor initialized successfully")
            
            # UPDATED: Run extraction using the correct method name
            print("DEBUG: Starting extraction using extract_questions_for_web_interface...")
            result = extractor.extract_questions_for_web_interface(
                pdf_filename="exam.pdf",
                subject=subject,
                year=str(year),
                month=month,
                paper_code=paper_code
            )
            
            print(f"DEBUG: Extraction completed with result: {result}")
            print(f"DEBUG: Result type: {type(result)}")
            print(f"DEBUG: Result is None: {result is None}")
            
            # UPDATED: Proper result validation
            if result and isinstance(result, dict) and result.get('success'):
                print(f"DEBUG: Valid result received with keys: {list(result.keys())}")
                
                # UPDATED: Count extracted images with standardized folder priority
                image_files = []
                
                # UPDATED: Check images folder FIRST (new standard)
                images_folder = paper_folder_path / "images"
                if images_folder.exists():
                    image_files.extend(list(images_folder.glob("question_*_enhanced.png")))
                    print(f"DEBUG: Found {len(image_files)} images in images folder (primary)")
                
                # UPDATED: Check extracted_images folder as FALLBACK only if no images found
                if not image_files:
                    extracted_images_folder = paper_folder_path / "extracted_images"
                    if extracted_images_folder.exists():
                        image_files.extend(list(extracted_images_folder.glob("question_*_enhanced.png")))
                        print(f"DEBUG: Found {len(image_files)} images in extracted_images folder (fallback)")
                
                question_count = len(image_files)
                
                print(f"SUCCESS: {question_count} questions extracted to {paper_folder_name}")
                print(f"FOLDER: {paper_folder_path}")
                
                if image_files:
                    sample_images = [img.name for img in image_files[:3]]
                    print(f"IMAGES: {sample_images}")
                
                # UPDATED: Return the correct images folder path
                active_images_folder = images_folder if images_folder.exists() else (extracted_images_folder if extracted_images_folder.exists() else images_folder)
                
                return {
                    "success": True,
                    "questions_found": question_count,
                    "paper_folder": str(paper_folder_path),
                    "paper_folder_name": paper_folder_name,
                    "images_folder": str(active_images_folder),
                    "extraction_result": result  # Include original result for debugging
                }
            else:
                error_msg = f"Extractor returned invalid result: {result} (type: {type(result)})"
                print(f"ERROR: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except ImportError as e:
            error_msg = f"Failed to import extractor: {str(e)}"
            print(f"ERROR: {error_msg}")
            return {"success": False, "error": error_msg}
        except AttributeError as e:
            error_msg = f"Extractor method not found: {str(e)}"
            print(f"ERROR: {error_msg}")
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Extraction error: {str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": error_msg}

# Initialize module manager
module_manager = ModuleManager()

# Register blueprints
app.register_blueprint(review_manager.create_blueprint())

# SIMPLE AI SOLVER MANAGER - DIRECT INTEGRATION (NO SEPARATE FILE NEEDED)
class SimpleAISolverManager:
    """Simple AI Solver Manager - returns JSON responses"""
    
    def __init__(self):
        self.current_paper_folder = None
    
    def initialize_solver(self, paper_folder_path):
        """Initialize AI Solver and return JSON response - UPDATED FOLDER PRIORITY"""
        try:
            paper_path = Path(paper_folder_path)
            if not paper_path.exists():
                return {
                    "success": False,
                    "error": f"Paper folder not found: {paper_folder_path}"
                }
            
            # UPDATED: Check with standardized folder priority (images first, extracted_images fallback)
            images_folder = paper_path / "images"
            extracted_images_folder = paper_path / "extracted_images"
            
            image_files = []
            images_dir = None
            
            # UPDATED: Check images folder FIRST (primary)
            if images_folder.exists():
                image_files = list(images_folder.glob("question_*_enhanced.png"))
                images_dir = images_folder
                print(f"📁 Found images in: {images_folder}")
            # UPDATED: Check extracted_images folder as FALLBACK
            elif extracted_images_folder.exists():
                image_files = list(extracted_images_folder.glob("question_*_enhanced.png"))
                images_dir = extracted_images_folder
                print(f"📁 Found images in: {extracted_images_folder}")
            else:
                return {
                    "success": False,
                    "error": "No images folder found. Please extract questions first."
                }
            
            if len(image_files) == 0:
                return {
                    "success": False,
                    "error": "No question images found. Please extract questions first."
                }
            
            # Read metadata if available
            metadata_file = paper_path / "metadata.json"
            metadata = {}
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            # Sort images by question number
            def extract_question_number(filename):
                match = re.search(r'question_(\d+)_enhanced\.png', filename.name)
                return int(match.group(1)) if match else 0
            
            image_files.sort(key=extract_question_number)
            
            # Generate AI solver interface HTML
            interface_html = self.generate_simple_solver_interface(image_files, paper_path.name, metadata)
            interface_path = paper_path / "ai_solver_interface.html"
            
            with open(interface_path, 'w', encoding='utf-8') as f:
                f.write(interface_html)
            
            print(f"✅ AI Solver initialized for {paper_path.name}")
            print(f"   Found {len(image_files)} questions")
            print(f"   Interface saved: {interface_path}")
            
            return {
                "success": True,
                "data": {
                    "total_questions": len(image_files),
                    "paper_folder": paper_path.name,
                    "interface_path": str(interface_path),
                    "subject": metadata.get('subject', 'Unknown'),
                    "year": metadata.get('year', 'Unknown'),
                    "month": metadata.get('month', 'Unknown'),
                    "paper_code": metadata.get('paper_code', 'Unknown')
                }
            }
            
        except Exception as e:
            print(f"❌ AI Solver error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"AI Solver initialization failed: {str(e)}"
            }
    
    def generate_simple_solver_interface(self, image_files, paper_name, metadata):
        """Generate simple AI solver interface"""
        
        # Create question cards
        question_cards = []
        for i, img_file in enumerate(image_files, 1):
            # Use Flask route for images
            img_url = f"/images/{paper_name}/{img_file.name}"
            
            card_html = f'''
            <div class="question-card" id="question-{i}">
                <h3>Question {i}</h3>
                <img src="{img_url}" alt="Question {i}" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; cursor: pointer;" onclick="openFullSize('{img_url}')">
                <div style="margin-top: 1rem;">
                    <button onclick="getPrompt({i})" style="background: #007bff; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; margin: 0.25rem; cursor: pointer;">
                        📋 Get Prompt
                    </button>
                    <button onclick="window.open('{img_url}', '_blank')" style="background: #6c757d; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; margin: 0.25rem; cursor: pointer;">
                        🔍 Open Image
                    </button>
                </div>
                <div style="margin-top: 1rem;">
                    <label style="font-weight: 600;">AI Response (JSON):</label>
                    <textarea id="solution-{i}" style="width: 100%; height: 120px; margin-top: 0.5rem; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; font-size: 12px;" placeholder="Paste JSON response from Claude.ai here..." onchange="validateSolution({i})"></textarea>
                    <div style="margin-top: 0.5rem;">
                        <button onclick="saveSolution({i})" style="background: #28a745; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; margin-right: 0.5rem; cursor: pointer;">
                            ✅ Save
                        </button>
                        <button onclick="clearSolution({i})" style="background: #dc3545; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer;">
                            🗑️ Clear
                        </button>
                    </div>
                </div>
                <div id="solution-display-{i}" style="display: none; margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 4px;"></div>
            </div>
            '''
            question_cards.append(card_html)
        
        # Simple HTML interface with all functionality
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 AI Solver - {paper_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 2rem; text-align: center; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; padding: 2rem; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }}
        .stat-card {{ background: white; padding: 1.5rem; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .controls {{ text-align: center; margin: 2rem 0; padding: 0 2rem; }}
        .questions-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 2rem; padding: 2rem; }}
        .question-card {{ background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #dee2e6; }}
        .btn {{ padding: 0.75rem 1.5rem; margin: 0.5rem; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.3s; }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-secondary {{ background: #6c757d; color: white; }}
        .btn-enhanced {{ background: #8b5cf6; color: white; }}
        .btn:hover {{ transform: translateY(-2px); }}
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: 5% auto; display: block; max-width: 90%; max-height: 80%; }}
        .close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
        .close:hover {{ color: #bbb; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Solver Interface</h1>
            <p>{metadata.get('subject', 'Physics')} {metadata.get('year', '2024')} {metadata.get('month', 'Mar')} Paper {metadata.get('paper_code', '13')}</p>
            <p>📊 {len(image_files)} Questions Found</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3 id="total-questions">{len(image_files)}</h3>
                <p>Total Questions</p>
            </div>
            <div class="stat-card">
                <h3 id="solved-count">0</h3>
                <p>Solved</p>
            </div>
            <div class="stat-card">
                <h3 id="flagged-count">0</h3>
                <p>Flagged (&lt;85%)</p>
            </div>
            <div class="stat-card">
                <h3 id="avg-confidence">0%</h3>
                <p>Avg Confidence</p>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-enhanced" onclick="getAllPrompts()">📋 Get All Prompts</button>
            <button class="btn btn-success" onclick="exportResults()">💾 Export Results</button>
            <button class="btn btn-primary" onclick="window.open('https://claude.ai', '_blank')">🌐 Open Claude.ai</button>
            <button class="btn btn-secondary" onclick="showInstructions()">❓ Instructions</button>
        </div>
        
        <div class="questions-grid">
            {''.join(question_cards)}
        </div>
    </div>
    
    <!-- Image Modal -->
    <div id="imageModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>
    
    <script>
        const PROMPT = `Analyze this Cambridge IGCSE Physics question and provide a complete solution in JSON format.

Return ONLY valid JSON in this exact structure:
{{
  "correct_answer": "A/B/C/D or calculated value",
  "simple_answer": "Brief clear explanation",
  "calculation_steps": ["Step 1: Identify given values", "Step 2: Apply formula", "Step 3: Calculate result"],
  "detailed_explanation": {{
    "why_correct": "Detailed explanation of the correct approach and physics concepts",
    "why_others_wrong": {{"A": "Why option A is incorrect", "B": "Why option B is incorrect"}}
  }},
  "topic": "Physics topic (e.g., Motion and Forces)",
  "difficulty": "easy/medium/hard",
  "confidence_score": 0.95
}}

Important:
- Be precise with calculations and units
- Explain physics concepts clearly
- For MCQ, explain why each wrong option is incorrect
- Confidence score should be between 0.0 and 1.0`;

        let solutions = {{}};
        let stats = {{ total: {len(image_files)}, solved: 0, flagged: 0 }};
        
        function getPrompt(questionNumber) {{
            navigator.clipboard.writeText(PROMPT).then(() => {{
                alert(`📋 Prompt copied for Question ${{questionNumber}}!\\n\\n1. Open Claude.ai in another tab\\n2. Upload the question image\\n3. Paste this prompt\\n4. Copy the JSON response back here`);
            }}).catch(() => {{
                alert(`Prompt for Question ${{questionNumber}}:\\n\\n${{PROMPT}}`);
            }});
        }}
        
        function getAllPrompts() {{
            let allPrompts = "";
            for(let i = 1; i <= stats.total; i++) {{
                allPrompts += `=== QUESTION ${{i}} ===\\n${{PROMPT}}\\n\\n`;
            }}
            navigator.clipboard.writeText(allPrompts).then(() => {{
                alert(`📋 All {len(image_files)} prompts copied to clipboard!\\n\\nEach prompt is labeled with question number.`);
            }}).catch(() => {{
                console.error('Clipboard failed');
                // Fallback: show in new window
                const newWindow = window.open('', '_blank');
                newWindow.document.write(`<pre>${{allPrompts}}</pre>`);
            }});
        }}
        
        function validateSolution(questionNumber) {{
            const textarea = document.getElementById(`solution-${{questionNumber}}`);
            const solution = textarea.value.trim();
            
            if (!solution) {{
                textarea.style.borderColor = '#ddd';
                return;
            }}
            
            try {{
                const parsed = JSON.parse(solution);
                textarea.style.borderColor = '#28a745';
                return parsed;
            }} catch(error) {{
                textarea.style.borderColor = '#dc3545';
                return null;
            }}
        }}
        
        function saveSolution(questionNumber) {{
            const textarea = document.getElementById(`solution-${{questionNumber}}`);
            const solution = textarea.value.trim();
            
            if(!solution) {{
                alert('❌ No solution to save');
                return;
            }}
            
            try {{
                const parsed = JSON.parse(solution);
                
                // Validate required fields
                const required = ['correct_answer', 'simple_answer', 'confidence_score'];
                const missing = required.filter(field => !(field in parsed));
                if (missing.length > 0) {{
                    throw new Error(`Missing required fields: ${{missing.join(', ')}}`);
                }}
                
                const confidence = parseFloat(parsed.confidence_score);
                if (isNaN(confidence) || confidence < 0 || confidence > 1) {{
                    throw new Error('Confidence score must be between 0 and 1');
                }}
                
                solutions[questionNumber] = parsed;
                displaySolution(questionNumber, parsed);
                updateStats();
                alert(`✅ Solution saved for Question ${{questionNumber}}`);
                
            }} catch(error) {{
                alert(`❌ Invalid JSON: ${{error.message}}`);
            }}
        }}
        
        function displaySolution(questionNumber, solution) {{
            const displayDiv = document.getElementById(`solution-display-${{questionNumber}}`);
            const confidence = parseFloat(solution.confidence_score);
            const confidencePercent = Math.round(confidence * 100);
            
            displayDiv.innerHTML = `
                <h5>✅ Solution Summary</h5>
                <p><strong>Answer:</strong> ${{solution.correct_answer}}</p>
                <p><strong>Explanation:</strong> ${{solution.simple_answer}}</p>
                <p><strong>Topic:</strong> ${{solution.topic || 'Not specified'}}</p>
                <p><strong>Confidence:</strong> ${{confidencePercent}}% ${{confidence < 0.85 ? '⚠️ FLAGGED' : '✅'}}</p>
            `;
            displayDiv.style.display = 'block';
        }}
        
        function clearSolution(questionNumber) {{
            if(confirm(`Clear solution for Question ${{questionNumber}}?`)) {{
                document.getElementById(`solution-${{questionNumber}}`).value = '';
                document.getElementById(`solution-display-${{questionNumber}}`).style.display = 'none';
                delete solutions[questionNumber];
                updateStats();
            }}
        }}
        
        function updateStats() {{
            const solved = Object.keys(solutions).length;
            const flagged = Object.values(solutions).filter(s => s.confidence_score < 0.85).length;
            const totalConfidence = Object.values(solutions).reduce((sum, s) => sum + s.confidence_score, 0);
            const avgConfidence = solved > 0 ? Math.round((totalConfidence / solved) * 100) : 0;
            
            document.getElementById('solved-count').textContent = solved;
            document.getElementById('flagged-count').textContent = flagged;
            document.getElementById('avg-confidence').textContent = avgConfidence + '%';
        }}
        
        function exportResults() {{
            if(Object.keys(solutions).length === 0) {{
                alert('❌ No solutions to export');
                return;
            }}
            
            const exportData = {{
                paper_name: "{paper_name}",
                metadata: {json.dumps(metadata)},
                solutions: solutions,
                statistics: {{
                    completion_rate: Math.round((Object.keys(solutions).length / stats.total) * 100),
                    average_confidence: Object.keys(solutions).length > 0 ? 
                        Math.round((Object.values(solutions).reduce((sum, s) => sum + s.confidence_score, 0) / Object.keys(solutions).length) * 100) : 0,
                    flagged_count: Object.values(solutions).filter(s => s.confidence_score < 0.85).length
                }},
                export_timestamp: new Date().toISOString()
            }};
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `{paper_name}_solutions_${{new Date().toISOString().slice(0, 19).replace(/:/g, '-')}}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            alert(`📥 Exported ${{Object.keys(solutions).length}} solutions to JSON file`);
        }}
        
        function openFullSize(imageSrc) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            modal.style.display = 'block';
            modalImg.src = imageSrc;
        }}
        
        function closeModal() {{
            document.getElementById('imageModal').style.display = 'none';
        }}
        
        function showInstructions() {{
            alert(`🤖 AI Solver Instructions:

1. 📋 GET PROMPTS:
   • Click "Get Prompt" for individual questions
   • Or "Get All Prompts" for batch processing

2. 🌐 USE CLAUDE.AI:
   • Open Claude.ai in another tab
   • Upload the question image
   • Paste the copied prompt
   • Copy the JSON response

3. 💾 SAVE SOLUTIONS:
   • Paste JSON response in the textarea
   • Click "Save" to validate and store
   • Solutions auto-flagged if confidence < 85%

4. 📥 EXPORT:
   • Click "Export Results" for JSON file
   • Contains all solutions + statistics

Tips:
• Keep this tab open while working with Claude.ai
• Process questions in batches for efficiency
• Review flagged solutions carefully`);
        }}
        
        // Close modal on outside click
        window.onclick = function(event) {{
            const modal = document.getElementById('imageModal');
            if (event.target === modal) {{
                closeModal();
            }}
        }}
        
        console.log('🤖 AI Solver Interface ready with {len(image_files)} questions');
    </script>
</body>
</html>
        '''
        return html_content

# Initialize AI Solver Manager
ai_solver_manager = SimpleAISolverManager()

# FIXED AI SOLVER ROUTES - RETURN JSON (REPLACING BLUEPRINT)
@app.route('/api/ai-solver/initialize', methods=['POST'])
def initialize_ai_solver():
    """Initialize AI Solver - RETURNS JSON"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        if not paper_folder:
            return jsonify({
                "success": False,
                "error": "No paper folder specified"
            }), 400
        
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        
        if not paper_folder_path.exists():
            return jsonify({
                "success": False,
                "error": f"Paper folder not found: {paper_folder}"
            }), 404
        
        # Initialize solver and get JSON response
        result = ai_solver_manager.initialize_solver(str(paper_folder_path))
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        print(f"❌ AI Solver initialization error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/ai-solver/<paper_folder>')
def serve_ai_solver_interface(paper_folder):
    """Serve the AI solver interface HTML"""
    try:
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        interface_path = paper_folder_path / "ai_solver_interface.html"
        
        if not interface_path.exists():
            # Generate interface if it doesn't exist
            result = ai_solver_manager.initialize_solver(str(paper_folder_path))
            if not result["success"]:
                return f"Failed to generate AI solver interface: {result['error']}", 500
        
        # Serve the HTML file
        with open(interface_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return html_content
        
    except Exception as e:
        print(f"❌ Error serving AI solver interface: {e}")
        return f"Error serving AI solver interface: {str(e)}", 500

def create_cache_busted_response(image_path):
    """Create a response with aggressive cache-busting headers"""
    try:
        response = make_response(send_file(str(image_path)))
        
        # Generate strong ETag based on file modification time and size
        stat = image_path.stat()
        etag_data = f"{stat.st_mtime}-{stat.st_size}"
        etag = hashlib.md5(etag_data.encode()).hexdigest()
        
        # Aggressive cache-busting headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['ETag'] = etag
        response.headers['Last-Modified'] = datetime.fromtimestamp(stat.st_mtime).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Add custom header for debugging
        response.headers['X-Image-Cache-Bust'] = str(int(time.time() * 1000))
        
        return response
        
    except Exception as e:
        print(f"❌ Error creating cache-busted response: {e}")
        abort(500)

# Enhanced HTML template with Upload, Extract, Review, Solve workflow - CORRECT ORDER
HTML_TEMPLATE = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI Tutor - Upload, Extract, Review & Solve</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            width: 100%;
            max-width: 1400px;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
        }}
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        .nav-tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        .nav-tab {{
            flex: 1;
            padding: 1rem;
            text-align: center;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            font-size: 14px;
        }}
        .nav-tab.active {{
            background: white;
            color: #4facfe;
            border-bottom: 3px solid #4facfe;
        }}
        .nav-tab:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .tab-content {{ 
            padding: 2rem; 
            flex: 1;
            overflow-y: auto;
            min-height: 400px;
        }}
        .tab-pane {{ display: none; }}
        .tab-pane.active {{ display: block; }}
        .upload-area {{
            border: 3px dashed #4facfe;
            border-radius: 15px;
            padding: 3rem;
            text-align: center;
            margin-bottom: 2rem;
            cursor: pointer;
            transition: all 0.3s;
            background: #f8f9ff;
        }}
        .upload-area:hover {{ background: #e6f3ff; border-color: #2196F3; }}
        .upload-area.success {{
            border-color: #28a745;
            background: #f0fff0;
        }}
        .btn {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            margin: 0.5rem;
            text-decoration: none;
            display: inline-block;
        }}
        .btn:hover {{ transform: translateY(-2px); }}
        .btn:disabled {{ opacity: 0.6; cursor: not-allowed; transform: none; }}
        .btn.success {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); }}
        .btn.danger {{ background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%); }}
        .btn.secondary {{ background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); }}
        .btn.enhanced {{ background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%); }}
        .alert {{
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-weight: 500;
        }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .alert-info {{ background: #cce7ff; color: #0c5460; border: 1px solid #bee5eb; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .progress {{
            width: 100%;
            height: 24px;
            background: #e9ecef;
            border-radius: 12px;
            overflow: hidden;
            margin: 1rem 0;
        }}
        .progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, #4facfe, #00f2fe);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }}
        .hidden {{ display: none !important; }}
        .spinner {{
            width: 20px;
            height: 20px;
            border: 2px solid #ffffff;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .file-info {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }}
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        .result-card {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
        }}
        .question-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        .question-card {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        .question-card img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            margin-bottom: 1rem;
        }}
        .question-actions {{
            display: flex;
            gap: 0.5rem;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .btn-small {{
            padding: 0.5rem 1rem;
            font-size: 12px;
        }}
        .status-ready {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-pending {{
            color: #ffc107;
            font-weight: bold;
        }}
        .status-error {{
            color: #dc3545;
            font-weight: bold;
        }}
        .solve-features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }}
        .feature-card {{
            background: linear-gradient(135deg, #f8f9ff 0%, #e6f3ff 100%);
            border: 1px solid #4facfe;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
        }}
        .feature-icon {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
        .solver-controls {{
            display: flex;
            gap: 1rem;
            margin: 2rem 0;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        /* Review Tab Specific Styles */
        {get_review_css()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Tutor - Complete Workflow</h1>
            <p>Upload, Extract, Review & Solve exam papers with AI-powered processing</p>
        </div>

        <div class="nav-tabs">
            <button id="upload-tab-btn" class="nav-tab active" onclick="showTab('upload')">📤 Upload</button>
            <button id="extract-tab-btn" class="nav-tab" onclick="showTab('extract')" disabled>⚙️ Extract</button>
            <button id="review-tab-btn" class="nav-tab" onclick="showTab('review')" disabled>🔍 Review</button>
            <button id="solve-tab-btn" class="nav-tab" onclick="showTab('solve')" disabled>🤖 Solve</button>
        </div>

        <div class="tab-content">
            <!-- Upload Tab -->
            <div class="tab-pane active" id="upload-tab">
                <h2>📤 Upload Exam PDF</h2>
                <p style="margin-bottom: 2rem; color: #6c757d;">Upload a Cambridge IGCSE exam paper PDF for AI-powered processing</p>

                <!-- Exam Information Form -->
                <div class="file-info" style="display: block;">
                    <h4>📋 Exam Information</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Exam Type:</label>
                            <select id="examType" style="width: 100%; padding: 0.5rem; border: 1px solid #dee2e6; border-radius: 4px;">
                                <option value="Cambridge">Cambridge</option>
                                <option value="Edexcel">Edexcel</option>
                                <option value="AQA">AQA</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Subject:</label>
                            <select id="subject" style="width: 100%; padding: 0.5rem; border: 1px solid #dee2e6; border-radius: 4px;">
                                <option value="physics">Physics</option>
                                <option value="chemistry">Chemistry</option>
                                <option value="biology">Biology</option>
                                <option value="mathematics">Mathematics</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Year:</label>
                            <select id="year" style="width: 100%; padding: 0.5rem; border: 1px solid #dee2e6; border-radius: 4px;">
                                <option value="2025">2025</option>
                                <option value="2024">2024</option>
                                <option value="2023">2023</option>
                                <option value="2022">2022</option>
                                <option value="2021">2021</option>
                            </select>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Month:</label>
                            <select id="month" style="width: 100%; padding: 0.5rem; border: 1px solid #dee2e6; border-radius: 4px;">
                                <option value="Mar">March</option>
                                <option value="May">May</option>
                                <option value="Oct">October</option>
                            </select>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Paper Type:</label>
                            <select id="paperType" style="width: 100%; padding: 0.5rem; border: 1px solid #dee2e6; border-radius: 4px;">
                                <option value="Extended">Extended</option>
                                <option value="Core">Core</option>
                                <option value="Paper 1">Paper 1</option>
                                <option value="Paper 2">Paper 2</option>
                                <option value="Paper 3">Paper 3</option>
                            </select>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 600;">Paper Code:</label>
                            <select id="paperCode" style="width: 100%; padding: 0.5rem; border: 1px solid #dee2e6; border-radius: 4px;">
                                <option value="13">13</option>
                                <option value="11">11</option>
                                <option value="12">12</option>
                                <option value="21">21</option>
                                <option value="22">22</option>
                                <option value="31">31</option>
                                <option value="32">32</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- PDF File Upload -->
                <div style="margin-top: 2rem;">
                    <h4>📎 PDF File</h4>
                    <div id="upload-area" class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <div style="font-size: 2.5rem; margin-bottom: 1rem;">📄</div>
                        <h3>Select a PDF file to upload</h3>
                        <p style="color: #6c757d; margin-top: 1rem;">Click here or drag and drop your exam paper</p>
                    </div>
                </div>

                <input type="file" id="fileInput" accept=".pdf" style="display: none;">
                
                <div id="file-info" class="file-info hidden">
                    <h4>📄 Selected File</h4>
                    <div id="file-details"></div>
                </div>
                
                <div id="uploadStatus"></div>
                
                <button id="uploadBtn" class="btn" onclick="uploadFile()" disabled>
                    📤 Upload PDF
                </button>
            </div>

            <!-- Extract Tab -->
            <div class="tab-pane" id="extract-tab">
                <h2>⚙️ Extract Questions</h2>
                <p style="margin-bottom: 2rem; color: #6c757d;">Extract individual questions from the uploaded exam paper</p>

                <div id="extractStatus">
                    <div class="alert alert-info">
                        <strong>📋 Extraction Process:</strong>
                        <ol style="margin-top: 10px; margin-left: 20px; line-height: 1.6;">
                            <li><strong>Upload:</strong> PDF uploaded and ready for extraction</li>
                            <li><strong>AI Analysis:</strong> Automatic page structure analysis</li>
                            <li><strong>Boundary Detection:</strong> Identifies question boundaries</li>
                            <li><strong>Image Generation:</strong> Extracts each question as enhanced PNG</li>
                            <li><strong>Quality Check:</strong> Images optimized for AI reading</li>
                        </ol>
                    </div>
                </div>

                <button id="extractBtn" class="btn" onclick="extractQuestions()" disabled>
                    ⚙️ Extract Questions
                </button>

                <div id="extractProgress" class="hidden">
                    <h4>🔄 Extraction in Progress</h4>
                    <div class="progress">
                        <div id="extractProgressBar" class="progress-bar" style="width: 0%">0%</div>
                    </div>
                    <p id="extractProgressText">Initializing extraction...</p>
                </div>

                <div id="extractResults" class="hidden"></div>
            </div>

            {create_review_html_tab()}

            <!-- Solve Tab -->
            <div class="tab-pane" id="solve-tab">
                <h2>🤖 Enhanced AI Solving</h2>
                <p style="margin-bottom: 2rem; color: #6c757d;">Enhanced manual solving with batch processing and quality control</p>

                <div class="solve-features">
                    <div class="feature-card">
                        <div class="feature-icon">📋</div>
                        <h4>Batch Processing</h4>
                        <p>Copy all standardized prompts at once for efficient processing</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎯</div>
                        <h4>Quality Control</h4>
                        <p>Auto-flagging below 85% confidence with detailed metrics</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h4>Progress Tracking</h4>
                        <p>Real-time solving statistics and completion tracking</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🚀</div>
                        <h4>Enhanced Interface</h4>
                        <p>Optimized workflow for Cambridge IGCSE Physics questions</p>
                    </div>
                </div>

                <div id="solveStatus">
                    <div class="alert alert-info">
                        <strong>🤖 Enhanced Solving Features:</strong>
                        <ul style="margin-top: 10px; margin-left: 20px; line-height: 1.6;">
                            <li><strong>Batch Prompts:</strong> Copy all standardized prompts at once</li>
                            <li><strong>Quality Control:</strong> Auto-flagging below 85% confidence</li>
                            <li><strong>Progress Tracking:</strong> Real-time solving statistics</li>
                            <li><strong>Smart Export:</strong> Standardized JSON with quality metrics</li>
                            <li><strong>Enhanced Prompts:</strong> Optimized for Cambridge IGCSE Physics</li>
                        </ul>
                    </div>
                </div>

                <div class="solver-controls">
                    <button id="launchSolverBtn" class="btn enhanced" onclick="launchEnhancedSolver()" disabled>
                        🚀 Launch AI Solver
                    </button>
                    <button class="btn secondary" onclick="openClaudeAI()">
                        🌐 Open Claude.ai
                    </button>
                    <button class="btn" onclick="showSolverHelp()">
                        ❓ How to Use
                    </button>
                </div>

                <div id="solverProgress" class="hidden">
                    <h4>🔄 Initializing Enhanced Solver</h4>
                    <div class="progress">
                        <div id="solverProgressBar" class="progress-bar" style="width: 0%">0%</div>
                    </div>
                    <p id="solverProgressText">Preparing solving interface...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;
        let extractionComplete = false;
        let questionsExtracted = 0;
        let examMetadata = {{}};
        let currentPaperFolder = null;

        // Review Tab Variables
        let currentImages = [];
        let pendingReplacements = {{}};

        // Tab switching with auto-loading for review tab
        function showTab(tabName) {{
            document.querySelectorAll('.tab-pane').forEach(pane => {{
                pane.classList.remove('active');
            }});
            document.querySelectorAll('.nav-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.getElementById(tabName + '-tab').classList.add('active');
            document.getElementById(tabName + '-tab-btn').classList.add('active');
            
            // Auto-load images when switching to review tab (if not already loaded)
            if (tabName === 'review' && currentPaperFolder) {{
                const galleryDiv = document.getElementById('imageGallery');
                // Only load if gallery is hidden (not already loaded)
                if (galleryDiv.classList.contains('hidden')) {{
                    setTimeout(() => autoLoadImagesForReview(), 500);
                }}
            }}
        }}

        // File selection handler
        document.getElementById('fileInput').addEventListener('change', function(e) {{
            selectedFile = e.target.files[0];
            
            if (selectedFile) {{
                const fileInfo = document.getElementById('file-info');
                const fileDetails = document.getElementById('file-details');
                const uploadArea = document.getElementById('upload-area');
                
                fileDetails.innerHTML = `
                    <p><strong>Name:</strong> ${{selectedFile.name}}</p>
                    <p><strong>Size:</strong> ${{(selectedFile.size / (1024*1024)).toFixed(2)}} MB</p>
                    <p><strong>Type:</strong> ${{selectedFile.type}}</p>
                    <p><strong>Last Modified:</strong> ${{new Date(selectedFile.lastModified).toLocaleString()}}</p>
                `;
                fileInfo.classList.remove('hidden');
                
                uploadArea.classList.add('success');
                uploadArea.innerHTML = `
                    <div style="font-size: 2.5rem; margin-bottom: 1rem; color: #28a745;">✅</div>
                    <h3 style="color: #28a745;">File Ready for Upload</h3>
                    <p style="color: #6c757d; margin-top: 1rem;"><strong>${{selectedFile.name}}</strong></p>
                    <p style="color: #6c757d; font-size: 14px;">${{(selectedFile.size / (1024*1024)).toFixed(2)}} MB</p>
                `;
                
                document.getElementById('uploadBtn').disabled = false;
            }}
        }});

        // Check if paper already exists before upload
        function checkPaperExists() {{
            const metadata = {{
                exam_type: document.getElementById('examType').value,
                subject: document.getElementById('subject').value,
                year: parseInt(document.getElementById('year').value),
                month: document.getElementById('month').value,
                paper_type: document.getElementById('paperType').value,
                paper_code: document.getElementById('paperCode').value
            }};

            return fetch('/api/check-paper-exists', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify(metadata)
            }})
            .then(response => response.json());
        }}

        // Upload file with overwrite warning
        function uploadFile() {{
            if (!selectedFile) {{
                showAlert('uploadStatus', 'error', 'Please select a PDF file first');
                return;
            }}

            // First check if paper exists
            checkPaperExists()
                .then(data => {{
                    if (data.exists) {{
                        // Show overwrite warning
                        const confirmOverwrite = confirm(
                            `⚠️ PAPER ALREADY EXISTS\\n\\n${{data.message}}\\n\\nUploading will REPLACE all existing questions for this paper.\\n\\nDo you want to continue?`
                        );
                        
                        if (!confirmOverwrite) {{
                            showAlert('uploadStatus', 'warning', '📋 Upload cancelled. Paper was not overwritten.');
                            return;
                        }}
                        
                        showAlert('uploadStatus', 'warning', `⚠️ Overwriting existing paper: ${{data.paper_name}}`);
                    }}
                    
                    // Proceed with upload
                    performUpload();
                }})
                .catch(error => {{
                    console.error('Error checking paper existence:', error);
                    // If check fails, proceed with upload anyway
                    performUpload();
                }});
        }}

        // Perform the actual upload
        function performUpload() {{
            examMetadata = {{
                exam_type: document.getElementById('examType').value,
                subject: document.getElementById('subject').value,
                year: parseInt(document.getElementById('year').value),
                month: document.getElementById('month').value,
                paper_type: document.getElementById('paperType').value,
                paper_code: document.getElementById('paperCode').value
            }};

            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('metadata', JSON.stringify(examMetadata));

            const uploadBtn = document.getElementById('uploadBtn');
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<span class="spinner"></span>Uploading...';

            fetch('/api/upload', {{
                method: 'POST',
                body: formData
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    currentPaperFolder = data.paper_folder;
                    showAlert('uploadStatus', 'success', `✅ ${{examMetadata.exam_type}} ${{examMetadata.subject}} ${{examMetadata.year}} ${{examMetadata.month}} Paper ${{examMetadata.paper_code}} uploaded successfully!<br>📁 Folder: ${{data.paper_folder}}`);
                    
                    document.getElementById('extract-tab-btn').disabled = false;
                    document.getElementById('extractBtn').disabled = false;
                    
                    setTimeout(() => showTab('extract'), 2000);
                }} else {{
                    showAlert('uploadStatus', 'error', `❌ Upload failed: ${{data.error}}`);
                }}
            }})
            .catch(error => {{
                showAlert('uploadStatus', 'error', `❌ Upload error: ${{error.message}}`);
            }})
            .finally(() => {{
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '📤 Upload PDF';
            }});
        }}

        // Extract questions
        function extractQuestions() {{
            const extractBtn = document.getElementById('extractBtn');
            const progressDiv = document.getElementById('extractProgress');
            const progressBar = document.getElementById('extractProgressBar');
            const progressText = document.getElementById('extractProgressText');
            const resultsDiv = document.getElementById('extractResults');

            extractBtn.disabled = true;
            extractBtn.innerHTML = '<span class="spinner"></span>Running Extractor...';
            progressDiv.classList.remove('hidden');
            resultsDiv.classList.add('hidden');

            // Progress simulation
            let progress = 0;
            const stages = [
                {{ progress: 15, text: "Loading extractor module..." }},
                {{ progress: 30, text: "Analyzing PDF structure..." }},
                {{ progress: 50, text: "Detecting question boundaries..." }},
                {{ progress: 70, text: "Extracting question images..." }},
                {{ progress: 90, text: "Enhancing image quality..." }},
                {{ progress: 100, text: "Finalizing extraction..." }}
            ];
            
            let stageIndex = 0;
            const progressInterval = setInterval(() => {{
                if (stageIndex < stages.length) {{
                    const stage = stages[stageIndex];
                    progress = stage.progress;
                    progressBar.style.width = progress + '%';
                    progressBar.textContent = progress + '%';
                    progressText.textContent = stage.text;
                    stageIndex++;
                }} else {{
                    clearInterval(progressInterval);
                }}
            }}, 1000);

            fetch('/api/extract', {{
                method: 'POST'
            }})
            .then(response => response.json())
            .then(data => {{
                clearInterval(progressInterval);
                progressBar.style.width = '100%';
                progressBar.textContent = '100%';
                
                if (data.success) {{
                    questionsExtracted = data.questions_found;
                    currentPaperFolder = data.paper_folder_name;
                    progressText.textContent = `✅ Successfully extracted ${{questionsExtracted}} questions!`;
                    
                    resultsDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h3>🎉 Extraction Successful!</h3>
                            <div class="results-grid">
                                <div class="result-card">
                                    <h4>📊 Extraction Results</h4>
                                    <p><strong>Questions found:</strong> ${{data.questions_found}}</p>
                                    <p><strong>Status:</strong> ✅ Ready for processing</p>
                                </div>
                                <div class="result-card">
                                    <h4>🎯 Next Steps</h4>
                                    <button class="btn enhanced" onclick="showTab('solve')" style="margin: 0.5rem 0;">
                                        🚀 Go Directly to Solve
                                    </button>
                                    <button class="btn" onclick="showTab('review')" style="margin: 0.5rem 0;">
                                        🔍 Review Images First
                                    </button>
                                    <p style="margin-top: 1rem; font-size: 12px; color: #6c757d;">Both tabs are now enabled!</p>
                                </div>
                            </div>
                        </div>
                    `;
                    resultsDiv.classList.remove('hidden');
                    extractionComplete = true;
                    
                    // Enable review tab first
                    enableReviewTab();
                    
                    showAlert('extractStatus', 'info', '💡 Both Review and Solve tabs are now available!');
                    
                }} else {{
                    progressText.textContent = `❌ Extraction failed`;
                    showAlert('extractStatus', 'error', `Extraction failed: ${{data.error}}`);
                }}
            }})
            .catch(error => {{
                clearInterval(progressInterval);
                showAlert('extractStatus', 'error', `Extraction error: ${{error.message}}`);
            }})
            .finally(() => {{
                extractBtn.disabled = false;
                extractBtn.innerHTML = '⚙️ Extract Questions';
            }});
        }}

        // Updated workflow functions for correct order
        function enableReviewTab() {{
            document.getElementById('review-tab-btn').disabled = false;
            
            // IMPORTANT: Also enable Solve tab after extraction
            enableSolveTab();
            
            // Auto-switch to review tab after extraction
            setTimeout(() => {{
                showTab('review');
            }}, 3000);
        }}

        function enableSolveTab() {{
            document.getElementById('solve-tab-btn').disabled = false;
            document.getElementById('launchSolverBtn').disabled = false;
        }}

        function enableSolveAfterReview() {{
            enableSolveTab();
            showAlert('reviewStatus', 'success', '✅ Review complete! You can now go to the Solve tab to process questions.');
        }}

        function enableReviewAndSolve() {{
            document.getElementById('review-tab-btn').disabled = false;
            document.getElementById('solve-tab-btn').disabled = false;
            document.getElementById('launchSolverBtn').disabled = false;
        }}

        // Enhanced Solver Functions - UPDATED API ENDPOINT
        function launchEnhancedSolver() {{
            if (!currentPaperFolder) {{
                showAlert('solveStatus', 'error', 'No paper folder available. Please extract questions first.');
                return;
            }}
            
            const progressDiv = document.getElementById('solverProgress');
            progressDiv.classList.remove('hidden');
            
            document.getElementById('solverProgressText').textContent = 'Initializing enhanced solver...';
            document.getElementById('solverProgressBar').style.width = '30%';
            
            // Initialize enhanced solver - CORRECTED ENDPOINT
            fetch('/api/ai-solver/initialize', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    paper_folder: currentPaperFolder
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    document.getElementById('solverProgressBar').style.width = '100%';
                    document.getElementById('solverProgressText').textContent = 
                        `✅ Enhanced solver ready! Found ${{data.data.total_questions}} questions.`;
                    
                    // Open enhanced solver in new tab
                    const solverUrl = `/ai-solver/${{currentPaperFolder}}`;
                    window.open(solverUrl, '_blank', 'width=1600,height=1000');
                    
                    showAlert('solveStatus', 'success', 
                        `🚀 Enhanced AI Solver launched for ${{data.data.subject}} ${{data.data.year}} ${{data.data.month}} Paper ${{data.data.paper_code}}`);
                    
                    setTimeout(() => {{
                        progressDiv.classList.add('hidden');
                    }}, 3000);
                }} else {{
                    showAlert('solveStatus', 'error', `❌ Failed to initialize solver: ${{data.error}}`);
                    progressDiv.classList.add('hidden');
                }}
            }})
            .catch(error => {{
                showAlert('solveStatus', 'error', `❌ Solver initialization error: ${{error.message}}`);
                progressDiv.classList.add('hidden');
            }});
        }}

        function openClaudeAI() {{
            window.open('https://claude.ai', '_blank');
        }}

        function showSolverHelp() {{
            alert(`🤖 Enhanced AI Solver Help

1. 🚀 Launch Enhanced Solver
   • Opens a new tab with the solving interface
   • Shows all extracted questions with images

2. 📋 Batch Processing
   • Click "Get All Prompts" to copy all prompts at once
   • Each prompt is labeled with question number

3. 🌐 Using Claude.ai
   • Upload question image to Claude.ai
   • Paste the standardized prompt
   • Copy the JSON response back to solver

4. 💾 Quality Control
   • Solutions auto-flagged if confidence < 85%
   • Real-time progress tracking
   • Validation checks for JSON format

5. 📥 Export Results
   • Export standardized JSON with quality metrics
   • Compatible with review system

Tips:
• Keep the solver tab open while working
• Process questions in batches for efficiency
• Review flagged questions carefully`);
        }}

        // Auto-load images when switching to review tab (simplified version)
        function autoLoadImagesForReview() {{
            const progressDiv = document.getElementById('reviewProgress');
            const galleryDiv = document.getElementById('imageGallery');
            
            if (!currentPaperFolder) {{
                showAlert('reviewStatus', 'error', 'No paper folder available. Please extract questions first.');
                return;
            }}
            
            progressDiv.classList.remove('hidden');
            galleryDiv.classList.add('hidden');
            
            document.getElementById('reviewProgressText').textContent = 'Loading extracted images...';
            document.getElementById('reviewProgressBar').style.width = '50%';
            document.getElementById('reviewProgressBar').textContent = '50%';
            
            fetch('/api/review/load-images', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    paper_folder: currentPaperFolder
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    currentImages = data.images;
                    renderImageGallery(data);
                    
                    document.getElementById('galleryInfo').textContent = 
                        `${{data.total_images}} questions found in ${{data.paper_folder}}`;
                    
                    galleryDiv.classList.remove('hidden');
                    document.getElementById('reviewControls').classList.remove('hidden');
                    
                    document.getElementById('reviewProgressBar').style.width = '100%';
                    document.getElementById('reviewProgressBar').textContent = '100%';
                    document.getElementById('reviewProgressText').textContent = 
                        `✅ Successfully loaded ${{data.total_images}} images for review`;
                    
                    setTimeout(() => {{
                        progressDiv.classList.add('hidden');
                    }}, 2000);
                }} else {{
                    showAlert('reviewStatus', 'error', `❌ Failed to load images: ${{data.error}}`);
                    progressDiv.classList.add('hidden');
                }}
            }})
            .catch(error => {{
                showAlert('reviewStatus', 'error', `❌ Error loading images: ${{error.message}}`);
                progressDiv.classList.add('hidden');
            }});
        }}

        // Manual load function (kept for manual refresh if needed)
        function loadImagesForReview() {{
            autoLoadImagesForReview();
        }}

        function renderImageGallery(data) {{
            const gridDiv = document.getElementById('imageGrid');
            gridDiv.innerHTML = '';
            
            data.images.forEach((image, index) => {{
                const cardDiv = document.createElement('div');
                cardDiv.className = 'image-review-card';
                cardDiv.id = `image-card-${{image.question_number}}`;
                
                cardDiv.innerHTML = `
                    <h5>Question ${{image.question_number}}</h5>
                    <img src="${{image.url}}" alt="Question ${{image.question_number}}" 
                         class="image-preview" loading="lazy"
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div style="display: none; padding: 2rem; color: #dc3545;">❌ Image not found</div>
                    
                    <div class="image-info">
                        <div><strong>File:</strong> ${{image.filename}}</div>
                        <div><strong>Size:</strong> ${{image.file_size_mb}} MB</div>
                        <div><strong>Dimensions:</strong> ${{image.dimensions}}</div>
                        <div><strong>Status:</strong> <span class="status-badge status-${{image.status}}">${{image.status}}</span></div>
                    </div>
                    
                    <div class="image-actions">
                        <button class="btn btn-small" onclick="toggleReplacement(${{image.question_number}})">
                            🔄 Replace Image
                        </button>
                        <button class="btn btn-small" onclick="previewFullSize('${{image.url}}')">
                            🔍 Full Size
                        </button>
                    </div>
                    
                    <div class="upload-replacement" id="upload-${{image.question_number}}">
                        <div style="margin-bottom: 1rem;">
                            <strong>📤 Upload Replacement Image</strong>
                            <p style="color: #6c757d; font-size: 12px; margin-top: 0.5rem;">
                                Supports PNG, JPG, JPEG (max 10MB)
                            </p>
                        </div>
                        <input type="file" id="file-${{image.question_number}}" 
                               accept=".png,.jpg,.jpeg" style="display: none;"
                               onchange="handleImageReplacement(${{image.question_number}}, this)">
                        <div onclick="document.getElementById('file-${{image.question_number}}').click()" 
                             style="cursor: pointer; padding: 1rem; border: 2px dashed #4facfe; border-radius: 6px;">
                            Click to select replacement image
                        </div>
                        <div style="margin-top: 1rem;">
                            <button class="btn btn-small danger" onclick="toggleReplacement(${{image.question_number}})">
                                ❌ Cancel
                            </button>
                        </div>
                    </div>
                    
                    <div class="replacement-preview" id="preview-${{image.question_number}}">
                        <strong>🔍 Replacement Ready</strong>
                        <div id="preview-content-${{image.question_number}}"></div>
                        <div style="margin-top: 1rem;">
                            <button class="btn btn-small success" onclick="confirmReplacement(${{image.question_number}})">
                                ✅ Confirm
                            </button>
                            <button class="btn btn-small danger" onclick="cancelReplacement(${{image.question_number}})">
                                ❌ Cancel
                            </button>
                        </div>
                    </div>
                `;
                
                gridDiv.appendChild(cardDiv);
            }});
        }}

        function toggleReplacement(questionNumber) {{
            const uploadDiv = document.getElementById(`upload-${{questionNumber}}`);
            const previewDiv = document.getElementById(`preview-${{questionNumber}}`);
            
            if (uploadDiv.classList.contains('active')) {{
                uploadDiv.classList.remove('active');
            }} else {{
                // Hide all other open upload/preview sections
                document.querySelectorAll('.upload-replacement.active, .replacement-preview.active')
                    .forEach(div => div.classList.remove('active'));
                
                uploadDiv.classList.add('active');
                previewDiv.classList.remove('active');
            }}
        }}

        function handleImageReplacement(questionNumber, fileInput) {{
            const file = fileInput.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('question_number', questionNumber);
            
            const originalImage = currentImages.find(img => img.question_number === questionNumber);
            if (originalImage) {{
                formData.append('original_filename', originalImage.filename);
            }}
            
            const uploadDiv = document.getElementById(`upload-${{questionNumber}}`);
            const previewDiv = document.getElementById(`preview-${{questionNumber}}`);
            
            // Show loading
            uploadDiv.innerHTML = '<div style="padding: 2rem;"><span class="spinner"></span>Processing image...</div>';
            
            fetch('/api/review/replace-image', {{
                method: 'POST',
                body: formData
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    // Show preview
                    const previewContent = document.getElementById(`preview-content-${{questionNumber}}`);
                    previewContent.innerHTML = `
                        <img src="${{data.preview_url}}" alt="Replacement preview" style="max-width: 100%; max-height: 150px; margin: 0.5rem 0;">
                        <div style="font-size: 12px; color: #6c757d;">
                            <div>Size: ${{data.replacement_info.file_size_mb}} MB</div>
                            <div>Dimensions: ${{data.replacement_info.dimensions}}</div>
                        </div>
                    `;
                    
                    uploadDiv.classList.remove('active');
                    previewDiv.classList.add('active');
                    
                    // Mark card as having replacement
                    const card = document.getElementById(`image-card-${{questionNumber}}`);
                    card.classList.add('has-replacement');
                    
                    pendingReplacements[questionNumber] = data.replacement_info;
                    updatePendingCount();
                    
                    showAlert('reviewStatus', 'success', 
                        `✅ Replacement image staged for Question ${{questionNumber}}`);
                }} else {{
                    showAlert('reviewStatus', 'error', `❌ Failed to stage replacement: ${{data.error}}`);
                    // Reset upload div
                    toggleReplacement(questionNumber);
                    toggleReplacement(questionNumber);
                }}
            }})
            .catch(error => {{
                showAlert('reviewStatus', 'error', `❌ Error uploading replacement: ${{error.message}}`);
                // Reset upload div
                toggleReplacement(questionNumber);
                toggleReplacement(questionNumber);
            }});
        }}

        function confirmReplacement(questionNumber) {{
            const previewDiv = document.getElementById(`preview-${{questionNumber}}`);
            previewDiv.classList.remove('active');
            
            showAlert('reviewStatus', 'info', 
                `✅ Replacement for Question ${{questionNumber}} confirmed. Click "Update All Changes" to apply.`);
        }}

        function cancelReplacement(questionNumber) {{
            const card = document.getElementById(`image-card-${{questionNumber}}`);
            const previewDiv = document.getElementById(`preview-${{questionNumber}}`);
            
            card.classList.remove('has-replacement');
            previewDiv.classList.remove('active');
            
            delete pendingReplacements[questionNumber];
            updatePendingCount();
            
            showAlert('reviewStatus', 'info', `Replacement for Question ${{questionNumber}} cancelled`);
        }}

        function updatePendingCount() {{
            const count = Object.keys(pendingReplacements).length;
            const countSpan = document.getElementById('pendingCount');
            const updateBtn = document.getElementById('updateAllBtn');
            const resetBtn = document.getElementById('resetReplacementsBtn');
            
            if (count > 0) {{
                countSpan.textContent = `${{count}} pending replacement${{count > 1 ? 's' : ''}}`;
                countSpan.style.display = 'inline';
                updateBtn.disabled = false;
                resetBtn.disabled = false;
            }} else {{
                countSpan.style.display = 'none';
                updateBtn.disabled = true;
                resetBtn.disabled = true;
            }}
        }}

        function updateAllImages() {{
            const updateBtn = document.getElementById('updateAllBtn');
            const count = Object.keys(pendingReplacements).length;
            
            if (count === 0) {{
                showAlert('reviewStatus', 'warning', 'No pending replacements to apply');
                return;
            }}
            
            const confirmUpdate = confirm(
                `Apply ${{count}} image replacement${{count > 1 ? 's' : ''}}?\\n\\nThis will permanently replace the original images.\\nBackups will be created automatically.\\n\\nContinue?`
            );
            
            if (!confirmUpdate) return;
            
            updateBtn.disabled = true;
            updateBtn.innerHTML = '<span class="spinner"></span>Updating Images...';
            
            fetch('/api/review/update-all-images', {{
                method: 'POST'
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    // Clear all replacement indicators
                    document.querySelectorAll('.image-review-card').forEach(card => {{
                        card.classList.remove('has-replacement');
                    }});
                    document.querySelectorAll('.replacement-preview.active').forEach(preview => {{
                        preview.classList.remove('active');
                    }});
                    
                    pendingReplacements = {{}};
                    updatePendingCount();
                    
                    showAlert('reviewStatus', 'success', 
                        `🎉 Successfully updated ${{data.applied_count}} images!\\nBackups saved to: backup_images folder`);
                    
                    // Enable solve tab after successful review completion
                    enableSolveAfterReview();
                    
                    // IMPROVED: Force complete image refresh with multiple strategies
                    setTimeout(() => {{
                        console.log('🔄 Starting aggressive image refresh...');
                        
                        // Strategy 1: Reload images with unique timestamps
                        document.querySelectorAll('.image-preview').forEach((img, index) => {{
                            const currentSrc = img.src;
                            if (currentSrc) {{
                                const baseUrl = currentSrc.split('?')[0];
                                const uniqueTimestamp = Date.now() + Math.random() * 1000 + index;
                                const newSrc = baseUrl + `?nocache=${{uniqueTimestamp}}&refresh=${{Math.random()}}`;
                                
                                console.log(`🔄 Refreshing image ${{index + 1}}: ${{newSrc}}`);
                                
                                // Create new image element to force reload
                                const newImg = new Image();
                                newImg.onload = function() {{
                                    img.src = newSrc;
                                    console.log(`✅ Image ${{index + 1}} refreshed successfully`);
                                }};
                                newImg.onerror = function() {{
                                    console.log(`❌ Failed to refresh image ${{index + 1}}`);
                                    // Fallback: try direct assignment
                                    img.src = newSrc;
                                }};
                                newImg.src = newSrc;
                            }}
                        }});
                        
                        // Strategy 2: Full gallery reload after a delay
                        setTimeout(() => {{
                            console.log('🔄 Full gallery reload...');
                            forceReloadImages();
                        }}, 2000);
                        
                        // Strategy 3: Individual image refresh as final fallback
                        setTimeout(() => {{
                            console.log('🔄 Individual refresh fallback...');
                            document.querySelectorAll('.image-preview').forEach((img, index) => {{
                                if (img.complete && img.naturalHeight === 0) {{
                                    console.log(`🔄 Fixing broken image ${{index + 1}}`);
                                    const questionNumber = index + 1;
                                    forceRefreshImage(questionNumber);
                                }}
                            }});
                        }}, 4000);
                        
                    }}, 500);
                }} else {{
                    showAlert('reviewStatus', 'error', `❌ Failed to update images: ${{data.error}}`);
                }}
            }})
            .catch(error => {{
                showAlert('reviewStatus', 'error', `❌ Error updating images: ${{error.message}}`);
            }})
            .finally(() => {{
                updateBtn.disabled = false;
                updateBtn.innerHTML = '💾 Update All Changes';
            }});
        }}

        function forceReloadImages() {{
            console.log('🔄 Starting full image reload...');
            
            fetch('/api/review/load-images', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    paper_folder: currentPaperFolder
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    currentImages = data.images;
                    console.log('📊 Loaded fresh image data:', data.images.length, 'images');
                    
                    // Update all image sources with fresh URLs
                    data.images.forEach((image, index) => {{
                        const imgElement = document.querySelector(`#image-card-${{image.question_number}} .image-preview`);
                        if (imgElement) {{
                            console.log(`🔄 Updating image ${{image.question_number}} with URL: ${{image.url}}`);
                            
                            // Force browser to reload by creating new image element
                            const newImg = new Image();
                            newImg.onload = function() {{
                                imgElement.src = image.url;
                                console.log(`✅ Image ${{image.question_number}} updated successfully`);
                            }};
                            newImg.onerror = function() {{
                                console.log(`❌ Failed to load new image ${{image.question_number}}`);
                                // Try direct assignment anyway
                                imgElement.src = image.url;
                            }};
                            newImg.src = image.url;
                            
                            // Also update image info
                            const infoDiv = document.querySelector(`#image-card-${{image.question_number}} .image-info`);
                            if (infoDiv) {{
                                infoDiv.innerHTML = `
                                    <div><strong>File:</strong> ${{image.filename}}</div>
                                    <div><strong>Size:</strong> ${{image.file_size_mb}} MB</div>
                                    <div><strong>Dimensions:</strong> ${{image.dimensions}}</div>
                                    <div><strong>Status:</strong> <span class="status-badge status-${{image.status}}">${{image.status}}</span></div>
                                `;
                            }}
                        }}
                    }});
                    
                    showAlert('reviewStatus', 'success', 
                        `✅ Images refreshed successfully! Updated images should now be visible.`);
                }} else {{
                    showAlert('reviewStatus', 'error', `❌ Failed to refresh images: ${{data.error}}`);
                }}
            }})
            .catch(error => {{
                console.error('❌ Error in forceReloadImages:', error);
                showAlert('reviewStatus', 'error', `❌ Error refreshing images: ${{error.message}}`);
            }});
        }}

        function forceRefreshImage(questionNumber) {{
            const imgElement = document.querySelector(`#image-card-${{questionNumber}} .image-preview`);
            if (imgElement) {{
                console.log(`🔄 Force refreshing image ${{questionNumber}}`);
                
                const baseUrl = imgElement.src.split('?')[0];
                const uniqueTimestamp = Date.now() + Math.random() * 1000;
                const newSrc = baseUrl + `?nocache=${{uniqueTimestamp}}&refresh=${{Math.random()}}&q=${{questionNumber}}`;
                
                // Create new image to preload
                const newImg = new Image();
                newImg.onload = function() {{
                    imgElement.src = newSrc;
                    console.log(`✅ Image ${{questionNumber}} force refresh completed`);
                    showAlert('reviewStatus', 'info', `🔄 Refreshed image for Question ${{questionNumber}}`);
                }};
                newImg.onerror = function() {{
                    console.log(`❌ Force refresh failed for image ${{questionNumber}}`);
                    // Fallback: direct assignment
                    imgElement.src = newSrc;
                }};
                newImg.src = newSrc;
            }}
        }}

        function resetReplacements() {{
            const count = Object.keys(pendingReplacements).length;
            
            if (count === 0) {{
                showAlert('reviewStatus', 'warning', 'No pending replacements to reset');
                return;
            }}
            
            const confirmReset = confirm(
                `Reset ${{count}} pending replacement${{count > 1 ? 's' : ''}}?\\n\\nAll staged replacements will be discarded.`
            );
            
            if (!confirmReset) return;
            
            fetch('/api/review/reset-replacements', {{
                method: 'POST'
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    // Clear all replacement indicators
                    document.querySelectorAll('.image-review-card').forEach(card => {{
                        card.classList.remove('has-replacement');
                    }});
                    document.querySelectorAll('.replacement-preview.active, .upload-replacement.active').forEach(div => {{
                        div.classList.remove('active');
                    }});
                    
                    pendingReplacements = {{}};
                    updatePendingCount();
                    
                    showAlert('reviewStatus', 'success', 
                        `✅ Reset ${{data.cleared_count}} pending replacements`);
                }} else {{
                    showAlert('reviewStatus', 'error', `❌ Failed to reset: ${{data.error}}`);
                }}
            }})
            .catch(error => {{
                showAlert('reviewStatus', 'error', `❌ Error resetting: ${{error.message}}`);
            }});
        }}

        function previewFullSize(imageUrl) {{
            window.open(imageUrl, '_blank');
        }}

        function goToSolve() {{
            const confirmGo = confirm(
                `🚀 Go to Solve Tab?\\n\\nThis will:\\n• Keep current images as-is\\n• Enable the Solve tab\\n• Switch to Solve tab\\n\\nContinue?`
            );
            
            if (confirmGo) {{
                // Ensure solve tab is enabled
                enableSolveTab();
                
                // Switch to solve tab
                showTab('solve');
                
                showAlert('reviewStatus', 'info', 
                    '🚀 Moved to Solve tab. Images ready for processing. You can return to Review anytime.');
            }}
        }}

        // Utility function to show alerts
        function showAlert(containerId, type, message) {{
            const container = document.getElementById(containerId);
            container.innerHTML = `<div class="alert alert-${{type}}">${{message}}</div>`;
            
            if (type === 'success' || type === 'info') {{
                setTimeout(() => {{
                    if (container.innerHTML.includes(message.substring(0, 50))) {{
                        container.innerHTML = '';
                    }}
                }}, 10000);
            }}
        }}

        // Drag and drop support
        const uploadArea = document.getElementById('upload-area');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {{
            uploadArea.addEventListener(eventName, preventDefaults, false);
        }});

        function preventDefaults(e) {{
            e.preventDefault();
            e.stopPropagation();
        }}

        ['dragenter', 'dragover'].forEach(eventName => {{
            uploadArea.addEventListener(eventName, highlight, false);
        }});

        ['dragleave', 'drop'].forEach(eventName => {{
            uploadArea.addEventListener(eventName, unhighlight, false);
        }});

        function highlight(e) {{
            uploadArea.style.background = '#e3f2fd';
            uploadArea.style.borderColor = '#2196F3';
        }}

        function unhighlight(e) {{
            uploadArea.style.background = selectedFile ? '#f0fff0' : '#f8f9ff';
            uploadArea.style.borderColor = selectedFile ? '#28a745' : '#4facfe';
        }}

        uploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {{
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {{
                const file = files[0];
                if (file.type === 'application/pdf') {{
                    selectedFile = file;
                    document.getElementById('fileInput').files = files;
                    const event = new Event('change', {{ bubbles: true }});
                    document.getElementById('fileInput').dispatchEvent(event);
                }} else {{
                    showAlert('uploadStatus', 'error', '❌ Please drop a PDF file only.');
                }}
            }}
        }}

        // Check initial status - Updated for correct workflow order
        window.addEventListener('load', function() {{
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {{
                    console.log('Status check result:', data);
                    
                    // Check for existing question banks
                    if (data.question_banks && data.question_banks.length > 0) {{
                        const lastBank = data.question_banks[data.question_banks.length - 1];
                        if (lastBank.has_questions) {{
                            questionsExtracted = lastBank.image_count;
                            extractionComplete = true;
                            currentPaperFolder = lastBank.folder_name;
                            
                            document.getElementById('extract-tab-btn').disabled = false;
                            enableReviewAndSolve();
                            
                            showAlert('uploadStatus', 'info', `✅ Found existing question bank: ${{lastBank.folder_name}} with ${{lastBank.image_count}} questions. Both Review and Solve tabs are now available!`);
                            
                            // Show the extraction results section if questions exist
                            document.getElementById('extractResults').innerHTML = `
                                <div class="alert alert-success">
                                    <h3>🎉 Previously Extracted Questions Found!</h3>
                                    <div class="results-grid">
                                        <div class="result-card">
                                            <h4>📊 Found Results</h4>
                                            <p><strong>Questions found:</strong> ${{lastBank.image_count}}</p>
                                            <p><strong>Paper:</strong> ${{lastBank.folder_name}}</p>
                                            <p><strong>Status:</strong> ✅ Ready for solving</p>
                                        </div>
                                        <div class="result-card">
                                            <h4>🎯 Available Options</h4>
                                            <button class="btn enhanced" onclick="showTab('solve')" style="margin: 0.5rem 0;">
                                                🚀 Launch AI Solver
                                            </button>
                                            <button class="btn" onclick="showTab('review')" style="margin: 0.5rem 0;">
                                                🔍 Review Images
                                            </button>
                                            <p style="margin-top: 1rem; font-size: 12px; color: #6c757d;">
                                                Both tabs are enabled and ready to use!
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            `;
                            document.getElementById('extractResults').classList.remove('hidden');
                        }}
                    }}
                }})
                .catch(error => {{
                    console.error('Status check failed:', error);
                }});
        }});
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Serve the main unified interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    """Get current system status with question bank overview - UPDATED FOLDER PRIORITY"""
    try:
        status_data = {
            "extractor_available": module_manager.module_status['extractor']['available'],
            "backend_directory": str(BASE_DIR),
            "tutor_app_root": str(TUTOR_APP_ROOT),
            "question_banks_dir": str(QUESTION_BANKS_DIR),
            "current_file_exists": (BASE_DIR / "current_exam.pdf").exists(),
            "question_banks": [],
            "current_paper": None,
            "status": "ready"
        }
        
        # Check for existing question banks with standardized folder priority
        if QUESTION_BANKS_DIR.exists():
            for paper_folder in QUESTION_BANKS_DIR.iterdir():
                if paper_folder.is_dir():
                    # UPDATED: Check with standardized folder priority (images first, extracted_images fallback)
                    images_folder = paper_folder / "images"
                    extracted_images_folder = paper_folder / "extracted_images"
                    metadata_file = paper_folder / "metadata.json"
                    
                    # UPDATED: Count images with correct priority
                    image_count = 0
                    if images_folder.exists():
                        image_files = list(images_folder.glob("question_*_enhanced.png"))
                        image_count = len(image_files)
                    elif extracted_images_folder.exists():
                        image_files = list(extracted_images_folder.glob("question_*_enhanced.png"))
                        image_count = len(image_files)
                    
                    # Read metadata
                    metadata = {}
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                        except:
                            pass
                    
                    paper_info = {
                        "folder_name": paper_folder.name,
                        "path": str(paper_folder),
                        "image_count": image_count,
                        "metadata": metadata,
                        "has_questions": image_count > 0
                    }
                    
                    status_data["question_banks"].append(paper_info)
        
        # Check current paper status with updated folder priority
        if CURRENT_PAPER_FOLDER and CURRENT_PAPER_FOLDER.exists():
            # UPDATED: Check with standardized folder priority (images first, extracted_images fallback)
            images_folder = CURRENT_PAPER_FOLDER / "images"
            extracted_images_folder = CURRENT_PAPER_FOLDER / "extracted_images"
            
            image_count = 0
            if images_folder.exists():
                image_files = list(images_folder.glob("question_*_enhanced.png"))
                image_count = len(image_files)
            elif extracted_images_folder.exists():
                image_files = list(extracted_images_folder.glob("question_*_enhanced.png"))
                image_count = len(image_files)
            
            if image_count > 0:
                status_data["current_paper"] = {
                    "folder_name": CURRENT_PAPER_FOLDER.name,
                    "image_count": image_count,
                    "status": "extraction_complete"
                }
                status_data["status"] = "extraction_complete"
        
        return jsonify(status_data)
        
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "extractor_available": module_manager.module_status['extractor']['available']
        }), 500

@app.route('/api/check-paper-exists', methods=['POST'])
def check_paper_exists():
    """Check if a paper already exists before upload - UPDATED FOLDER PRIORITY"""
    try:
        data = request.get_json()
        
        subject = data.get('subject', 'physics').lower()
        year = data.get('year', 2024)
        month = data.get('month', 'Mar').lower()
        paper_code = data.get('paper_code', '13')
        
        paper_folder_name = f"{subject}_{year}_{month}_{paper_code}"
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder_name
        
        if paper_folder_path.exists():
            # UPDATED: Count existing questions with standardized folder priority
            images_folder = paper_folder_path / "images"
            extracted_images_folder = paper_folder_path / "extracted_images"
            question_count = 0
            
            # UPDATED: Check images folder FIRST (primary)
            if images_folder.exists():
                image_files = list(images_folder.glob("question_*_enhanced.png"))
                question_count = len(image_files)
            # UPDATED: Check extracted_images folder as FALLBACK
            elif extracted_images_folder.exists():
                image_files = list(extracted_images_folder.glob("question_*_enhanced.png"))
                question_count = len(image_files)
            
            return jsonify({
                "exists": True,
                "paper_name": paper_folder_name,
                "folder_path": str(paper_folder_path),
                "existing_questions": question_count,
                "message": f"{data.get('exam_type', 'Cambridge')} {subject.title()} {year} {month.title()} Paper {paper_code} already exists with {question_count} questions."
            })
        else:
            return jsonify({
                "exists": False,
                "paper_name": paper_folder_name
            })
            
    except Exception as e:
        print(f"❌ Error checking paper existence: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload with metadata storage and folder structure - WORKING VERSION"""
    global CURRENT_FILE_PATH, CURRENT_EXAM_METADATA, CURRENT_PAPER_FOLDER
    
    try:
        print("📋 DEBUG: Upload endpoint called")
        print(f"📋 DEBUG: Request method: {request.method}")
        print(f"📋 DEBUG: Request form keys: {list(request.form.keys())}")
        print(f"📋 DEBUG: Request files keys: {list(request.files.keys())}")
        
        if 'file' not in request.files:
            print("❌ ERROR: No file in request")
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        
        file = request.files['file']
        print(f"📋 DEBUG: File received: {file.filename}")
        
        if file.filename == '' or not file.filename.lower().endswith('.pdf'):
            print("❌ ERROR: Invalid file")
            return jsonify({"success": False, "error": "Please upload a valid PDF file"}), 400
        
        # Get exam metadata
        exam_metadata = {
            "exam_type": "Cambridge", 
            "subject": "physics", 
            "year": 2024, 
            "month": "Mar", 
            "paper_type": "Extended", 
            "paper_code": "13"
        }
        
        if 'metadata' in request.form:
            try:
                metadata_str = request.form['metadata']
                print(f"📋 DEBUG: Metadata string: {metadata_str}")
                exam_metadata.update(json.loads(metadata_str))
                print(f"📋 DEBUG: Parsed metadata: {exam_metadata}")
            except Exception as e:
                print(f"⚠️ WARNING: Failed to parse metadata: {e}")
        
        CURRENT_EXAM_METADATA = exam_metadata
        
        # Check file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        print(f"📋 DEBUG: File size: {file_size} bytes")
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            return jsonify({"success": False, "error": "File too large. Maximum size is 50MB"}), 400
        
        # Create paper-specific folder structure
        subject = exam_metadata.get('subject', 'physics').lower()
        year = exam_metadata.get('year', 2024)
        month = exam_metadata.get('month', 'Mar').lower()
        paper_code = exam_metadata.get('paper_code', '13')
        
        paper_folder_name = f"{subject}_{year}_{month}_{paper_code}"
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder_name
        print(f"📋 DEBUG: Creating paper folder: {paper_folder_path}")
        paper_folder_path.mkdir(parents=True, exist_ok=True)
        
        CURRENT_PAPER_FOLDER = paper_folder_path
        
        # Save file with structured naming
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{paper_folder_name}_{timestamp}.pdf"
        file_path = UPLOAD_FOLDER / safe_filename
        print(f"📋 DEBUG: Saving file to: {file_path}")
        
        # Save file
        file.save(str(file_path))
        
        # Copy to expected location for extractor
        expected_path = BASE_DIR / "current_exam.pdf"
        print(f"📋 DEBUG: Copying to extractor location: {expected_path}")
        shutil.copy2(file_path, expected_path)
        CURRENT_FILE_PATH = expected_path
        
        # Save metadata in paper folder
        metadata_path = paper_folder_path / "metadata.json"
        print(f"📋 DEBUG: Saving metadata to: {metadata_path}")
        with open(metadata_path, 'w') as f:
            json.dump(exam_metadata, f, indent=2)
        
        # Also save in backend directory for extractor compatibility
        base_metadata_path = BASE_DIR / "current_exam_metadata.json"
        with open(base_metadata_path, 'w') as f:
            json.dump(exam_metadata, f, indent=2)
        
        print(f"✅ PDF uploaded successfully")
        print(f"   Paper folder: {paper_folder_path}")
        print(f"   Metadata: {exam_metadata}")
        
        return jsonify({
            "success": True,
            "message": f"PDF uploaded successfully for {paper_folder_name}",
            "filename": safe_filename,
            "file_size_mb": round(file_size / (1024*1024), 2),
            "metadata": exam_metadata,
            "paper_folder": paper_folder_name,
            "paper_path": str(paper_folder_path)
        })
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def extract_questions():
    """Extract questions using direct call to extractor.py with shared question_banks folder"""
    global CURRENT_PAPER_FOLDER
    
    try:
        current_file = BASE_DIR / "current_exam.pdf"
        if not current_file.exists():
            return jsonify({
                "success": False,
                "error": "No PDF file found. Please upload a file first."
            }), 400
        
        if not CURRENT_EXAM_METADATA:
            return jsonify({
                "success": False,
                "error": "No exam metadata found. Please upload a file first."
            }), 400
        
        print(f"🚀 Starting extraction with shared question_banks structure")
        print(f"   Backend: {BASE_DIR}")
        print(f"   Question Banks: {QUESTION_BANKS_DIR}")
        
        # Use the module manager to run extractor directly (not subprocess)
        result = module_manager.run_extractor(current_file, CURRENT_EXAM_METADATA)
        
        if not result["success"]:
            return jsonify(result), 500
        
        # Update global folder reference
        CURRENT_PAPER_FOLDER = Path(result["paper_folder"])
        
        # Connect review manager
        review_manager.set_current_paper_folder(result["paper_folder_name"])
        
        # Clean up uploaded file
        if current_file.exists():
            current_file.unlink()
        
        print(f"✅ Extraction completed: {result['questions_found']} questions extracted")
        print(f"   Paper folder: {result['paper_folder']}")
        
        return jsonify({
            "success": True,
            "message": f"Successfully extracted {result['questions_found']} questions for {result['paper_folder_name']}",
            "questions_found": result["questions_found"],
            "paper_folder": result["paper_folder"],
            "paper_folder_name": result["paper_folder_name"],
            "extraction_timestamp": datetime.now().isoformat(),
            "extractor_used": "direct_import"
        })
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": f"Extraction failed: {str(e)}"
        }), 500

@app.route('/images/<paper_folder>/<filename>')
def serve_paper_image(paper_folder, filename):
    """Serve images from paper-specific folders with STANDARDIZED FOLDER PRIORITY"""
    try:
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        
        # UPDATED: Try images folder FIRST (new standard)
        images_dir = paper_folder_path / "images"
        if images_dir.exists():
            image_path = images_dir / filename
            if image_path.exists():
                print(f"🖼️ Serving image: {image_path} (images - primary)")
                return create_cache_busted_response(image_path)
        
        # UPDATED: Fallback to extracted_images folder
        extracted_images_dir = paper_folder_path / "extracted_images"
        if extracted_images_dir.exists():
            image_path = extracted_images_dir / filename
            if image_path.exists():
                print(f"🖼️ Serving image: {image_path} (extracted_images - fallback)")
                return create_cache_busted_response(image_path)
        
        print(f"❌ Image not found: {filename} in {paper_folder}")
        return f"Image not found: {filename} in {paper_folder}", 404
            
    except Exception as e:
        print(f"❌ Error serving paper image {paper_folder}/{filename}: {e}")
        return "Image serving error", 500

@app.route('/images/<paper_folder>/extracted_images/<filename>')
def serve_extracted_image(paper_folder, filename):
    """Serve images from extracted_images folder with aggressive cache-busting"""
    try:
        extracted_images_dir = QUESTION_BANKS_DIR / paper_folder / "extracted_images"
        if not extracted_images_dir.exists():
            return f"Extracted images folder not found: {paper_folder}", 404
            
        image_path = extracted_images_dir / filename
        if not image_path.exists():
            return f"Image not found: {filename}", 404
            
        print(f"🖼️ Serving extracted image: {image_path}")
        return create_cache_busted_response(image_path)
        
    except Exception as e:
        print(f"❌ Error serving extracted image {paper_folder}/{filename}: {e}")
        return "Image serving error", 500

@app.route('/images/<paper_folder>/temp_replacements/<filename>')
def serve_temp_replacement_image(paper_folder, filename):
    """Serve temporary replacement images with aggressive cache-busting"""
    try:
        temp_images_dir = QUESTION_BANKS_DIR / paper_folder / "temp_replacements"
        if not temp_images_dir.exists():
            return f"Temp folder not found: {paper_folder}", 404
            
        image_path = temp_images_dir / filename
        if not image_path.exists():
            return f"Temp image not found: {filename}", 404
            
        print(f"🖼️ Serving temp replacement image: {image_path}")
        return create_cache_busted_response(image_path)
        
    except Exception as e:
        print(f"❌ Error serving temp replacement image {paper_folder}/{filename}: {e}")
        return "Image serving error", 500

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve extracted question images with STANDARDIZED FOLDER PRIORITY (backward compatibility)"""
    try:
        # Try current paper folder first with updated priority
        if CURRENT_PAPER_FOLDER and CURRENT_PAPER_FOLDER.exists():
            # UPDATED: Check images folder FIRST (new standard)
            images_folder = CURRENT_PAPER_FOLDER / "images"
            if images_folder.exists():
                image_path = images_folder / filename
                if image_path.exists():
                    print(f"🖼️ Serving image (current/images): {image_path}")
                    return create_cache_busted_response(image_path)
            
            # UPDATED: Then check extracted_images folder as fallback
            extracted_images_folder = CURRENT_PAPER_FOLDER / "extracted_images"
            if extracted_images_folder.exists():
                image_path = extracted_images_folder / filename
                if image_path.exists():
                    print(f"🖼️ Serving image (current/extracted_images): {image_path}")
                    return create_cache_busted_response(image_path)
        
        # Fallback to old extracted_images directory
        extracted_images_dir = BASE_DIR / "extracted_images"
        if extracted_images_dir.exists():
            image_path = extracted_images_dir / filename
            if image_path.exists():
                print(f"🖼️ Serving image (backend/extracted): {image_path}")
                return create_cache_busted_response(image_path)
        
        print(f"❌ Image not found: {filename}")
        return f"Image not found: {filename}", 404
            
    except Exception as e:
        print(f"❌ Error serving image {filename}: {e}")
        return "Image serving error", 500

@app.route('/api/export-results')
def export_results():
    """Export results as JSON file"""
    try:
        if not CURRENT_PAPER_FOLDER or not CURRENT_PAPER_FOLDER.exists():
            return jsonify({
                "success": False,
                "error": "No current paper folder available"
            }), 400
        
        # Look for existing JSON exports in the paper folder
        json_files = list(CURRENT_PAPER_FOLDER.glob("*.json"))
        
        # Filter out metadata.json
        export_files = [f for f in json_files if f.name != "metadata.json"]
        
        if export_files:
            # Return the most recent export file
            latest_export = max(export_files, key=lambda f: f.stat().st_mtime)
            return send_file(latest_export, as_attachment=True)
        else:
            return jsonify({
                "success": False,
                "error": "No export files found. Please solve questions first using the Enhanced AI Solver."
            }), 404
            
    except Exception as e:
        print(f"❌ Error exporting results: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Cleanup function
def cleanup():
    """Clean up any subprocess on exit"""
    for process in module_manager.processes.values():
        if process and process.poll() is None:
            process.terminate()

atexit.register(cleanup)

if __name__ == '__main__':
    print("🚀 Starting AI Tutor - Complete Workflow...")
    print("=" * 70)
    print(f"📂 Backend directory: {BASE_DIR}")
    print(f"📂 Tutor App root: {TUTOR_APP_ROOT}")
    print(f"📂 Upload folder: {UPLOAD_FOLDER}")
    print(f"📂 Question banks (shared): {QUESTION_BANKS_DIR}")
    print(f"🔧 Extractor available: {'✅ Yes' if module_manager.module_status['extractor']['available'] else '❌ No'}")
    print(f"🔍 Review System: ✅ Integrated")
    print(f"🌐 Web interface: http://localhost:5004")
    print("=" * 70)
    
    # Ensure directories exist
    BASE_DIR.mkdir(exist_ok=True)
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    QUESTION_BANKS_DIR.mkdir(exist_ok=True)
    
    app.run(
        host='0.0.0.0',
        port=5004,
        debug=True
    )