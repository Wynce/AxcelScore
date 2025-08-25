#!/usr/bin/env python3
"""
Static Routes for AI Tutor
Handles image serving and static file routes
"""

from flask import Blueprint, abort
from pathlib import Path
from config import BASE_DIR, QUESTION_BANKS_DIR, get_app_state
from utils import create_cache_busted_response

# Create blueprint for static routes
static_bp = Blueprint('static', __name__)

@static_bp.route('/images/<paper_folder>/<filename>')
def serve_paper_image(paper_folder, filename):
    """Serve images from paper-specific folders with aggressive cache-busting"""
    try:
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        
        # Try extracted_images folder first (your current structure)
        extracted_images_dir = paper_folder_path / "extracted_images"
        if extracted_images_dir.exists():
            image_path = extracted_images_dir / filename
            if image_path.exists():
                print(f"🖼️ Serving image: {image_path} (extracted_images)")
                return create_cache_busted_response(image_path)
        
        # Fallback to images folder
        images_dir = paper_folder_path / "images"
        if images_dir.exists():
            image_path = images_dir / filename
            if image_path.exists():
                print(f"🖼️ Serving image: {image_path} (images)")
                return create_cache_busted_response(image_path)
        
        print(f"❌ Image not found: {filename} in {paper_folder}")
        return f"Image not found: {filename} in {paper_folder}", 404
            
    except Exception as e:
        print(f"❌ Error serving paper image {paper_folder}/{filename}: {e}")
        return "Image serving error", 500

@static_bp.route('/images/<paper_folder>/extracted_images/<filename>')
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

@static_bp.route('/images/<paper_folder>/temp_replacements/<filename>')
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

@static_bp.route('/images/<filename>')
def serve_image(filename):
    """Serve extracted question images with aggressive cache-busting (backward compatibility)"""
    try:
        app_state = get_app_state()
        
        # Try current paper folder first
        if app_state.current_paper_folder and app_state.current_paper_folder.exists():
            # Check extracted_images folder first
            extracted_images_folder = app_state.current_paper_folder / "extracted_images"
            if extracted_images_folder.exists():
                image_path = extracted_images_folder / filename
                if image_path.exists():
                    print(f"🖼️ Serving image (current/extracted): {image_path}")
                    return create_cache_busted_response(image_path)
            
            # Then check images folder
            images_folder = app_state.current_paper_folder / "images"
            if images_folder.exists():
                image_path = images_folder / filename
                if image_path.exists():
                    print(f"🖼️ Serving image (current/images): {image_path}")
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

@static_bp.route('/ai-solver/<paper_folder>')
def serve_ai_solver_interface(paper_folder):
    """Serve the AI solver interface HTML"""
    try:
        from ai_solver_manager import SimpleAISolverManager
        
        paper_folder_path = QUESTION_BANKS_DIR / paper_folder
        interface_path = paper_folder_path / "ai_solver_interface.html"
        
        if not interface_path.exists():
            # Generate interface if it doesn't exist
            ai_solver_manager = SimpleAISolverManager()
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