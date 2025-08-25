#!/usr/bin/env python3
"""
Module Manager for handling extractor.py integration
Manages extractor module loading and execution
"""

import sys
import shutil
from pathlib import Path
from config import BASE_DIR, QUESTION_BANKS_DIR
from utils import generate_paper_folder_name

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
            Path.cwd() / "extractor.py"
        ]
        
        for path in extractor_paths:
            if path.exists():
                self.module_status['extractor']['available'] = True
                self.module_status['extractor']['path'] = path
                break
                
        print(f"🔧 Extractor available: {'✅ Yes' if self.module_status['extractor']['available'] else '❌ No'}")
    
    def run_extractor(self, pdf_path, exam_metadata):
        """Run extractor.py directly with proper folder structure - FIXED VERSION"""
        if not self.module_status['extractor']['available']:
            raise Exception("Extractor module not found")
        
        try:
            # Create paper-specific folder
            paper_folder_name = generate_paper_folder_name(exam_metadata)
            paper_folder_path = QUESTION_BANKS_DIR / paper_folder_name
            paper_folder_path.mkdir(parents=True, exist_ok=True)
            
            # Create images subdirectory
            images_folder = paper_folder_path / "images"
            images_folder.mkdir(exist_ok=True)
            
            print(f"DEBUG: Paper folder: {paper_folder_path}")
            print(f"DEBUG: Images folder: {images_folder}")
            
            # Import your extractor directly (no subprocess needed)
            extractor_parent = self.module_status['extractor']['path'].parent
            if str(extractor_parent) not in sys.path:
                sys.path.insert(0, str(extractor_parent))
            
            print("DEBUG: Importing FixedPDFExtractor...")
            from extractor import FixedPDFExtractor
            print("DEBUG: FixedPDFExtractor imported successfully")
            
            # Copy PDF to paper folder
            pdf_dest = paper_folder_path / "exam.pdf"
            print(f"DEBUG: Copying PDF from {pdf_path} to {pdf_dest}")
            shutil.copy2(pdf_path, pdf_dest)
            
            # Initialize extractor with paper folder as base_dir
            print("DEBUG: Initializing FixedPDFExtractor...")
            extractor = FixedPDFExtractor(base_dir=str(paper_folder_path))
            print("DEBUG: FixedPDFExtractor initialized successfully")
            
            # Run extraction using your exact method
            print("DEBUG: Starting extraction using extract_for_html_interface...")
            result = extractor.extract_for_html_interface(
                pdf_filename="exam.pdf",
                subject=exam_metadata.get('subject', 'physics'),
                year=str(exam_metadata.get('year', 2024)),
                month=exam_metadata.get('month', 'Mar'),
                paper_code=exam_metadata.get('paper_code', '13')
            )
            
            print(f"DEBUG: Extraction completed with result: {result}")
            
            if result:
                # Count the extracted images (check both folders)
                image_files = []
                
                # Check extracted_images folder first (your current structure)
                extracted_images_folder = paper_folder_path / "extracted_images"
                if extracted_images_folder.exists():
                    image_files.extend(list(extracted_images_folder.glob("question_*_enhanced.png")))
                
                # Also check images folder as fallback
                if not image_files and images_folder.exists():
                    image_files.extend(list(images_folder.glob("question_*_enhanced.png")))
                
                question_count = len(image_files)
                
                print(f"SUCCESS: {question_count} questions extracted to {paper_folder_name}")
                print(f"FOLDER: {paper_folder_path}")
                
                if image_files:
                    sample_images = [img.name for img in image_files[:3]]
                    print(f"IMAGES: {sample_images}")
                
                return {
                    "success": True,
                    "questions_found": question_count,
                    "paper_folder": str(paper_folder_path),
                    "paper_folder_name": paper_folder_name,
                    "images_folder": str(images_folder)
                }
            else:
                error_msg = "Extractor returned None/False - no questions found"
                print(f"ERROR: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Extraction error: {str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": error_msg}

    def cleanup(self):
        """Clean up any subprocess on exit"""
        for process in self.processes.values():
            if process and process.poll() is None:
                process.terminate()