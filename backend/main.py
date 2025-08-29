#!/usr/bin/env python3
"""
Complete main.py - AI Tutor Interface with Hybrid Solver Integration
Upload • Extract • Review • Solve workflow - COMPLETE VERSION WITH HYBRID SOLVER
"""

from flask import Flask, request, jsonify, send_from_directory, render_template_string, send_file, abort, make_response, redirect
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

# Allow importing hybrid.py from same directory
sys.path.append(str(Path(__file__).parent))

# Import the review module
from review import ReviewManager, create_review_html_tab, get_review_css

# Import the hybrid solver
from hybrid import ScalableAISolverManager

app = Flask(__name__)
CORS(app)

# Configuration - Proper separation for frontend integration
BASE_DIR = Path("/Users/wynceaxcel/Apps/axcelscore/backend")
TUTOR_APP_ROOT = Path("/Users/wynceaxcel/Apps/axcelscore")
FRONTEND_PUBLIC_DIR = TUTOR_APP_ROOT / "frontend" / "public"
UPLOAD_FOLDER = BASE_DIR / "uploads"
QUESTION_BANKS_DIR = FRONTEND_PUBLIC_DIR / "question_banks"  # Shared with frontend
UPLOAD_FOLDER.mkdir(exist_ok=True)
QUESTION_BANKS_DIR.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Initialize Review Manager
review_manager = ReviewManager(QUESTION_BANKS_DIR)

# Initialize Hybrid Solver
hybrid_solver = ScalableAISolverManager(QUESTION_BANKS_DIR)

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
        TUTOR_APP_ROOT / "extractor.py",
        Path("/Users/wynceaxcel/Apps/axcelscore/extractor.py")
        ]
        
        for path in extractor_paths:
            if path.exists():
                self.module_status['extractor']['available'] = True
                self.module_status['extractor']['path'] = path
                break
                
        print(f"Extractor available: {'Yes' if self.module_status['extractor']['available'] else 'No'}")
    
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
            
            # Add extractor path to Python path for direct import
            extractor_parent = self.module_status['extractor']['path'].parent
            if str(extractor_parent) not in sys.path:
                sys.path.insert(0, str(extractor_parent))
            
            # Import the correct class name
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
            
            # Initialize extractor with correct base_dir parameter
            print("DEBUG: Initializing EnhancedPDFExtractor...")
            extractor = EnhancedPDFExtractor(base_dir=str(paper_folder_path))
            print("DEBUG: EnhancedPDFExtractor initialized successfully")
            
            # Run extraction using the correct method name
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
            
            # Proper result validation
            if result and isinstance(result, dict) and result.get('success'):
                print(f"DEBUG: Valid result received with keys: {list(result.keys())}")
                
                # Count extracted images with standardized folder priority
                image_files = []
                
                # Check images folder FIRST (new standard)
                images_folder = paper_folder_path / "images"
                if images_folder.exists():
                    image_files.extend(list(images_folder.glob("question_*_enhanced.png")))
                    print(f"DEBUG: Found {len(image_files)} images in images folder (primary)")
                
                # Check extracted_images folder as FALLBACK only if no images found
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
                
                # Return the correct images folder path
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

# SIMPLE AI SOLVER MANAGER - DIRECT INTEGRATION
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
            
            # Check with standardized folder priority (images first, extracted_images fallback)
            images_folder = paper_path / "images"
            extracted_images_folder = paper_path / "extracted_images"
            
            image_files = []
            images_dir = None
            
            # Check images folder FIRST (primary)
            if images_folder.exists():
                image_files = list(images_folder.glob("question_*_enhanced.png"))
                images_dir = images_folder
                print(f"Found images in: {images_folder}")
            # Check extracted_images folder as FALLBACK
            elif extracted_images_folder.exists():
                image_files = list(extracted_images_folder.glob("question_*_enhanced.png"))
                images_dir = extracted_images_folder
                print(f"Found images in: {extracted_images_folder}")
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
            
            print(f"AI Solver initialized for {paper_path.name}")
            print(f"   Found {len(image_files)} questions")
            
            return {
                "success": True,
                "data": {
                    "total_questions": len(image_files),
                    "paper_folder": paper_path.name,
                    "subject": metadata.get('subject', 'Unknown'),
                    "year": metadata.get('year', 'Unknown'),
                    "month": metadata.get('month', 'Unknown'),
                    "paper_code": metadata.get('paper_code', 'Unknown')
                }
            }
            
        except Exception as e:
            print(f"AI Solver error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"AI Solver initialization failed: {str(e)}"
            }

# Initialize AI Solver Manager
ai_solver_manager = SimpleAISolverManager()

# AI SOLVER ROUTES - Hybrid Integration
@app.route('/api/ai-solver/initialize', methods=['POST'])
def initialize_ai_solver():
    """Initialize AI Solver - Now uses hybrid solver"""
    try:
        data = request.get_json()
        paper_folder = data.get('paper_folder')
        
        if not paper_folder:
            return jsonify({
                "success": False,
                "error": "No paper folder specified"
            }), 400
        
        # Use hybrid solver instead of simple solver
        result = hybrid_solver.initialize_solver(paper_folder)
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        print(f"AI Solver initialization error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# HYBRID SOLVER ROUTES
@app.route('/solver/<paper_folder>')
def serve_hybrid_solver(paper_folder):
    """Serve the hybrid manual solver interface"""
    try:
        result = hybrid_solver.generate_simplified_interface(paper_folder)
        if result["success"]:
            return result["html_content"]
        else:
            return f"Error: {result['error']}", 500
    except Exception as e:
        return f"Error creating interface: {str(e)}", 500

@app.route('/api/save-solution', methods=['POST'])
def save_solution():
    """Save solution from hybrid solver"""
    try:
        data = request.get_json()
        result = hybrid_solver.save_solution(
            data.get('paper_folder'),
            data.get('question_number'),
            data.get('solution')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/get-progress', methods=['POST'])
def get_hybrid_progress():
    """Get hybrid solver progress"""
    try:
        data = request.get_json()
        result = hybrid_solver.get_progress(data.get('paper_folder'))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/export-solutions', methods=['POST'])
def export_hybrid_solutions():
    """Export solutions from hybrid solver"""
    try:
        data = request.get_json()
        result = hybrid_solver.export_solutions(data.get('paper_folder'))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Legacy route redirect for compatibility
@app.route('/ai-solver/<paper_folder>')
def serve_ai_solver_interface(paper_folder):
    """Redirect to hybrid solver for compatibility"""
    return redirect(f'/solver/{paper_folder}')

def create_cache_busted_response(image_path):
    """Create a response with aggressive cache-busting headers"""
    try:
        response = make_response(send_file(str(image_path)))
        
        stat = image_path.stat()
        etag_data = f"{stat.st_mtime}-{stat.st_size}"
        etag = hashlib.md5(etag_data.encode()).hexdigest()
        
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['ETag'] = etag
        response.headers['Last-Modified'] = datetime.fromtimestamp(stat.st_mtime).strftime('%a, %d %b %Y %H:%M:%S GMT')
        response.headers['X-Image-Cache-Bust'] = str(int(time.time() * 1000))
        
        return response
        
    except Exception as e:
        print(f"Error creating cache-busted response: {e}")
        abort(500)

# Enhanced HTML template with fixed f-string syntax and updated solver URL
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Tutor - Upload, Extract, Review & Solve</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            width: 100%;
            max-width: 1400px;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .nav-tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        .nav-tab {
            flex: 1;
            padding: 1rem;
            text-align: center;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            font-size: 14px;
        }
        .nav-tab.active {
            background: white;
            color: #4facfe;
            border-bottom: 3px solid #4facfe;
        }
        .nav-tab:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .tab-content { 
            padding: 2rem; 
            flex: 1;
            overflow-y: auto;
            min-height: 400px;
        }
        .tab-pane { display: none; }
        .tab-pane.active { display: block; }
        .upload-area {
            border: 3px dashed #4facfe;
            border-radius: 15px;
            padding: 3rem;
            text-align: center;
            margin-bottom: 2rem;
            cursor: pointer;
            transition: all 0.3s;
            background: #f8f9ff;
        }
        .upload-area:hover { background: #e6f3ff; border-color: #2196F3; }
        .upload-area.success {
            border-color: #28a745;
            background: #f0fff0;
        }
        .btn {
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
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .btn.success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); }
        .btn.danger { background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%); }
        .btn.secondary { background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); }
        .btn.enhanced { background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%); }
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-weight: 500;
        }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-info { background: #cce7ff; color: #0c5460; border: 1px solid #bee5eb; }
        .alert-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .progress {
            width: 100%;
            height: 24px;
            background: #e9ecef;
            border-radius: 12px;
            overflow: hidden;
            margin: 1rem 0;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #4facfe, #00f2fe);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }
        .hidden { display: none !important; }
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #ffffff;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .file-info {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        .result-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
        }
        .question-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        .question-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }
        .question-card img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        .question-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: center;
            flex-wrap: wrap;
        }
        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 12px;
        }
        .status-ready {
            color: #28a745;
            font-weight: bold;
        }
        .status-pending {
            color: #ffc107;
            font-weight: bold;
        }
        .status-error {
            color: #dc3545;
            font-weight: bold;
        }
        .solve-features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        .feature-card {
            background: linear-gradient(135deg, #f8f9ff 0%, #e6f3ff 100%);
            border: 1px solid #4facfe;
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
        }
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        .solver-controls {
            display: flex;
            gap: 1rem;
            margin: 2rem 0;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        /* Review Tab Specific Styles */
        ''' + get_review_css() + '''
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Tutor - Complete Workflow</h1>
            <p>Upload, Extract, Review & Solve exam papers with AI-powered processing</p>
        </div>

        <div class="nav-tabs">
            <button id="upload-tab-btn" class="nav-tab active" onclick="showTab('upload')">Upload</button>
            <button id="extract-tab-btn" class="nav-tab" onclick="showTab('extract')" disabled>Extract</button>
            <button id="review-tab-btn" class="nav-tab" onclick="showTab('review')" disabled>Review</button>
            <button id="solve-tab-btn" class="nav-tab" onclick="showTab('solve')" disabled>Solve</button>
        </div>

        <div class="tab-content">
            <!-- Upload Tab -->
            <div class="tab-pane active" id="upload-tab">
                <h2>Upload Exam PDF</h2>
                <p style="margin-bottom: 2rem; color: #6c757d;">Upload a Cambridge IGCSE exam paper PDF for AI-powered processing</p>

                <!-- Exam Information Form -->
                <div class="file-info" style="display: block;">
                    <h4>Exam Information</h4>
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
                    <h4>PDF File</h4>
                    <div id="upload-area" class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <div style="font-size: 2.5rem; margin-bottom: 1rem;">📄</div>
                        <h3>Select a PDF file to upload</h3>
                        <p style="color: #6c757d; margin-top: 1rem;">Click here or drag and drop your exam paper</p>
                    </div>
                </div>

                <input type="file" id="fileInput" accept=".pdf" style="display: none;">
                
                <div id="file-info" class="file-info hidden">
                    <h4>Selected File</h4>
                    <div id="file-details"></div>
                </div>
                
                <div id="uploadStatus"></div>
                
                <button id="uploadBtn" class="btn" onclick="uploadFile()" disabled>
                    Upload PDF
                </button>
            </div>

            <!-- Extract Tab -->
            <div class="tab-pane" id="extract-tab">
                <h2>Extract Questions</h2>
                <p style="margin-bottom: 2rem; color: #6c757d;">Extract individual questions from the uploaded exam paper</p>

                <div id="extractStatus">
                    <div class="alert alert-info">
                        <strong>Extraction Process:</strong>
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
                    Extract Questions
                </button>

                <div id="extractProgress" class="hidden">
                    <h4>Extraction in Progress</h4>
                    <div class="progress">
                        <div id="extractProgressBar" class="progress-bar" style="width: 0%">0%</div>
                    </div>
                    <p id="extractProgressText">Initializing extraction...</p>
                </div>

                <div id="extractResults" class="hidden"></div>
            </div>

            ''' + create_review_html_tab() + '''

            <!-- Solve Tab -->
            <div class="tab-pane" id="solve-tab">
                <h2>Hybrid AI Solving</h2>
                <p style="margin-bottom: 2rem; color: #6c757d;">Enhanced manual solving with colorful interface and quality control</p>

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
                        <div class="feature-icon">🎨</div>
                        <h4>Colorful Interface</h4>
                        <p>Gen Alpha design with animated gradients and modern UI</p>
                    </div>
                </div>

                <div id="solveStatus">
                    <div class="alert alert-info">
                        <strong>Hybrid Solving Features:</strong>
                        <ul style="margin-top: 10px; margin-left: 20px; line-height: 1.6;">
                            <li><strong>Animated Interface:</strong> Colorful gradient backgrounds with smooth animations</li>
                            <li><strong>Batch Prompts:</strong> Copy all standardized prompts at once</li>
                            <li><strong>Quality Control:</strong> Auto-flagging below 85% confidence</li>
                            <li><strong>Progress Tracking:</strong> Real-time solving statistics</li>
                            <li><strong>Smart Export:</strong> Comprehensive JSON backup with quality metrics</li>
                            <li><strong>Enhanced Prompts:</strong> Optimized for Cambridge IGCSE Physics</li>
                        </ul>
                    </div>
                </div>

                <div class="solver-controls">
                    <button id="launchSolverBtn" class="btn enhanced" onclick="launchHybridSolver()" disabled>
                        🚀 Launch Hybrid Solver
                    </button>
                    <button class="btn secondary" onclick="openClaudeAI()">
                        🌐 Open Claude.ai
                    </button>
                    <button class="btn" onclick="showSolverHelp()">
                        ❓ How to Use
                    </button>
                </div>

                <div id="solverProgress" class="hidden">
                    <h4>Initializing Hybrid Solver</h4>
                    <div class="progress">
                        <div id="solverProgressBar" class="progress-bar" style="width: 0%">0%</div>
                    </div>
                    <p id="solverProgressText">Preparing hybrid interface...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;
        let extractionComplete = false;
        let questionsExtracted = 0;
        let examMetadata = {};
        let currentPaperFolder = null;

        // Review Tab Variables
        let currentImages = [];
        let pendingReplacements = {};

        // Tab switching with auto-loading for review tab
        function showTab(tabName) {
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName + '-tab').classList.add('active');
            document.getElementById(tabName + '-tab-btn').classList.add('active');
            
            // Auto-load images when switching to review tab (if not already loaded)
            if (tabName === 'review' && currentPaperFolder) {
                const galleryDiv = document.getElementById('imageGallery');
                // Only load if gallery is hidden (not already loaded)
                if (galleryDiv.classList.contains('hidden')) {
                    setTimeout(() => autoLoadImagesForReview(), 500);
                }
            }
        }

        // File selection handler
        document.getElementById('fileInput').addEventListener('change', function(e) {
            selectedFile = e.target.files[0];
            
            if (selectedFile) {
                const fileInfo = document.getElementById('file-info');
                const fileDetails = document.getElementById('file-details');
                const uploadArea = document.getElementById('upload-area');
                
                fileDetails.innerHTML = `
                    <p><strong>Name:</strong> ${selectedFile.name}</p>
                    <p><strong>Size:</strong> ${(selectedFile.size / (1024*1024)).toFixed(2)} MB</p>
                    <p><strong>Type:</strong> ${selectedFile.type}</p>
                    <p><strong>Last Modified:</strong> ${new Date(selectedFile.lastModified).toLocaleString()}</p>
                `;
                fileInfo.classList.remove('hidden');
                
                uploadArea.classList.add('success');
                uploadArea.innerHTML = `
                    <div style="font-size: 2.5rem; margin-bottom: 1rem; color: #28a745;">✅</div>
                    <h3 style="color: #28a745;">File Ready for Upload</h3>
                    <p style="color: #6c757d; margin-top: 1rem;"><strong>${selectedFile.name}</strong></p>
                    <p style="color: #6c757d; font-size: 14px;">${(selectedFile.size / (1024*1024)).toFixed(2)} MB</p>
                `;
                
                document.getElementById('uploadBtn').disabled = false;
            }
        });

        // Check if paper already exists before upload
        function checkPaperExists() {
            const metadata = {
                exam_type: document.getElementById('examType').value,
                subject: document.getElementById('subject').value,
                year: parseInt(document.getElementById('year').value),
                month: document.getElementById('month').value,
                paper_type: document.getElementById('paperType').value,
                paper_code: document.getElementById('paperCode').value
            };

            return fetch('/api/check-paper-exists', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(metadata)
            })
            .then(response => response.json());
        }

        // Upload file with overwrite warning
        function uploadFile() {
            if (!selectedFile) {
                showAlert('uploadStatus', 'error', 'Please select a PDF file first');
                return;
            }

            // First check if paper exists
            checkPaperExists()
                .then(data => {
                    if (data.exists) {
                        // Show overwrite warning
                        const confirmOverwrite = confirm(
                            `⚠️ PAPER ALREADY EXISTS\\n\\n${data.message}\\n\\nUploading will REPLACE all existing questions for this paper.\\n\\nDo you want to continue?`
                        );
                        
                        if (!confirmOverwrite) {
                            showAlert('uploadStatus', 'warning', '📋 Upload cancelled. Paper was not overwritten.');
                            return;
                        }
                        
                        showAlert('uploadStatus', 'warning', `⚠️ Overwriting existing paper: ${data.paper_name}`);
                    }
                    
                    // Proceed with upload
                    performUpload();
                })
                .catch(error => {
                    console.error('Error checking paper existence:', error);
                    // If check fails, proceed with upload anyway
                    performUpload();
                });
        }

        // Perform the actual upload
        function performUpload() {
            examMetadata = {
                exam_type: document.getElementById('examType').value,
                subject: document.getElementById('subject').value,
                year: parseInt(document.getElementById('year').value),
                month: document.getElementById('month').value,
                paper_type: document.getElementById('paperType').value,
                paper_code: document.getElementById('paperCode').value
            };

            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('metadata', JSON.stringify(examMetadata));

            const uploadBtn = document.getElementById('uploadBtn');
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<span class="spinner"></span>Uploading...';

            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentPaperFolder = data.paper_folder;
                    showAlert('uploadStatus', 'success', `✅ ${examMetadata.exam_type} ${examMetadata.subject} ${examMetadata.year} ${examMetadata.month} Paper ${examMetadata.paper_code} uploaded successfully!<br>📁 Folder: ${data.paper_folder}`);
                    
                    document.getElementById('extract-tab-btn').disabled = false;
                    document.getElementById('extractBtn').disabled = false;
                    
                    setTimeout(() => showTab('extract'), 2000);
                } else {
                    showAlert('uploadStatus', 'error', `❌ Upload failed: ${data.error}`);
                }
            })
            .catch(error => {
                showAlert('uploadStatus', 'error', `❌ Upload error: ${error.message}`);
            })
            .finally(() => {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '📤 Upload PDF';
            });
        }

        // Extract questions
        function extractQuestions() {
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
                { progress: 15, text: "Loading extractor module..." },
                { progress: 30, text: "Analyzing PDF structure..." },
                { progress: 50, text: "Detecting question boundaries..." },
                { progress: 70, text: "Extracting question images..." },
                { progress: 90, text: "Enhancing image quality..." },
                { progress: 100, text: "Finalizing extraction..." }
            ];
            
            let stageIndex = 0;
            const progressInterval = setInterval(() => {
                if (stageIndex < stages.length) {
                    const stage = stages[stageIndex];
                    progress = stage.progress;
                    progressBar.style.width = progress + '%';
                    progressBar.textContent = progress + '%';
                    progressText.textContent = stage.text;
                    stageIndex++;
                } else {
                    clearInterval(progressInterval);
                }
            }, 1000);

            fetch('/api/extract', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                clearInterval(progressInterval);
                progressBar.style.width = '100%';
                progressBar.textContent = '100%';
                
                if (data.success) {
                    questionsExtracted = data.questions_found;
                    currentPaperFolder = data.paper_folder_name;
                    progressText.textContent = `✅ Successfully extracted ${questionsExtracted} questions!`;
                    
                    resultsDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h3>🎉 Extraction Successful!</h3>
                            <div class="results-grid">
                                <div class="result-card">
                                    <h4>📊 Extraction Results</h4>
                                    <p><strong>Questions found:</strong> ${data.questions_found}</p>
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
                    
                } else {
                    progressText.textContent = `❌ Extraction failed`;
                    showAlert('extractStatus', 'error', `Extraction failed: ${data.error}`);
                }
            })
            .catch(error => {
                clearInterval(progressInterval);
                showAlert('extractStatus', 'error', `Extraction error: ${error.message}`);
            })
            .finally(() => {
                extractBtn.disabled = false;
                extractBtn.innerHTML = '⚙️ Extract Questions';
            });
        }

        // Updated workflow functions for correct order
        function enableReviewTab() {
            document.getElementById('review-tab-btn').disabled = false;
            
            // IMPORTANT: Also enable Solve tab after extraction
            enableSolveTab();
            
            // Auto-switch to review tab after extraction
            setTimeout(() => {
                showTab('review');
            }, 3000);
        }

        function enableSolveTab() {
            document.getElementById('solve-tab-btn').disabled = false;
            document.getElementById('launchSolverBtn').disabled = false;
        }

        function enableSolveAfterReview() {
            enableSolveTab();
            showAlert('reviewStatus', 'success', '✅ Review complete! You can now go to the Solve tab to process questions.');
        }

        function enableReviewAndSolve() {
            document.getElementById('review-tab-btn').disabled = false;
            document.getElementById('solve-tab-btn').disabled = false;
            document.getElementById('launchSolverBtn').disabled = false;
        }

        // Hybrid Solver Functions - UPDATED to use /solver/ endpoint
        function launchHybridSolver() {
            if (!currentPaperFolder) {
                showAlert('solveStatus', 'error', 'No paper folder available. Please extract questions first.');
                return;
            }
            
            const progressDiv = document.getElementById('solverProgress');
            progressDiv.classList.remove('hidden');
            
            document.getElementById('solverProgressText').textContent = 'Initializing hybrid solver...';
            document.getElementById('solverProgressBar').style.width = '30%';
            
            // Initialize hybrid solver 
            fetch('/api/ai-solver/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    paper_folder: currentPaperFolder
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('solverProgressBar').style.width = '100%';
                    document.getElementById('solverProgressText').textContent = 
                        `✅ Hybrid solver ready! Found ${data.data.total_questions} questions.`;
                    
                    // Open hybrid solver in new tab using /solver/ endpoint
                    const solverUrl = `/solver/${currentPaperFolder}`;
                    window.open(solverUrl, '_blank', 'width=1600,height=1000');
                    
                    showAlert('solveStatus', 'success', 
                        `🚀 Hybrid AI Solver launched with colorful interface for ${data.data.subject} ${data.data.year} ${data.data.month} Paper ${data.data.paper_code}`);
                    
                    setTimeout(() => {
                        progressDiv.classList.add('hidden');
                    }, 3000);
                } else {
                    showAlert('solveStatus', 'error', `❌ Failed to initialize solver: ${data.error}`);
                    progressDiv.classList.add('hidden');
                }
            })
            .catch(error => {
                showAlert('solveStatus', 'error', `❌ Solver initialization error: ${error.message}`);
                progressDiv.classList.add('hidden');
            });
        }

        function openClaudeAI() {
            window.open('https://claude.ai', '_blank');
        }

        function showSolverHelp() {
            alert(`🤖 Hybrid AI Solver Help

1. 🚀 Launch Hybrid Solver
   • Opens a new tab with colorful animated interface
   • Gen Alpha design with gradient backgrounds
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
   • Export comprehensive JSON backup with quality metrics
   • Compatible with review system

Tips:
• Keep the solver tab open while working
• Process questions in batches for efficiency
• Review flagged solutions carefully
• Enjoy the colorful animated interface!`);
        }

        // Auto-load images when switching to review tab (simplified version)
        function autoLoadImagesForReview() {
            const progressDiv = document.getElementById('reviewProgress');
            const galleryDiv = document.getElementById('imageGallery');
            
            if (!currentPaperFolder) {
                showAlert('reviewStatus', 'error', 'No paper folder available. Please extract questions first.');
                return;
            }
            
            progressDiv.classList.remove('hidden');
            galleryDiv.classList.add('hidden');
            
            document.getElementById('reviewProgressText').textContent = 'Loading extracted images...';
            document.getElementById('reviewProgressBar').style.width = '50%';
            document.getElementById('reviewProgressBar').textContent = '50%';
            
            fetch('/api/review/load-images', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    paper_folder: currentPaperFolder
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentImages = data.images;
                    renderImageGallery(data);
                    
                    document.getElementById('galleryInfo').textContent = 
                        `${data.total_images} questions found in ${data.paper_folder}`;
                    
                    galleryDiv.classList.remove('hidden');
                    document.getElementById('reviewControls').classList.remove('hidden');
                    
                    document.getElementById('reviewProgressBar').style.width = '100%';
                    document.getElementById('reviewProgressBar').textContent = '100%';
                    document.getElementById('reviewProgressText').textContent = 
                        `✅ Successfully loaded ${data.total_images} images for review`;
                    
                    setTimeout(() => {
                        progressDiv.classList.add('hidden');
                    }, 2000);
                } else {
                    showAlert('reviewStatus', 'error', `❌ Failed to load images: ${data.error}`);
                    progressDiv.classList.add('hidden');
                }
            })
            .catch(error => {
                showAlert('reviewStatus', 'error', `❌ Error loading images: ${error.message}`);
                progressDiv.classList.add('hidden');
            });
        }

        // Manual load function (kept for manual refresh if needed)
        function loadImagesForReview() {
            autoLoadImagesForReview();
        }

        function renderImageGallery(data) {
            const gridDiv = document.getElementById('imageGrid');
            gridDiv.innerHTML = '';
            
            data.images.forEach((image, index) => {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'image-review-card';
                cardDiv.id = `image-card-${image.question_number}`;
                
                cardDiv.innerHTML = `
                    <h5>Question ${image.question_number}</h5>
                    <img src="${image.url}" alt="Question ${image.question_number}" 
                         class="image-preview" loading="lazy"
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div style="display: none; padding: 2rem; color: #dc3545;">❌ Image not found</div>
                    
                    <div class="image-info">
                        <div><strong>File:</strong> ${image.filename}</div>
                        <div><strong>Size:</strong> ${image.file_size_mb} MB</div>
                        <div><strong>Dimensions:</strong> ${image.dimensions}</div>
                        <div><strong>Status:</strong> <span class="status-badge status-${image.status}">${image.status}</span></div>
                    </div>
                    
                    <div class="image-actions">
                        <button class="btn btn-small" onclick="toggleReplacement(${image.question_number})">
                            🔄 Replace Image
                        </button>
                        <button class="btn btn-small" onclick="previewFullSize('${image.url}')">
                            🔍 Full Size
                        </button>
                    </div>
                    
                    <div class="upload-replacement" id="upload-${image.question_number}">
                        <div style="margin-bottom: 1rem;">
                            <strong>📤 Upload Replacement Image</strong>
                            <p style="color: #6c757d; font-size: 12px; margin-top: 0.5rem;">
                                Supports PNG, JPG, JPEG (max 10MB)
                            </p>
                        </div>
                        <input type="file" id="file-${image.question_number}" 
                               accept=".png,.jpg,.jpeg" style="display: none;"
                               onchange="handleImageReplacement(${image.question_number}, this)">
                        <div onclick="document.getElementById('file-${image.question_number}').click()" 
                             style="cursor: pointer; padding: 1rem; border: 2px dashed #4facfe; border-radius: 6px;">
                            Click to select replacement image
                        </div>
                        <div style="margin-top: 1rem;">
                            <button class="btn btn-small danger" onclick="toggleReplacement(${image.question_number})">
                                ❌ Cancel
                            </button>
                        </div>
                    </div>
                    
                    <div class="replacement-preview" id="preview-${image.question_number}">
                        <strong>🔍 Replacement Ready</strong>
                        <div id="preview-content-${image.question_number}"></div>
                        <div style="margin-top: 1rem;">
                            <button class="btn btn-small success" onclick="confirmReplacement(${image.question_number})">
                                ✅ Confirm
                            </button>
                            <button class="btn btn-small danger" onclick="cancelReplacement(${image.question_number})">
                                ❌ Cancel
                            </button>
                        </div>
                    </div>
                `;
                
                gridDiv.appendChild(cardDiv);
            });
        }

        // FIXED: Toggle replacement function that properly resets upload div
        function toggleReplacement(questionNumber) {
            const uploadDiv = document.getElementById(`upload-${questionNumber}`);
            const previewDiv = document.getElementById(`preview-${questionNumber}`);
            
            if (uploadDiv.classList.contains('active')) {
                // FIXED: Reset upload div HTML to original state when closing
                uploadDiv.classList.remove('active');
                uploadDiv.innerHTML = `
                    <div style="margin-bottom: 1rem;">
                        <strong>📤 Upload Replacement Image</strong>
                        <p style="color: #6c757d; font-size: 12px; margin-top: 0.5rem;">
                            Supports PNG, JPG, JPEG (max 10MB)
                        </p>
                    </div>
                    <input type="file" id="file-${questionNumber}" 
                           accept=".png,.jpg,.jpeg" style="display: none;"
                           onchange="handleImageReplacement(${questionNumber}, this)">
                    <div onclick="document.getElementById('file-${questionNumber}').click()" 
                         style="cursor: pointer; padding: 1rem; border: 2px dashed #4facfe; border-radius: 6px;">
                        Click to select replacement image
                    </div>
                    <div style="margin-top: 1rem;">
                        <button class="btn btn-small danger" onclick="toggleReplacement(${questionNumber})">
                            ❌ Cancel
                        </button>
                    </div>
                `;
            } else {
                // Hide all other open upload/preview sections
                document.querySelectorAll('.upload-replacement.active, .replacement-preview.active')
                    .forEach(div => div.classList.remove('active'));
                
                uploadDiv.classList.add('active');
                previewDiv.classList.remove('active');
            }
        }

        function handleImageReplacement(questionNumber, fileInput) {
            const file = fileInput.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('question_number', questionNumber);
            
            const originalImage = currentImages.find(img => img.question_number === questionNumber);
            if (originalImage) {
                formData.append('original_filename', originalImage.filename);
            }
            
            const uploadDiv = document.getElementById(`upload-${questionNumber}`);
            const previewDiv = document.getElementById(`preview-${questionNumber}`);
            
            // Show loading
            uploadDiv.innerHTML = '<div style="padding: 2rem;"><span class="spinner"></span>Processing image...</div>';
            
            fetch('/api/review/replace-image', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show preview
                    const previewContent = document.getElementById(`preview-content-${questionNumber}`);
                    previewContent.innerHTML = `
                        <img src="${data.preview_url}" alt="Replacement preview" style="max-width: 100%; max-height: 150px; margin: 0.5rem 0;">
                        <div style="font-size: 12px; color: #6c757d;">
                            <div>Size: ${data.replacement_info.file_size_mb} MB</div>
                            <div>Dimensions: ${data.replacement_info.dimensions}</div>
                        </div>
                    `;
                    
                    uploadDiv.classList.remove('active');
                    previewDiv.classList.add('active');
                    
                    // Mark card as having replacement
                    const card = document.getElementById(`image-card-${questionNumber}`);
                    card.classList.add('has-replacement');
                    
                    pendingReplacements[questionNumber] = data.replacement_info;
                    updatePendingCount();
                    
                    showAlert('reviewStatus', 'success', 
                        `✅ Replacement image staged for Question ${questionNumber}`);
                } else {
                    showAlert('reviewStatus', 'error', `❌ Failed to stage replacement: ${data.error}`);
                    // FIXED: Reset upload div to original state
                    toggleReplacement(questionNumber);
                    toggleReplacement(questionNumber);
                }
            })
            .catch(error => {
                showAlert('reviewStatus', 'error', `❌ Error uploading replacement: ${error.message}`);
                // FIXED: Reset upload div to original state
                toggleReplacement(questionNumber);
                toggleReplacement(questionNumber);
            });
        }

        function confirmReplacement(questionNumber) {
            const previewDiv = document.getElementById(`preview-${questionNumber}`);
            previewDiv.classList.remove('active');
            
            showAlert('reviewStatus', 'info', 
                `Replacement for Question ${questionNumber} confirmed. Click "Update All Changes" to apply.`);
        }

        function cancelReplacement(questionNumber) {
            const card = document.getElementById(`image-card-${questionNumber}`);
            const previewDiv = document.getElementById(`preview-${questionNumber}`);
            
            card.classList.remove('has-replacement');
            previewDiv.classList.remove('active');
            
            delete pendingReplacements[questionNumber];
            updatePendingCount();
            
            showAlert('reviewStatus', 'info', `Replacement for Question ${questionNumber} cancelled`);
        }

        function updatePendingCount() {
            const count = Object.keys(pendingReplacements).length;
            const countSpan = document.getElementById('pendingCount');
            const updateBtn = document.getElementById('updateAllBtn');
            const resetBtn = document.getElementById('resetReplacementsBtn');
            
            if (count > 0) {
                countSpan.textContent = `${count} pending replacement${count > 1 ? 's' : ''}`;
                countSpan.style.display = 'inline';
                updateBtn.disabled = false;
                resetBtn.disabled = false;
            } else {
                countSpan.style.display = 'none';
                updateBtn.disabled = true;
                resetBtn.disabled = true;
            }
        }

        function updateAllImages() {
            const updateBtn = document.getElementById('updateAllBtn');
            const count = Object.keys(pendingReplacements).length;
            
            if (count === 0) {
                showAlert('reviewStatus', 'warning', 'No pending replacements to apply');
                return;
            }
            
            const confirmUpdate = confirm(
                `Apply ${count} image replacement${count > 1 ? 's' : ''}?\\n\\nThis will permanently replace the original images.\\nBackups will be created automatically.\\n\\nContinue?`
            );
            
            if (!confirmUpdate) return;
            
            updateBtn.disabled = true;
            updateBtn.innerHTML = '<span class="spinner"></span>Updating Images...';
            
            fetch('/api/review/update-all-images', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Clear all replacement indicators
                    document.querySelectorAll('.image-review-card').forEach(card => {
                        card.classList.remove('has-replacement');
                    });
                    document.querySelectorAll('.replacement-preview.active').forEach(preview => {
                        preview.classList.remove('active');
                    });
                    
                    pendingReplacements = {};
                    updatePendingCount();
                    
                    showAlert('reviewStatus', 'success', 
                        `Successfully updated ${data.applied_count} images! Backups saved to: backup_images folder`);
                    
                    // Enable solve tab after successful review completion
                    enableSolveAfterReview();
                    
                    // Force image refresh
                    setTimeout(() => {
                        forceReloadImages();
                    }, 1000);
                } else {
                    showAlert('reviewStatus', 'error', `Failed to update images: ${data.error}`);
                }
            })
            .catch(error => {
                showAlert('reviewStatus', 'error', `Error updating images: ${error.message}`);
            })
            .finally(() => {
                updateBtn.disabled = false;
                updateBtn.innerHTML = 'Update All Changes';
            });
        }

        function forceReloadImages() {
            fetch('/api/review/load-images', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    paper_folder: currentPaperFolder
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentImages = data.images;
                    
                    // Update all image sources with fresh URLs
                    data.images.forEach((image, index) => {
                        const imgElement = document.querySelector(`#image-card-${image.question_number} .image-preview`);
                        if (imgElement) {
                            const uniqueTimestamp = Date.now() + Math.random() * 1000 + index;
                            const newSrc = image.url + `?nocache=${uniqueTimestamp}`;
                            imgElement.src = newSrc;
                        }
                    });
                    
                    showAlert('reviewStatus', 'success', 
                        `Images refreshed successfully! Updated images should now be visible.`);
                }
            })
            .catch(error => {
                console.error('Error in forceReloadImages:', error);
            });
        }

        function resetReplacements() {
            const count = Object.keys(pendingReplacements).length;
            
            if (count === 0) {
                showAlert('reviewStatus', 'warning', 'No pending replacements to reset');
                return;
            }
            
            const confirmReset = confirm(
                `Reset ${count} pending replacement${count > 1 ? 's' : ''}?\\n\\nAll staged replacements will be discarded.`
            );
            
            if (!confirmReset) return;
            
            fetch('/api/review/reset-replacements', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Clear all replacement indicators
                    document.querySelectorAll('.image-review-card').forEach(card => {
                        card.classList.remove('has-replacement');
                    });
                    document.querySelectorAll('.replacement-preview.active, .upload-replacement.active').forEach(div => {
                        div.classList.remove('active');
                    });
                    
                    pendingReplacements = {};
                    updatePendingCount();
                    
                    showAlert('reviewStatus', 'success', 
                        `Reset ${data.cleared_count} pending replacements`);
                } else {
                    showAlert('reviewStatus', 'error', `Failed to reset: ${data.error}`);
                }
            })
            .catch(error => {
                showAlert('reviewStatus', 'error', `Error resetting: ${error.message}`);
            });
        }

        function previewFullSize(imageUrl) {
            window.open(imageUrl, '_blank');
        }

        function goToSolve() {
            const confirmGo = confirm(
                `Go to Solve Tab?\\n\\nThis will:\\n• Keep current images as-is\\n• Enable the Solve tab\\n• Switch to Solve tab\\n\\nContinue?`
            );
            
            if (confirmGo) {
                enableSolveTab();
                showTab('solve');
                showAlert('reviewStatus', 'info', 
                    'Moved to Solve tab. Images ready for processing. You can return to Review anytime.');
            }
        }

        // Utility function to show alerts
        function showAlert(containerId, type, message) {
            const container = document.getElementById(containerId);
            container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            
            if (type === 'success' || type === 'info') {
                setTimeout(() => {
                    if (container.innerHTML.includes(message.substring(0, 50))) {
                        container.innerHTML = '';
                    }
                }, 10000);
            }
        }

        // Drag and drop support
        const uploadArea = document.getElementById('upload-area');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            uploadArea.style.background = '#e3f2fd';
            uploadArea.style.borderColor = '#2196F3';
        }

        function unhighlight(e) {
            uploadArea.style.background = selectedFile ? '#f0fff0' : '#f8f9ff';
            uploadArea.style.borderColor = selectedFile ? '#28a745' : '#4facfe';
        }

        uploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                const file = files[0];
                if (file.type === 'application/pdf') {
                    selectedFile = file;
                    document.getElementById('fileInput').files = files;
                    const event = new Event('change', { bubbles: true });
                    document.getElementById('fileInput').dispatchEvent(event);
                } else {
                    showAlert('uploadStatus', 'error', 'Please drop a PDF file only.');
                }
            }
        }

        // Check initial status
        window.addEventListener('load', function() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    if (data.question_banks && data.question_banks.length > 0) {
                        const lastBank = data.question_banks[data.question_banks.length - 1];
                        if (lastBank.has_questions) {
                            questionsExtracted = lastBank.image_count;
                            extractionComplete = true;
                            currentPaperFolder = lastBank.folder_name;
                            
                            document.getElementById('extract-tab-btn').disabled = false;
                            enableReviewAndSolve();
                            
                            showAlert('uploadStatus', 'info', `Found existing question bank: ${lastBank.folder_name} with ${lastBank.image_count} questions. Both Review and Solve tabs are now available!`);
                        }
                    }
                })
                .catch(error => {
                    console.error('Status check failed:', error);
                });
        });
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
    """Get current system status with question bank overview"""
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
                    # Check with standardized folder priority
                    images_folder = paper_folder / "images"
                    extracted_images_folder = paper_folder / "extracted_images"
                    metadata_file = paper_folder / "metadata.json"
                    
                    # Count images with correct priority
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
        
        # Check current paper status
        if CURRENT_PAPER_FOLDER and CURRENT_PAPER_FOLDER.exists():
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
        print(f"Status check error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "extractor_available": module_manager.module_status['extractor']['available']
        }), 500

@app.route('/api/check-paper-exists', methods=['POST'])
def check_paper_exists():
    """Check if a paper already exists before upload"""
    try:
        data = request.get_json()
        
        subject = data.get('subject', 'physics').lower()
        year = data.get('year', 2024)
        month = data.get('month', 'Mar').lower()
        paper_code = data.get('paper_code', '13')
        
        paper_folder_name = f"{subject}_{year}_{month}_{paper_code}"
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder_name
        
        if paper_folder_path.exists():
            images_folder = paper_folder_path / "images"
            extracted_images_folder = paper_folder_path / "extracted_images"
            question_count = 0
            
            if images_folder.exists():
                image_files = list(images_folder.glob("question_*_enhanced.png"))
                question_count = len(image_files)
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
        print(f"Error checking paper existence: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload with metadata storage and folder structure"""
    global CURRENT_FILE_PATH, CURRENT_EXAM_METADATA, CURRENT_PAPER_FOLDER
    
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        if file.filename == '' or not file.filename.lower().endswith('.pdf'):
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
                exam_metadata.update(json.loads(metadata_str))
            except Exception as e:
                print(f"WARNING: Failed to parse metadata: {e}")
        
        CURRENT_EXAM_METADATA = exam_metadata
        
        # Check file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            return jsonify({"success": False, "error": "File too large. Maximum size is 50MB"}), 400
        
        # Create paper-specific folder structure
        subject = exam_metadata.get('subject', 'physics').lower()
        year = exam_metadata.get('year', 2024)
        month = exam_metadata.get('month', 'Mar').lower()
        paper_code = exam_metadata.get('paper_code', '13')
        
        paper_folder_name = f"{subject}_{year}_{month}_{paper_code}"
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder_name
        paper_folder_path.mkdir(parents=True, exist_ok=True)
        
        CURRENT_PAPER_FOLDER = paper_folder_path
        
        # Save file with structured naming
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{paper_folder_name}_{timestamp}.pdf"
        file_path = UPLOAD_FOLDER / safe_filename
        
        # Save file
        file.save(str(file_path))
        
        # Copy to expected location for extractor
        expected_path = BASE_DIR / "current_exam.pdf"
        shutil.copy2(file_path, expected_path)
        CURRENT_FILE_PATH = expected_path
        
        # Save metadata in paper folder
        metadata_path = paper_folder_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(exam_metadata, f, indent=2)
        
        # Also save in backend directory for extractor compatibility
        base_metadata_path = BASE_DIR / "current_exam_metadata.json"
        with open(base_metadata_path, 'w') as f:
            json.dump(exam_metadata, f, indent=2)
        
        print(f"PDF uploaded successfully")
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
        print(f"Upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def extract_questions():
    """Extract questions using direct call to extractor.py"""
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
        
        result = module_manager.run_extractor(current_file, CURRENT_EXAM_METADATA)
        
        if not result["success"]:
            return jsonify(result), 500
        
        CURRENT_PAPER_FOLDER = Path(result["paper_folder"])
        review_manager.set_current_paper_folder(result["paper_folder_name"])
        
        if current_file.exists():
            current_file.unlink()
        
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
        print(f"Extraction error: {e}")
        return jsonify({
            "success": False,
            "error": f"Extraction failed: {str(e)}"
        }), 500

@app.route('/images/<paper_folder>/<filename>')
def serve_paper_image(paper_folder, filename):
    """Serve images from paper-specific folders"""
    try:
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        
        # Try images folder FIRST
        images_dir = paper_folder_path / "images"
        if images_dir.exists():
            image_path = images_dir / filename
            if image_path.exists():
                return create_cache_busted_response(image_path)
        
        # Fallback to extracted_images folder
        extracted_images_dir = paper_folder_path / "extracted_images"
        if extracted_images_dir.exists():
            image_path = extracted_images_dir / filename
            if image_path.exists():
                return create_cache_busted_response(image_path)
        
        return f"Image not found: {filename} in {paper_folder}", 404
            
    except Exception as e:
        return "Image serving error", 500

@app.route('/images/<paper_folder>/extracted_images/<filename>')
def serve_extracted_image(paper_folder, filename):
    """Serve images from extracted_images folder"""
    try:
        extracted_images_dir = QUESTION_BANKS_DIR / paper_folder / "extracted_images"
        if not extracted_images_dir.exists():
            return f"Extracted images folder not found: {paper_folder}", 404
            
        image_path = extracted_images_dir / filename
        if not image_path.exists():
            return f"Image not found: {filename}", 404
            
        return create_cache_busted_response(image_path)
        
    except Exception as e:
        return "Image serving error", 500

@app.route('/images/<paper_folder>/temp_replacements/<filename>')
def serve_temp_replacement_image(paper_folder, filename):
    """Serve temporary replacement images"""
    try:
        temp_images_dir = QUESTION_BANKS_DIR / paper_folder / "temp_replacements"
        if not temp_images_dir.exists():
            return f"Temp folder not found: {paper_folder}", 404
            
        image_path = temp_images_dir / filename
        if not image_path.exists():
            return f"Temp image not found: {filename}", 404
            
        return create_cache_busted_response(image_path)
        
    except Exception as e:
        return "Image serving error", 500

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve extracted question images (backward compatibility)"""
    try:
        # Try current paper folder first
        if CURRENT_PAPER_FOLDER and CURRENT_PAPER_FOLDER.exists():
            images_folder = CURRENT_PAPER_FOLDER / "images"
            if images_folder.exists():
                image_path = images_folder / filename
                if image_path.exists():
                    return create_cache_busted_response(image_path)
            
            extracted_images_folder = CURRENT_PAPER_FOLDER / "extracted_images"
            if extracted_images_folder.exists():
                image_path = extracted_images_folder / filename
                if image_path.exists():
                    return create_cache_busted_response(image_path)
        
        # Fallback to old extracted_images directory
        extracted_images_dir = BASE_DIR / "extracted_images"
        if extracted_images_dir.exists():
            image_path = extracted_images_dir / filename
            if image_path.exists():
                return create_cache_busted_response(image_path)
        
        return f"Image not found: {filename}", 404
            
    except Exception as e:
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
        
        json_files = list(CURRENT_PAPER_FOLDER.glob("*.json"))
        export_files = [f for f in json_files if f.name != "metadata.json"]
        
        if export_files:
            latest_export = max(export_files, key=lambda f: f.stat().st_mtime)
            return send_file(latest_export, as_attachment=True)
        else:
            return jsonify({
                "success": False,
                "error": "No export files found. Please solve questions first using the Hybrid AI Solver."
            }), 404
            
    except Exception as e:
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
    print("Starting AI Tutor - Complete Workflow with Hybrid Solver...")
    print("=" * 70)
    print(f"Backend directory: {BASE_DIR}")
    print(f"Tutor App root: {TUTOR_APP_ROOT}")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Question banks (shared): {QUESTION_BANKS_DIR}")
    print(f"Extractor available: {'Yes' if module_manager.module_status['extractor']['available'] else 'No'}")
    print(f"Review System: Integrated")
    print(f"Hybrid Solver: Integrated with Gen Alpha interface")
    print(f"Web interface: http://localhost:5004")
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