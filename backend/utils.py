#!/usr/bin/env python3
"""
Utility functions for AI Tutor
Contains helper functions for file operations, caching, etc.
"""

import hashlib
import time
import os
from datetime import datetime
from flask import make_response, send_file
from pathlib import Path

def get_file_hash(file_path):
    """Generate hash of file contents for ETag"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    except:
        return str(int(time.time()))

def create_cache_busted_response(file_path, mimetype="image/png"):
    """Create a response with aggressive cache-busting headers"""
    try:
        # Get file modification time and hash
        file_mtime = os.path.getmtime(file_path)
        file_hash = get_file_hash(file_path)
        
        response = make_response(send_file(str(file_path), mimetype=mimetype))
        
        # Aggressive cache-busting headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, s-maxage=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Last-Modified'] = datetime.fromtimestamp(file_mtime).strftime('%a, %d %b %Y %H:%M:%S GMT')
        response.headers['ETag'] = f'"{file_hash}-{int(file_mtime)}"'
        
        # Additional headers to prevent caching
        response.headers['Vary'] = '*'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Accel-Expires'] = '0'
        
        print(f"🖼️ Serving with cache-bust: {file_path} (mtime: {file_mtime}, hash: {file_hash[:8]})")
        return response
    except Exception as e:
        print(f"❌ Error creating cache-busted response: {e}")
        from flask import abort
        abort(404)

def generate_paper_folder_name(metadata):
    """Generate standardized paper folder name from metadata"""
    subject = metadata.get('subject', 'physics').lower()
    year = metadata.get('year', 2024)
    month = metadata.get('month', 'Mar').lower()
    paper_code = metadata.get('paper_code', '13')
    
    return f"{subject}_{year}_{month}_{paper_code}"

def get_image_count(paper_folder_path):
    """Count images in paper folder (checks both images and extracted_images)"""
    paper_path = Path(paper_folder_path)
    
    # Check extracted_images folder first
    extracted_images_folder = paper_path / "extracted_images"
    if extracted_images_folder.exists():
        image_files = list(extracted_images_folder.glob("question_*_enhanced.png"))
        return len(image_files)
    
    # Fallback to images folder
    images_folder = paper_path / "images"
    if images_folder.exists():
        image_files = list(images_folder.glob("question_*_enhanced.png"))
        return len(image_files)
    
    return 0

def extract_question_number(filename):
    """Extract question number from filename"""
    import re
    match = re.search(r'question_(\d+)_enhanced\.png', filename)
    return int(match.group(1)) if match else 0

def validate_pdf_file(file):
    """Validate uploaded PDF file"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    if not file.filename.lower().endswith('.pdf'):
        return False, "Please upload a valid PDF file"
    
    # Check file size
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 50 * 1024 * 1024:  # 50MB
        return False, "File too large. Maximum size is 50MB"
    
    return True, "Valid PDF file"

def create_safe_filename(original_filename, metadata):
    """Create a safe filename for uploaded files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    paper_folder_name = generate_paper_folder_name(metadata)
    return f"{paper_folder_name}_{timestamp}.pdf"