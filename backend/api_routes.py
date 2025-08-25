#!/usr/bin/env python3
"""
API Routes for AI Tutor
Contains all API endpoint handlers
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from config import BASE_DIR, UPLOAD_FOLDER, QUESTION_BANKS_DIR, get_app_state
from utils import (
    validate_pdf_file, create_safe_filename, generate_paper_folder_name,
    get_image_count
)

# Create blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/status')
def get_status():
    """Get current system status with question bank overview"""
    try:
        from module_manager import ModuleManager
        
        # Initialize module manager for status check
        module_manager = ModuleManager()
        app_state = get_app_state()
        
        status_data = {
            "extractor_available": module_manager.module_status['extractor']['available'],
            "backend_directory": str(BASE_DIR),
            "upload_folder": str(UPLOAD_FOLDER),
            "question_banks_dir": str(QUESTION_BANKS_DIR),
            "current_file_exists": (BASE_DIR / "current_exam.pdf").exists(),
            "question_banks": [],
            "current_paper": None,
            "status": "ready"
        }
        
        # Check for existing question banks
        if QUESTION_BANKS_DIR.exists():
            for paper_folder in QUESTION_BANKS_DIR.iterdir():
                if paper_folder.is_dir():
                    image_count = get_image_count(paper_folder)
                    
                    # Read metadata
                    metadata_file = paper_folder / "metadata.json"
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
        if app_state.current_paper_folder and app_state.current_paper_folder.exists():
            image_count = get_image_count(app_state.current_paper_folder)
            
            if image_count > 0:
                status_data["current_paper"] = {
                    "folder_name": app_state.current_paper_folder.name,
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
            "extractor_available": False
        }), 500

@api_bp.route('/check-paper-exists', methods=['POST'])
def check_paper_exists():
    """Check if a paper already exists before upload"""
    try:
        data = request.get_json()
        
        paper_folder_name = generate_paper_folder_name(data)
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder_name
        
        if paper_folder_path.exists():
            question_count = get_image_count(paper_folder_path)
            
            return jsonify({
                "exists": True,
                "paper_name": paper_folder_name,
                "folder_path": str(paper_folder_path),
                "existing_questions": question_count,
                "message": f"{data.get('exam_type', 'Cambridge')} {data.get('subject', 'Physics').title()} {data.get('year', 2024)} {data.get('month', 'Mar').title()} Paper {data.get('paper_code', '13')} already exists with {question_count} questions."
            })
        else:
            return jsonify({
                "exists": False,
                "paper_name": paper_folder_name
            })
            
    except Exception as e:
        print(f"❌ Error checking paper existence: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload with metadata storage and folder structure"""
    try:
        print("📁 DEBUG: Upload endpoint called")
        
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        
        file = request.files['file']
        print(f"📁 DEBUG: File received: {file.filename}")
        
        # Validate file
        is_valid, error_message = validate_pdf_file(file)
        if not is_valid:
            return jsonify({"success": False, "error": error_message}), 400
        
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
                print(f"⚠️ WARNING: Failed to parse metadata: {e}")
        
        # Update app state
        app_state = get_app_state()
        app_state.update_exam_metadata(exam_metadata)
        
        # Create paper-specific folder structure
        paper_folder_name = generate_paper_folder_name(exam_metadata)
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder_name
        paper_folder_path.mkdir(parents=True, exist_ok=True)
        
        app_state.set_paper_folder(paper_folder_path)
        
        # Save file with structured naming
        safe_filename = create_safe_filename(file.filename, exam_metadata)
        file_path = UPLOAD_FOLDER / safe_filename
        
        # Save file
        file.save(str(file_path))
        
        # Copy to expected location for extractor
        expected_path = BASE_DIR / "current_exam.pdf"
        shutil.copy2(file_path, expected_path)
        app_state.current_file_path = expected_path
        
        # Save metadata in paper folder
        metadata_path = paper_folder_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(exam_metadata, f, indent=2)
        
        # Also save in backend directory for extractor compatibility
        base_metadata_path = BASE_DIR / "current_exam_metadata.json"
        with open(base_metadata_path, 'w') as f:
            json.dump(exam_metadata, f, indent=2)
        
        file_size = file_path.stat().st_size
        
        print(f"✅ PDF uploaded successfully: {paper_folder_name}")
        
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

@api_bp.route('/extract', methods=['POST'])
def extract_questions():
    """Extract questions using direct call to extractor.py"""
    try:
        from module_manager import ModuleManager
        
        app_state = get_app_state()
        current_file = BASE_DIR / "current_exam.pdf"
        
        if not current_file.exists():
            return jsonify({
                "success": False,
                "error": "No PDF file found. Please upload a file first."
            }), 400
        
        if not app_state.current_exam_metadata:
            return jsonify({
                "success": False,
                "error": "No exam metadata found. Please upload a file first."
            }), 400
        
        print(f"🚀 Starting extraction with shared question_banks structure")
        
        # Initialize and use module manager
        module_manager = ModuleManager()
        result = module_manager.run_extractor(current_file, app_state.current_exam_metadata)
        
        if not result["success"]:
            return jsonify(result), 500
        
        # Update app state
        app_state.set_paper_folder(result["paper_folder"])
        
        # Clean up uploaded file
        if current_file.exists():
            current_file.unlink()
        
        print(f"✅ Extraction completed: {result['questions_found']} questions extracted")
        
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

@api_bp.route('/ai-solver/initialize', methods=['POST'])
def initialize_ai_solver():
    """Initialize AI Solver - RETURNS JSON"""
    try:
        from ai_solver_manager import SimpleAISolverManager
        
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
        ai_solver_manager = SimpleAISolverManager()
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

@api_bp.route('/export-results')
def export_results():
    """Export results as JSON file"""
    try:
        app_state = get_app_state()
        
        if not app_state.current_paper_folder or not app_state.current_paper_folder.exists():
            return jsonify({
                "success": False,
                "error": "No current paper folder available"
            }), 400
        
        # Look for existing JSON exports in the paper folder
        json_files = list(app_state.current_paper_folder.glob("*.json"))
        
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