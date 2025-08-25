#!/usr/bin/env python3
"""
Enhanced PDF Question Extractor with Web Interface - COMPLETE FIXED VERSION
Preserves ALL existing functionality + Fixes web interface + Standardizes folder structure
"""

import fitz  # PyMuPDF
import json
import re
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageEnhance
import shutil
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Web interface imports (only imported when running as web server)
WEB_MODE = False
try:
    from flask import Flask, request, jsonify, render_template_string, redirect, url_for, send_file
    from flask_cors import CORS
    import tempfile
    import traceback
    WEB_MODE = True
    logger.info("Flask imported successfully - Web mode available")
except ImportError:
    logger.warning("Flask not installed - running in CLI mode only")
    print("💡 Flask not installed - running in CLI mode only")
    print("   To enable web interface: pip install flask flask-cors")

class EnhancedPDFExtractor:
    """
    Enhanced PDF Extractor - All existing functionality preserved + Web interface + Fixes applied
    
    Key Features:
    - Multi-strategy question boundary detection
    - High-quality image extraction with enhancement
    - Standardized folder structure (using 'images' as primary)
    - Web interface compatibility
    - Dynamic exam parameter handling
    - Comprehensive error handling and logging
    """
    
    def __init__(self, base_dir="/Users/wynceaxcel/Apps/axcelscore/pdf-extraction-test"):
        self.base_dir = Path(base_dir)
        # STANDARDIZED: Use 'images' as primary folder name (not 'extracted_images')
        self.images_dir = self.base_dir / "images"
        self.react_app_path = Path("/Users/wynceaxcel/Apps/axcelscore")
        self.backend_dir = Path("/Users/wynceaxcel/Apps/axcelscore/backend")
        
        # Initialize directories
        self._setup_directories()
        
        # Question boundaries storage
        self.question_boundaries = {}
        
        # Enhanced configuration
        self.max_questions = 50
        self.image_quality = 2.0  # Zoom factor for image rendering
        self.enhancement_factor = 1.05  # Image enhancement factor
        
        # Logging setup
        logger.info("🎯 Enhanced PDF Question Extractor initialized")
        logger.info(f"📂 Base directory: {self.base_dir}")
        logger.info(f"🖼️ Images directory: {self.images_dir}")
        logger.info("✅ Ready for extraction")
    
    def _setup_directories(self):
        """Setup and clean directories"""
        try:
            # Clean up existing images directory
            if self.images_dir.exists():
                shutil.rmtree(self.images_dir)
                logger.info(f"🧹 Cleaned existing images directory: {self.images_dir}")
            
            # Create fresh directories
            self.images_dir.mkdir(parents=True, exist_ok=True)
            self.base_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"📁 Created directories successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup directories: {e}")
            raise
    
    def find_enhanced_question_boundaries(self, pdf_path):
        """
        Enhanced boundary detection using multiple strategies
        Preserves all existing detection logic with improvements
        """
        logger.info("🔍 Starting enhanced question boundary detection")
        
        try:
            pdf_doc = fitz.open(pdf_path)
            all_text_elements = []
            
            # Collect all text elements with detailed positioning
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                text_dict = page.get_text("dict")
                
                for block in text_dict["blocks"]:
                    if "lines" not in block:
                        continue
                        
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                element = {
                                    "text": text,
                                    "bbox": span["bbox"],
                                    "page": page_num + 1,
                                    "font_size": span["size"],
                                    "x": span["bbox"][0],
                                    "y": span["bbox"][1],
                                    "width": span["bbox"][2] - span["bbox"][0],
                                    "height": span["bbox"][3] - span["bbox"][1],
                                    "at_left_margin": span["bbox"][0] < 100,
                                    "near_left": span["bbox"][0] < 150,
                                    "is_bold": "Bold" in span.get("font", "").lower() or "bold" in span.get("font", "").lower(),
                                    "line_start": len([s for s in line["spans"] if s == span]) == 0,
                                    "font_name": span.get("font", "")
                                }
                                all_text_elements.append(element)
            
            # Enhanced question detection with multiple strategies
            question_starts = self._detect_question_starts_multi_strategy(all_text_elements)
            self._calculate_smart_boundaries(question_starts, all_text_elements, pdf_doc)
            
            pdf_doc.close()
            
            detected_count = len(self.question_boundaries)
            logger.info(f"📊 Detected {detected_count} question boundaries")
            
            return detected_count
            
        except Exception as e:
            logger.error(f"Boundary detection failed: {e}")
            raise
    
    def _detect_question_starts_multi_strategy(self, text_elements):
        """
        Multi-strategy question start detection
        Preserves all existing strategies + adds new ones
        """
        question_starts = []
        found_numbers = set()
        
        logger.info("🔍 Applying multiple detection strategies")
        
        strategies = [
            ("standalone_number", self._strategy_standalone_number, 0.9),
            ("number_with_text", self._strategy_number_with_text, 0.85),
            ("bold_number", self._strategy_bold_number, 0.8),
            ("two_digit_number", self._strategy_two_digit_number, 0.85),
            ("number_with_dot", self._strategy_number_with_dot, 0.75),
            ("number_with_parenthesis", self._strategy_number_with_parenthesis, 0.7),
            ("large_font_number", self._strategy_large_font_number, 0.8)
        ]
        
        for strategy_name, strategy_func, base_confidence in strategies:
            strategy_results = strategy_func(text_elements, found_numbers)
            
            for result in strategy_results:
                result["strategy"] = strategy_name
                result["confidence"] = base_confidence
                question_starts.append(result)
                found_numbers.add(result["question_number"])
                logger.info(f"  ✅ Found Q{result['question_number']} ({strategy_name})")
        
        # Sort and deduplicate
        question_starts.sort(key=lambda x: (
            x["element"]["page"], 
            x["element"]["y"],
            -x["confidence"]
        ))
        
        # Remove duplicates (keep highest confidence)
        unique_starts = []
        seen_numbers = set()
        for start in question_starts:
            if start["question_number"] not in seen_numbers:
                unique_starts.append(start)
                seen_numbers.add(start["question_number"])
        
        logger.info(f"📈 Total unique question starts: {len(unique_starts)}")
        return unique_starts
    
    def _strategy_standalone_number(self, elements, found_numbers):
        """Strategy 1: Standalone numbers at left margin (most reliable)"""
        results = []
        for element in elements:
            text = element["text"].strip()
            if (element["at_left_margin"] and 
                re.match(r'^\d{1,2}$', text) and
                6 <= element["font_size"] <= 20):
                
                q_num = int(text)
                if 1 <= q_num <= self.max_questions and q_num not in found_numbers:
                    results.append({
                        "question_number": q_num,
                        "element": element
                    })
        return results
    
    def _strategy_number_with_text(self, elements, found_numbers):
        """Strategy 2: Number followed by capital letter/word"""
        results = []
        for element in elements:
            text = element["text"].strip()
            if (element["at_left_margin"] and 
                re.match(r'^\d{1,2}\s+[A-Z]', text) and
                6 <= element["font_size"] <= 20):
                
                q_num_match = re.match(r'^(\d{1,2})', text)
                if q_num_match:
                    q_num = int(q_num_match.group(1))
                    if 1 <= q_num <= self.max_questions and q_num not in found_numbers:
                        results.append({
                            "question_number": q_num,
                            "element": element
                        })
        return results
    
    def _strategy_bold_number(self, elements, found_numbers):
        """Strategy 3: Bold numbers"""
        results = []
        for element in elements:
            text = element["text"].strip()
            if (element["is_bold"] and element["near_left"] and
                re.match(r'^\d{1,2}$', text) and
                8 <= element["font_size"] <= 18):
                
                q_num = int(text)
                if 1 <= q_num <= self.max_questions and q_num not in found_numbers:
                    results.append({
                        "question_number": q_num,
                        "element": element
                    })
        return results
    
    def _strategy_two_digit_number(self, elements, found_numbers):
        """Strategy 4: Two-digit numbers at left margin"""
        results = []
        for element in elements:
            text = element["text"].strip()
            if (element["at_left_margin"] and 
                re.match(r'^0?\d{1,2}$', text) and
                6 <= element["font_size"] <= 20):
                
                q_num = int(text)
                if 1 <= q_num <= self.max_questions and q_num not in found_numbers:
                    results.append({
                        "question_number": q_num,
                        "element": element
                    })
        return results
    
    def _strategy_number_with_dot(self, elements, found_numbers):
        """Strategy 5: Number with trailing dot"""
        results = []
        for element in elements:
            text = element["text"].strip()
            if (element["at_left_margin"] and 
                re.match(r'^\d{1,2}\.$', text) and
                6 <= element["font_size"] <= 20):
                
                q_num = int(text[:-1])
                if 1 <= q_num <= self.max_questions and q_num not in found_numbers:
                    results.append({
                        "question_number": q_num,
                        "element": element
                    })
        return results
    
    def _strategy_number_with_parenthesis(self, elements, found_numbers):
        """Strategy 6: Number with parenthesis"""
        results = []
        for element in elements:
            text = element["text"].strip()
            if (element["at_left_margin"] and 
                re.match(r'^\d{1,2}\)$', text) and
                6 <= element["font_size"] <= 20):
                
                q_num = int(text[:-1])
                if 1 <= q_num <= self.max_questions and q_num not in found_numbers:
                    results.append({
                        "question_number": q_num,
                        "element": element
                    })
        return results
    
    def _strategy_large_font_number(self, elements, found_numbers):
        """Strategy 7: Large font numbers (likely questions)"""
        results = []
        for element in elements:
            text = element["text"].strip()
            if (element["near_left"] and 
                re.match(r'^\d{1,2}$', text) and
                element["font_size"] >= 12):
                
                q_num = int(text)
                if 1 <= q_num <= self.max_questions and q_num not in found_numbers:
                    results.append({
                        "question_number": q_num,
                        "element": element
                    })
        return results
    
    def _calculate_smart_boundaries(self, question_starts, all_elements, pdf_doc):
        """
        Calculate smart question boundaries
        Preserves existing logic with enhancements
        """
        logger.info("🎯 Calculating smart question boundaries")
        
        for i, start_info in enumerate(question_starts):
            q_num = start_info["question_number"]
            start_element = start_info["element"]
            page_num = start_element["page"]
            start_y = start_element["y"]
            
            end_y = self._find_smart_end_boundary(
                q_num, page_num, start_y, all_elements, question_starts, i, pdf_doc
            )
            
            self.question_boundaries[q_num] = {
                "page": page_num,
                "start_y": start_y,
                "end_y": end_y,
                "height": end_y - start_y,
                "strategy": start_info["strategy"],
                "confidence": start_info["confidence"]
            }
            
            logger.info(f"  Q{q_num}: Page {page_num}, Y: {start_y:.0f}-{end_y:.0f} (height: {end_y-start_y:.0f})")
    
    def _find_smart_end_boundary(self, q_num, page_num, start_y, all_elements, question_starts, start_index, pdf_doc):
        """
        Find smart end boundary for question
        Enhanced version of existing logic
        """
        page = pdf_doc[page_num - 1]
        page_height = page.rect.height
        
        # Default end boundary
        default_end_y = page_height
        if start_index + 1 < len(question_starts):
            next_start = question_starts[start_index + 1]
            if next_start["element"]["page"] == page_num:
                default_end_y = next_start["element"]["y"] - 15
        
        # Get elements in question area
        question_elements = [
            elem for elem in all_elements
            if (elem["page"] == page_num and 
                start_y <= elem["y"] <= default_end_y)
        ]
        
        # Find last meaningful content
        last_content_y = start_y + 80  # Minimum question height
        last_option_y = start_y + 80
        
        for element in sorted(question_elements, key=lambda x: x["y"]):
            text = element["text"].strip()
            
            if self._is_answer_option_enhanced(text, element):
                last_option_y = element["y"] + element["height"] + 5
                last_content_y = max(last_content_y, last_option_y)
            elif self._is_question_content(text, element) and not self._is_footer_content_enhanced(text):
                last_content_y = max(last_content_y, element["y"] + element["height"] + 5)
            elif self._is_footer_content_enhanced(text):
                # Stop at footer content
                break
        
        smart_end_y = min(max(last_content_y, last_option_y), default_end_y)
        
        # Ensure reasonable question height (80-600 pixels)
        if smart_end_y - start_y < 80:
            smart_end_y = start_y + 80
        elif smart_end_y - start_y > 600:
            smart_end_y = start_y + 600
        
        return min(smart_end_y, default_end_y)
    
    def _is_answer_option_enhanced(self, text, element):
        """Enhanced answer option detection"""
        # Single letter options (A, B, C, D)
        if re.match(r'^[A-D]$', text) and element["x"] < 250:
            return True
        
        # Letter with text (A something)
        if re.match(r'^[A-D]\s+\w+', text) and element["x"] < 300:
            return True
        
        # Numeric options
        if (re.match(r'^\d+\s*[A-Za-z]*$', text) and 
            30 < element["x"] < 350 and
            element["font_size"] >= 8):
            return True
        
        # Multiple choice patterns
        if re.match(r'^[A-D]\)', text) and element["x"] < 200:
            return True
        
        return False
    
    def _is_question_content(self, text, element):
        """Check if text is question content"""
        if len(text) < 2:
            return False
        if re.match(r'^\d+$', text):  # Just numbers
            return False
        if re.match(r'^[A-D]$', text):  # Just option letters
            return False
        if element["font_size"] < 6 or element["font_size"] > 20:
            return False
        return True
    
    def _is_footer_content_enhanced(self, text):
        """Enhanced footer content detection"""
        footer_patterns = [
            r'©\s*UCLES', r'UCLES\s+\d+', r'\d+/\d+/[A-Z]/[A-Z]/\d+',
            r'0625/\d+/[A-Z]/[A-Z]/\d+', r'Turn over', r'^\[Turn over\]$',
            r'Cambridge International', r'IGCSE', r'Do not write',
            r'Permission to reproduce', r'End of Question Paper'
        ]
        
        for pattern in footer_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def extract_enhanced_question_images(self, pdf_path):
        """
        Extract high-quality images with standardized naming
        STANDARDIZED: All images saved to 'images' folder with consistent naming
        """
        logger.info(f"📸 Extracting question images to: {self.images_dir}")
        
        try:
            pdf_doc = fitz.open(pdf_path)
            question_images = {}
            
            for q_num, bounds in self.question_boundaries.items():
                try:
                    page_num = bounds["page"] - 1
                    page = pdf_doc[page_num]
                    
                    # Create extraction rectangle with padding
                    crop_rect = fitz.Rect(
                        max(0, 5),
                        max(0, bounds["start_y"] - 5),
                        page.rect.width - 5,
                        min(page.rect.height, bounds["end_y"] + 10)
                    )
                    
                    # High quality rendering
                    zoom = self.image_quality
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, clip=crop_rect)
                    
                    # STANDARDIZED: Consistent naming convention
                    img_filename = f"question_{q_num:02d}_enhanced.png"
                    img_path = self.images_dir / img_filename
                    
                    # Save image
                    pix.save(str(img_path))
                    
                    # Apply enhancement
                    self._enhance_image(img_path)
                    
                    question_images[q_num] = {
                        "filename": img_filename,
                        "path": str(img_path),
                        "size": (pix.width, pix.height),
                        "page": bounds["page"],
                        "strategy": bounds["strategy"],
                        "confidence": bounds["confidence"]
                    }
                    
                    logger.info(f"  ✅ Q{q_num}: {img_filename} ({pix.width}x{pix.height})")
                    pix = None
                    
                except Exception as e:
                    logger.error(f"  ❌ Failed to extract Q{q_num}: {e}")
                    continue
            
            pdf_doc.close()
            logger.info(f"📊 Successfully extracted {len(question_images)} question images")
            
            return question_images
            
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            raise
    
    def _enhance_image(self, img_path):
        """Apply light enhancement to extracted images"""
        try:
            img = Image.open(img_path)
            
            # Light contrast enhancement
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(self.enhancement_factor)
            
            # Light sharpness enhancement
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(self.enhancement_factor)
            
            # Save optimized
            img.save(img_path, "PNG", quality=90, optimize=True)
            
        except Exception as e:
            logger.warning(f"Image enhancement failed for {img_path}: {e}")
    
    def get_month_display_name(self, month_code):
        """Convert month code to display name"""
        month_mapping = {
            "mar": "March",
            "may": "May/June", 
            "oct": "October/November",
            "jan": "January",
            "feb": "February", 
            "jun": "June",
            "nov": "November",
            "dec": "December"
        }
        return month_mapping.get(month_code.lower(), month_code.title())
    
    def create_enhanced_question_bank(self, question_images, subject, year, month, paper_code):
        """
        Create comprehensive question bank with all metadata
        Enhanced version with better structure and validation
        """
        logger.info("📊 Creating enhanced question bank")
        
        questions = []
        
        # Sort question numbers for consistent ordering
        sorted_q_nums = sorted(question_images.keys())
        
        for q_num in sorted_q_nums:
            img_info = question_images[q_num]
            
            question = {
                "id": f"{subject}_q{q_num:02d}",
                "question_number": q_num,
                "question_text": f"Question {q_num} - See image for full question",
                "options": {
                    "A": "Option A",
                    "B": "Option B", 
                    "C": "Option C",
                    "D": "Option D"
                },
                "image_filename": img_info["filename"],
                "page": img_info["page"],
                "marks": 1,
                "subject": subject,
                "difficulty": "medium",
                "correct_answer": "",
                "explanation": "",
                "extraction_method": "enhanced_multi_strategy_detection",
                "detection_strategy": img_info["strategy"],
                "confidence": img_info["confidence"],
                "has_images": True,
                "extraction_focus": "web_interface_compatible"
            }
            
            questions.append(question)
        
        # Generate standardized filename
        standardized_filename = f"{subject}_{year}_{month}_{paper_code}.json"
        
        # Comprehensive metadata
        question_bank = {
            "metadata": {
                "app_name": "Enhanced PDF Question Extractor",
                "exam_paper": f"Cambridge IGCSE {subject.title()} Paper {paper_code}",
                "exam_session": f"{self.get_month_display_name(month)} {year}",
                "extraction_date": datetime.now().isoformat(),
                "extraction_method": "Multi-Strategy Enhanced Detection",
                "total_questions": len(questions),
                "extraction_tool": "Enhanced PDF Extractor v2.0",
                "approach": "Multi-strategy boundary detection with smart end boundaries",
                "web_interface_ready": True,
                "images_location": str(self.images_dir),
                "images_folder": "images",  # STANDARDIZED
                "filename": standardized_filename,
                "standardized_naming": True,
                "subject": subject,
                "year": year,
                "month": month,
                "month_display": self.get_month_display_name(month),
                "paper_code": paper_code,
                "image_quality": self.image_quality,
                "enhancement_applied": True,
                "extraction_success": True
            },
            "questions": questions
        }
        
        logger.info(f"📋 Created question bank: {len(questions)} questions")
        logger.info(f"📄 Filename: {standardized_filename}")
        
        return question_bank
    
    def deploy_for_web_interface(self, question_bank):
        """
        Deploy question bank for web interface with standardized folder structure
        FIXED: Proper deployed_images tracking and error handling
        """
        logger.info("🚀 Deploying for web interface")
        
        # Use standardized filename from metadata
        filename = question_bank["metadata"]["filename"]
        local_output = self.base_dir / filename
        deployed_images = 0  # Initialize counter
        
        try:
            # Save JSON locally
            with open(local_output, 'w', encoding='utf-8') as f:
                json.dump(question_bank, f, indent=2, ensure_ascii=False)
            logger.info(f"  ✅ Saved JSON to: {local_output}")
        except Exception as e:
            logger.error(f"  ❌ Failed to save JSON: {e}")
            raise
        
        # Create question bank directory structure
        subject = question_bank["metadata"]["subject"]
        year = question_bank["metadata"]["year"] 
        month = question_bank["metadata"]["month"]
        paper_code = question_bank["metadata"]["paper_code"]
        
        # STANDARDIZED: Main question bank directory
        question_bank_dir = Path("/Users/wynceaxcel/Apps/axcelscore/question_banks") / f"{subject}_{year}_{month}_{paper_code}"
        question_bank_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Deploy JSON file
            question_bank_json = question_bank_dir / "solutions.json"
            shutil.copy2(local_output, question_bank_json)
            logger.info(f"  ✅ Deployed JSON to: {question_bank_json}")
            
            # Create metadata file
            metadata_file = question_bank_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(question_bank["metadata"], f, indent=2, ensure_ascii=False)
            logger.info(f"  ✅ Created metadata: {metadata_file}")
            
            # STANDARDIZED: Deploy images to 'images' folder (primary)
            images_dir = question_bank_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Deploy images from source to destination
            if self.images_dir.exists():
                for img_file in self.images_dir.glob("*.png"):
                    try:
                        dst_path = images_dir / img_file.name
                        shutil.copy2(img_file, dst_path)
                        deployed_images += 1
                        logger.info(f"  📸 Deployed image: {img_file.name}")
                    except Exception as e:
                        logger.error(f"  ❌ Failed to deploy {img_file.name}: {e}")
            
            logger.info(f"  ✅ Successfully deployed {deployed_images} images")
            
        except Exception as e:
            logger.error(f"  ❌ Failed to deploy to question bank directory: {e}")
            raise
        
        # Optional: Deploy to React app (if exists)
        react_deployed = self._deploy_to_react_app(local_output, filename)
        
        return {
            'success': True,
            'output_file': str(local_output),
            'question_bank_dir': str(question_bank_dir),
            'deployed_images': deployed_images,  # FIXED: Always return this key
            'react_deployed': react_deployed,
            'metadata': question_bank["metadata"]
        }
    
    def _deploy_to_react_app(self, json_file, filename):
        """
        Fixed React app deployment with proper error handling
        """
        react_deployed = 0
        
        try:
            react_data_dir = self.react_app_path / "public" / "data"
            react_images_dir = self.react_app_path / "public" / "images"
            
            # Deploy JSON file
            if self.react_app_path.exists():
                react_data_dir.mkdir(parents=True, exist_ok=True)
                react_questions_file = react_data_dir / filename
                shutil.copy2(json_file, react_questions_file)
                logger.info(f"  ✅ Deployed JSON to React app: {react_questions_file}")
                
                # Deploy images
                if self.images_dir.exists():
                    react_images_dir.mkdir(parents=True, exist_ok=True)
                    for img_file in self.images_dir.glob("*.png"):
                        try:
                            dst_path = react_images_dir / img_file.name
                            shutil.copy2(img_file, dst_path)
                            react_deployed += 1
                        except Exception as e:
                            logger.error(f"  ❌ Failed to deploy {img_file.name} to React: {e}")
                    
                    logger.info(f"  ✅ Deployed {react_deployed} images to React app")
            else:
                logger.warning(f"  ⚠️ React app path does not exist: {self.react_app_path}")
                
        except Exception as e:
            logger.warning(f"  ⚠️ React app deployment failed: {e}")
        
        return react_deployed
    
    def extract_questions_for_web_interface(self, pdf_filename, subject, year, month, paper_code):
        """
        MAIN EXTRACTION METHOD: Complete extraction pipeline for web interface
        Returns properly structured result for API consumption
        """
        logger.info(f"🎯 Starting complete extraction pipeline")
        logger.info(f"📄 PDF: {pdf_filename}")
        logger.info(f"📚 Subject: {subject}")
        logger.info(f"📅 Year: {year}")
        logger.info(f"📆 Month: {month}")
        logger.info(f"📃 Paper: {paper_code}")
        
        pdf_path = self.base_dir / pdf_filename
        if not pdf_path.exists():
            error_msg = f"PDF file not found: {pdf_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # Step 1: Find question boundaries
            logger.info("📋 Step 1: Finding question boundaries")
            found_questions = self.find_enhanced_question_boundaries(pdf_path)
            logger.info(f"  📊 Found {found_questions} questions")
            
            if found_questions == 0:
                error_msg = "No questions detected in PDF"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'questions_found': 0,
                    'deployed_images': 0
                }
            
            # Step 2: Extract images
            logger.info("📸 Step 2: Extracting question images")
            question_images = self.extract_enhanced_question_images(pdf_path)
            logger.info(f"  📊 Extracted {len(question_images)} images")
            
            if not question_images:
                error_msg = "No images could be extracted"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'questions_found': found_questions,
                    'deployed_images': 0
                }
            
            # Step 3: Create question bank
            logger.info("📊 Step 3: Creating question bank")
            question_bank = self.create_enhanced_question_bank(
                question_images, subject, year, month, paper_code
            )
            logger.info(f"  📋 Created question bank with {len(question_bank['questions'])} questions")
            
            # Step 4: Deploy for web interface
            logger.info("🚀 Step 4: Deploying for web interface")
            deployment_result = self.deploy_for_web_interface(question_bank)
            
            if deployment_result['success']:
                # Success summary
                logger.info(f"\n🎉 EXTRACTION COMPLETE - SUCCESS!")
                logger.info("=" * 60)
                logger.info(f"✅ Questions extracted: {len(question_bank['questions'])}")
                logger.info(f"🖼️ Images saved to: {self.images_dir}")
                logger.info(f"📁 Images available: {len(list(self.images_dir.glob('*.png')))}")
                logger.info(f"💾 Question bank: {deployment_result['output_file']}")
                logger.info(f"📃 Standardized filename: {question_bank['metadata']['filename']}")
                logger.info(f"📅 Month: {month} → Display: {self.get_month_display_name(month)}")
                logger.info(f"🎯 Web interface ready with standardized 'images' folder")
                
                # Return success result
                return {
                    'success': True,
                    'questions_found': len(question_bank['questions']),
                    'question_bank': question_bank,
                    'deployment': deployment_result,
                    'images_extracted': len(question_images),
                    'deployed_images': deployment_result['deployed_images'],
                    'output_file': deployment_result['output_file']
                }
            else:
                error_msg = "Deployment failed"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'questions_found': len(question_bank['questions']),
                    'deployed_images': 0
                }
                
        except Exception as e:
            error_msg = f"Extraction failed: {str(e)}"
            logger.error(error_msg)
            logger.error("Full traceback:", exc_info=True)
            
            return {
                'success': False,
                'error': error_msg,
                'questions_found': 0,
                'deployed_images': 0,
                'exception': str(e)
            }

# ============================================================================
# WEB INTERFACE SECTION
# ============================================================================

if WEB_MODE:
    app = Flask(__name__)
    CORS(app)

    # Configuration
    BASE_DIR = Path("/Users/wynceaxcel/Apps/axcelscore")
    BACKEND_DIR = BASE_DIR / "backend"
    UPLOAD_DIR = BACKEND_DIR / "uploads"
    PDF_EXTRACTION_TEST_DIR = BASE_DIR / "pdf-extraction-test"

    # Ensure directories exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PDF_EXTRACTION_TEST_DIR.mkdir(parents=True, exist_ok=True)

    @app.route('/')
    def web_index():
        """Serve the enhanced web extractor interface"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🎯 Enhanced PDF Question Extractor</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh; padding: 20px;
                }
                .container {
                    max-width: 900px; margin: 0 auto; background: white;
                    border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                .header {
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    padding: 40px; text-align: center; color: white;
                }
                .header h1 { font-size: 2.8em; margin-bottom: 10px; font-weight: 700; }
                .header p { font-size: 1.2em; opacity: 0.9; margin: 5px 0; }
                .enhanced-badge {
                    background: rgba(255,255,255,0.2); color: white; 
                    padding: 8px 16px; border-radius: 20px; 
                    font-size: 0.9em; margin: 10px 5px; display: inline-block;
                }
                .main-content { padding: 40px; }
                .form-group { margin: 25px 0; }
                .form-group label { 
                    display: block; margin-bottom: 10px; font-weight: 600; 
                    color: #2d3748; font-size: 1em;
                }
                .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
                input, select {
                    width: 100%; padding: 15px; border: 2px solid #e2e8f0;
                    border-radius: 12px; font-size: 1em; transition: all 0.3s ease;
                    font-family: inherit;
                }
                input:focus, select:focus {
                    outline: none; border-color: #4facfe;
                    box-shadow: 0 0 0 4px rgba(79, 172, 254, 0.1);
                    transform: translateY(-1px);
                }
                .upload-area {
                    border: 3px dashed #e2e8f0; border-radius: 15px; padding: 50px;
                    text-align: center; transition: all 0.3s ease; cursor: pointer;
                    background: linear-gradient(45deg, #f8fafc, #fff);
                }
                .upload-area:hover {
                    border-color: #4facfe; background: linear-gradient(45deg, #f7faff, #fff);
                    transform: translateY(-2px);
                }
                .upload-area.dragover {
                    border-color: #00f2fe; background: #f0fdff;
                    transform: scale(1.02);
                }
                .upload-icon { font-size: 4em; color: #4facfe; margin-bottom: 20px; }
                .btn {
                    padding: 18px 35px; border: none; border-radius: 12px;
                    font-size: 1.1em; font-weight: 600; cursor: pointer;
                    transition: all 0.3s ease; display: inline-flex;
                    align-items: center; gap: 12px; justify-content: center;
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white; width: 100%; margin: 10px 0;
                }
                .btn:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 15px 35px rgba(79, 172, 254, 0.4);
                }
                .btn:disabled { 
                    opacity: 0.6; cursor: not-allowed; transform: none; 
                    box-shadow: none;
                }
                .progress { 
                    margin: 25px 0; display: none; 
                    background: linear-gradient(45deg, #f7fafc, #fff); 
                    padding: 25px; border-radius: 12px; border-left: 4px solid #4facfe;
                }
                .progress-bar {
                    width: 100%; height: 10px; background: #e2e8f0;
                    border-radius: 10px; overflow: hidden; margin: 10px 0;
                }
                .progress-fill {
                    height: 100%; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    width: 0%; transition: width 0.5s ease;
                }
                .message {
                    margin: 20px 0; padding: 20px; border-radius: 12px; 
                    font-weight: 500; display: none;
                }
                .success {
                    background: linear-gradient(45deg, #f0fff4, #e6fffa); 
                    color: #2f855a; border-left: 4px solid #38a169;
                }
                .error {
                    background: linear-gradient(45deg, #fef5e7, #fed7d7); 
                    color: #c53030; border-left: 4px solid #e53e3e;
                }
                .file-info {
                    background: linear-gradient(45deg, #f7fafc, #edf2f7); 
                    padding: 20px; border-radius: 12px;
                    margin-top: 15px; display: none;
                    border-left: 4px solid #4299e1;
                }
                .features {
                    display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px; margin: 30px 0;
                }
                .feature {
                    background: linear-gradient(45deg, #f8fafc, #fff);
                    padding: 20px; border-radius: 10px;
                    text-align: center; border-left: 3px solid #4facfe;
                }
                .feature-icon { font-size: 2em; margin-bottom: 10px; }
                @media (max-width: 768px) { 
                    .form-grid { grid-template-columns: 1fr; }
                    .features { grid-template-columns: 1fr; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Enhanced PDF Question Extractor</h1>
                    <p>AI-powered question extraction with multi-strategy detection</p>
                    <div>
                        <span class="enhanced-badge">✅ Multi-Strategy Detection</span>
                        <span class="enhanced-badge">🖼️ High-Quality Images</span>
                        <span class="enhanced-badge">🎯 Web Interface Ready</span>
                    </div>
                </div>

                <div class="main-content">
                    <div class="features">
                        <div class="feature">
                            <div class="feature-icon">🔍</div>
                            <h3>Smart Detection</h3>
                            <p>7 different strategies to find questions</p>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">📸</div>
                            <h3>Quality Images</h3>
                            <p>Enhanced 2x resolution with optimization</p>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">🚀</div>
                            <h3>Web Ready</h3>
                            <p>Standardized folder structure</p>
                        </div>
                    </div>

                    <form id="extractForm" enctype="multipart/form-data">
                        <div class="form-group">
                            <label for="pdf">📄 Upload PDF File</label>
                            <div class="upload-area" id="uploadArea">
                                <div class="upload-icon">📁</div>
                                <h3>Drop your PDF here or click to browse</h3>
                                <p>Supports IGCSE past papers and similar formats</p>
                                <input type="file" id="pdf" name="pdf" accept=".pdf" style="display: none;">
                            </div>
                            <div class="file-info" id="fileInfo"></div>
                        </div>

                        <div class="form-grid">
                            <div class="form-group">
                                <label for="subject">📚 Subject</label>
                                <select id="subject" name="subject" required>
                                    <option value="">Select Subject</option>
                                    <option value="physics">Physics</option>
                                    <option value="chemistry">Chemistry</option>
                                    <option value="biology">Biology</option>
                                    <option value="mathematics">Mathematics</option>
                                    <option value="english">English</option>
                                    <option value="economics">Economics</option>
                                    <option value="business_studies">Business Studies</option>
                                    <option value="computer_science">Computer Science</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="year">📅 Year</label>
                                <select id="year" name="year" required>
                                    <option value="">Select Year</option>
                                    <option value="2024">2024</option>
                                    <option value="2023">2023</option>
                                    <option value="2022">2022</option>
                                    <option value="2021">2021</option>
                                    <option value="2020">2020</option>
                                    <option value="2019">2019</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="month">📆 Session</label>
                                <select id="month" name="month" required>
                                    <option value="">Select Session</option>
                                    <option value="mar">March</option>
                                    <option value="may">May/June</option>
                                    <option value="oct">October/November</option>
                                    <option value="jan">January</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="paper_code">📃 Paper Code</label>
                                <select id="paper_code" name="paper_code" required>
                                    <option value="">Select Paper</option>
                                    <option value="11">Paper 11</option>
                                    <option value="12">Paper 12</option>
                                    <option value="13">Paper 13</option>
                                    <option value="21">Paper 21</option>
                                    <option value="22">Paper 22</option>
                                    <option value="23">Paper 23</option>
                                    <option value="31">Paper 31</option>
                                    <option value="32">Paper 32</option>
                                    <option value="33">Paper 33</option>
                                </select>
                            </div>
                        </div>

                        <button type="submit" class="btn" id="extractBtn">
                            🚀 Extract Questions
                        </button>
                    </form>

                    <div class="progress" id="progress">
                        <h3>📄 Processing your PDF...</h3>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                        <p id="progressText">Initializing extraction...</p>
                    </div>

                    <div class="message success" id="successMessage"></div>
                    <div class="message error" id="errorMessage"></div>
                </div>
            </div>

            <script>
                const uploadArea = document.getElementById('uploadArea');
                const fileInput = document.getElementById('pdf');
                const fileInfo = document.getElementById('fileInfo');
                const extractForm = document.getElementById('extractForm');
                const extractBtn = document.getElementById('extractBtn');
                const progress = document.getElementById('progress');
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                const successMessage = document.getElementById('successMessage');
                const errorMessage = document.getElementById('errorMessage');

                // File upload handling
                uploadArea.addEventListener('click', () => fileInput.click());
                uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                });
                uploadArea.addEventListener('dragleave', () => {
                    uploadArea.classList.remove('dragover');
                });
                uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        fileInput.files = files;
                        showFileInfo(files[0]);
                    }
                });

                fileInput.addEventListener('change', (e) => {
                    if (e.target.files.length > 0) {
                        showFileInfo(e.target.files[0]);
                    }
                });

                function showFileInfo(file) {
                    fileInfo.innerHTML = `
                        <h4>📄 Selected File:</h4>
                        <p><strong>Name:</strong> ${file.name}</p>
                        <p><strong>Size:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        <p><strong>Type:</strong> ${file.type}</p>
                    `;
                    fileInfo.style.display = 'block';
                }

                // Form submission
                extractForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    // Hide previous messages
                    successMessage.style.display = 'none';
                    errorMessage.style.display = 'none';
                    
                    // Validate form
                    if (!fileInput.files[0]) {
                        showError('Please select a PDF file');
                        return;
                    }
                    
                    // Show progress
                    extractBtn.disabled = true;
                    progress.style.display = 'block';
                    
                    // Simulate progress
                    simulateProgress();
                    
                    // Create form data
                    const formData = new FormData(extractForm);
                    
                    try {
                        const response = await fetch('/extract', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            showSuccess(`
                                <h3>🎉 Extraction Successful!</h3>
                                <p><strong>Questions Found:</strong> ${result.questions_found}</p>
                                <p><strong>Images Deployed:</strong> ${result.deployed_images || result.images_extracted}</p>
                                <p><strong>Output File:</strong> ${result.output_file}</p>
                                <p>Your questions are now available in the web interface!</p>
                            `);
                        } else {
                            showError(`Extraction failed: ${result.error}`);
                        }
                        
                    } catch (error) {
                        showError(`Network error: ${error.message}`);
                    } finally {
                        extractBtn.disabled = false;
                        progress.style.display = 'none';
                        progressFill.style.width = '0%';
                    }
                });

                function simulateProgress() {
                    const steps = [
                        'Analyzing PDF structure...',
                        'Detecting question boundaries...',
                        'Applying multi-strategy detection...',
                        'Extracting high-quality images...',
                        'Enhancing image quality...',
                        'Creating question bank...',
                        'Deploying to web interface...'
                    ];
                    
                    let step = 0;
                    const interval = setInterval(() => {
                        if (step < steps.length) {
                            progressText.textContent = steps[step];
                            progressFill.style.width = `${((step + 1) / steps.length) * 100}%`;
                            step++;
                        } else {
                            clearInterval(interval);
                        }
                    }, 1000);
                }

                function showSuccess(message) {
                    successMessage.innerHTML = message;
                    successMessage.style.display = 'block';
                    successMessage.scrollIntoView({ behavior: 'smooth' });
                }

                function showError(message) {
                    errorMessage.innerHTML = `<h3>❌ Error</h3><p>${message}</p>`;
                    errorMessage.style.display = 'block';
                    errorMessage.scrollIntoView({ behavior: 'smooth' });
                }
            </script>
        </body>
        </html>
        """

    @app.route('/extract', methods=['POST'])
    def web_extract_questions():
        """
        FIXED: Enhanced error handling and proper response structure
        """
        temp_path = None
        
        try:
            # Get form data with validation
            pdf_file = request.files.get('pdf')
            subject = request.form.get('subject', '').strip()
            year = request.form.get('year', '').strip()
            month = request.form.get('month', '').strip()
            paper_code = request.form.get('paper_code', '').strip()
            
            logger.info(f"📋 Extraction request: {subject}, {year}, {month}, {paper_code}")
            
            # Validate required fields
            if not all([pdf_file, subject, year, month, paper_code]):
                missing_fields = []
                if not pdf_file: missing_fields.append('PDF file')
                if not subject: missing_fields.append('subject')
                if not year: missing_fields.append('year')
                if not month: missing_fields.append('month')
                if not paper_code: missing_fields.append('paper_code')
                
                error_msg = f'Missing required fields: {", ".join(missing_fields)}'
                logger.error(f"❌ Validation error: {error_msg}")
                
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'questions_found': 0,
                    'deployed_images': 0
                }), 400
            
            # Validate PDF file
            if not pdf_file.filename.lower().endswith('.pdf'):
                error_msg = 'Only PDF files are supported'
                logger.error(f"❌ File validation error: {error_msg}")
                
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'questions_found': 0,
                    'deployed_images': 0
                }), 400
            
            # Save uploaded PDF temporarily with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_filename = f"temp_{timestamp}_{pdf_file.filename}"
            temp_path = PDF_EXTRACTION_TEST_DIR / temp_filename
            
            logger.info(f"📄 Saving PDF to: {temp_path}")
            pdf_file.save(str(temp_path))
            
            # Verify file was saved
            if not temp_path.exists() or temp_path.stat().st_size == 0:
                error_msg = "Failed to save uploaded PDF file"
                logger.error(f"❌ {error_msg}")
                
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'questions_found': 0,
                    'deployed_images': 0
                }), 500
            
            logger.info(f"✅ PDF saved successfully: {temp_path.stat().st_size} bytes")
            
            # Initialize enhanced extractor
            try:
                extractor = EnhancedPDFExtractor(base_dir=str(PDF_EXTRACTION_TEST_DIR))
                logger.info("✅ Extractor initialized successfully")
            except Exception as e:
                error_msg = f"Failed to initialize extractor: {str(e)}"
                logger.error(f"❌ {error_msg}")
                
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'questions_found': 0,
                    'deployed_images': 0
                }), 500
            
            # Perform extraction
            logger.info("🎯 Starting extraction process...")
            
            result = extractor.extract_questions_for_web_interface(
                pdf_filename=temp_filename,
                subject=subject.lower(),
                year=str(year),
                month=month.lower(),
                paper_code=str(paper_code)
            )
            
            logger.info(f"📊 Extraction result: {result}")
            
            # Return result with proper structure
            if result and result.get('success'):
                logger.info(f"✅ Extraction successful: {result['questions_found']} questions")
                
                response_data = {
                    'success': True,
                    'questions_found': result.get('questions_found', 0),
                    'output_file': result.get('output_file', ''),
                    'images_extracted': result.get('images_extracted', 0),
                    'deployed_images': result.get('deployed_images', 0),
                    'metadata': result.get('question_bank', {}).get('metadata', {})
                }
                
                return jsonify(response_data)
                
            else:
                error_msg = result.get('error', 'Unknown extraction error') if result else 'Extraction returned None'
                questions_found = result.get('questions_found', 0) if result else 0
                deployed_images = result.get('deployed_images', 0) if result else 0
                
                logger.error(f"❌ Extraction failed: {error_msg}")
                
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'questions_found': questions_found,
                    'deployed_images': deployed_images
                }), 500
                
        except Exception as e:
            error_msg = f'Server error: {str(e)}'
            logger.error(f"❌ Web extraction error: {error_msg}")
            logger.error("Full traceback:", exc_info=True)
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'questions_found': 0,
                'deployed_images': 0
            }), 500
            
        finally:
            # Clean up temp file
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                    logger.info(f"🧹 Cleaned up temp file: {temp_filename}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file: {e}")

    @app.route('/status')
    def web_status():
        """Enhanced health check endpoint"""
        return jsonify({
            'status': 'running',
            'mode': 'enhanced_pdf_extractor_v2',
            'timestamp': datetime.now().isoformat(),
            'features': {
                'multi_strategy_detection': True,
                'enhanced_image_quality': True,
                'standardized_folder_structure': True,
                'web_interface_ready': True,
                'backward_compatibility': True
            },
            'version': '2.0.0',
            'extraction_capabilities': {
                'max_questions': 50,
                'image_quality': '2x resolution',
                'enhancement_applied': True,
                'folder_structure': 'standardized_images_folder'
            }
        })

    @app.route('/solver')
    def web_solver():
        """Redirect to AI Solver interface"""
        return redirect('http://localhost:8000')

    # Image serving route for testing
    @app.route('/images/<path:filename>')
    def serve_image(filename):
        """Serve extracted images for testing"""
        try:
            images_dir = Path("/Users/wynceaxcel/Apps/axcelscore/pdf-extraction-test/images")
            return send_file(images_dir / filename, mimetype='image/png')
        except Exception as e:
            logger.error(f"Failed to serve image {filename}: {e}")
            return "Image not found", 404

# ============================================================================
# CLI FUNCTIONS AND MAIN EXECUTION
# ============================================================================

def interactive_extraction():
    """Interactive CLI extraction with enhanced interface"""
    print("\n🎯 Enhanced PDF Question Extractor - Interactive Mode")
    print("=" * 60)
    
    # Check available PDFs
    base_dir = Path("/Users/wynceaxcel/Apps/axcelscore/pdf-extraction-test")
    pdf_files = list(base_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in pdf-extraction-test directory")
        print(f"📂 Please place PDF files in: {base_dir}")
        return False
    
    print(f"📂 Found {len(pdf_files)} PDF file(s):")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"   {i}. {pdf_file.name}")
    
    try:
        # Select PDF
        pdf_choice = int(input(f"\nSelect PDF (1-{len(pdf_files)}): ")) - 1
        if not 0 <= pdf_choice < len(pdf_files):
            print("❌ Invalid PDF selection")
            return False
        
        selected_pdf = pdf_files[pdf_choice]
        print(f"✅ Selected: {selected_pdf.name}")
        
        # Get exam details with validation
        print("\n📋 Enter exam details:")
        subject = input("Subject (physics/chemistry/biology/etc.): ").strip().lower()
        year = input("Year (2019-2024): ").strip()
        month = input("Month (mar/may/oct/jan): ").strip().lower()
        paper_code = input("Paper code (11/12/13/21/22/23/etc.): ").strip()
        
        # Validate inputs
        if not all([subject, year, month, paper_code]):
            print("❌ All fields are required")
            return False
        
        if not year.isdigit() or not 2019 <= int(year) <= 2024:
            print("❌ Year must be between 2019-2024")
            return False
        
        if month not in ['mar', 'may', 'oct', 'jan', 'feb', 'jun', 'nov', 'dec']:
            print("❌ Invalid month code")
            return False
        
        # Confirm extraction
        print(f"\n🎯 Ready to extract:")
        print(f"   📄 PDF: {selected_pdf.name}")
        print(f"   📚 Subject: {subject}")
        print(f"   📅 Year: {year}")
        print(f"   📆 Month: {month}")
        print(f"   📃 Paper: {paper_code}")
        
        confirm = input("\nProceed with extraction? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Extraction cancelled")
            return False
        
        # Perform extraction
        print("\n🚀 Starting enhanced extraction...")
        extractor = EnhancedPDFExtractor(base_dir=str(selected_pdf.parent))
        
        result = extractor.extract_questions_for_web_interface(
            pdf_filename=selected_pdf.name,
            subject=subject,
            year=year,
            month=month,
            paper_code=paper_code
        )
        
        if result and result.get('success'):
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Questions extracted: {result['questions_found']}")
            print(f"🖼️ Images extracted: {result['images_extracted']}")
            print(f"📸 Images deployed: {result['deployed_images']}")
            print(f"💾 Output file: {result['output_file']}")
            print(f"🎯 Web interface ready!")
            return True
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Extraction failed'
            print(f"\n❌ Extraction failed: {error_msg}")
            return False
            
    except (ValueError, KeyboardInterrupt) as e:
        print(f"\n❌ Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error("Interactive extraction error:", exc_info=True)
        return False

def test_extraction():
    """Test extraction with sample parameters for development"""
    print("🧪 Test extraction mode")
    print("=" * 40)
    
    # Test parameters - modify as needed
    test_params = {
        'pdf_filename': '0625_w23_qp_13.pdf',  # Update with your PDF
        'subject': 'physics',
        'year': '2023',
        'month': 'oct',
        'paper_code': '13'
    }
    
    print(f"📋 Test parameters:")
    for key, value in test_params.items():
        print(f"   {key}: {value}")
    
    base_dir = "/Users/wynceaxcel/Apps/axcelscore/pdf-extraction-test"
    pdf_path = Path(base_dir) / test_params['pdf_filename']
    
    if not pdf_path.exists():
        print(f"❌ Test PDF not found: {pdf_path}")
        print("   Please update test_params with an existing PDF filename")
        return False
    
    try:
        extractor = EnhancedPDFExtractor(base_dir=base_dir)
        
        result = extractor.extract_questions_for_web_interface(
            pdf_filename=test_params['pdf_filename'],
            subject=test_params['subject'],
            year=test_params['year'],
            month=test_params['month'],
            paper_code=test_params['paper_code']
        )
        
        if result and result.get('success'):
            print("✅ Test extraction successful")
            print(f"   Questions found: {result['questions_found']}")
            print(f"   Images extracted: {result['images_extracted']}")
            print(f"   Images deployed: {result['deployed_images']}")
            return True
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Test failed'
            print(f"❌ Test extraction failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Test extraction error: {e}")
        logger.error("Test extraction error:", exc_info=True)
        return False

def start_web_server():
    """Start the enhanced web interface server"""
    if not WEB_MODE:
        print("❌ Flask not installed. Install with: pip install flask flask-cors")
        return
    
    print("🎯 Starting Enhanced PDF Question Extractor Web Server v2.0")
    print("=" * 70)
    print("✅ Multi-strategy question detection")
    print("✅ High-quality image extraction (2x resolution)")
    print("✅ Standardized folder structure (images/)")
    print("✅ Web interface ready")
    print("✅ Single images folder (GitHub optimized)")
    print("=" * 70)
    print(f"📂 Base directory: {BASE_DIR}")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print(f"🧪 PDF extraction test: {PDF_EXTRACTION_TEST_DIR}")
    print("=" * 70)
    
    # Try multiple ports
    ports = [5555, 8080, 3000, 5001, 8000, 5000]
    
    for port in ports:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            
            print(f"🌐 Web interface available at: http://localhost:{port}")
            print("📱 CLI mode still available: python extractor.py")
            print(f"\n🚀 Starting enhanced server on port {port}...")
            
            app.run(debug=False, host='0.0.0.0', port=port)
            return
            
        except OSError:
            print(f"⚠️ Port {port} is busy, trying next...")
            continue
    
    print("❌ All ports are busy. Common solutions:")
    print("   • Free up port 5000: lsof -ti:5000 | xargs kill -9")
    print("   • Disable AirPlay Receiver: System Preferences → General → AirDrop & Handoff")

def show_help():
    """Display comprehensive help information"""
    print("🎯 Enhanced PDF Question Extractor v2.0 - Help")
    print("=" * 60)
    print("\n📖 USAGE:")
    print("  python extractor.py              # Interactive CLI mode")
    print("  python extractor.py --web        # Web interface")
    print("  python extractor.py --test       # Test extraction")
    print("  python extractor.py --help       # This help")
    
    print("\n🎉 NEW FEATURES (v2.0):")
    print("  ✅ Multi-strategy question detection (7 strategies)")
    print("  ✅ Enhanced image quality (2x resolution + optimization)")
    print("  ✅ Standardized folder structure (images/)")
    print("  ✅ Improved web interface with progress tracking")
    print("  ✅ Comprehensive error handling and logging")
    print("  ✅ Single images folder structure")
    
    print("\n🔧 DETECTION STRATEGIES:")
    print("  1. Standalone numbers at left margin (most reliable)")
    print("  2. Numbers followed by capital letters/words")
    print("  3. Bold numbers near left margin")
    print("  4. Two-digit numbers at left margin")
    print("  5. Numbers with trailing dots")
    print("  6. Numbers with parentheses")
    print("  7. Large font numbers (likely questions)")
    
    print("\n📁 FOLDER STRUCTURE:")
    print("  question_banks/")
    print("  └── subject_year_month_paper/")
    print("      ├── solutions.json")
    print("      ├── metadata.json")
    print("      └── images/           # Primary folder")
    
    print("\n🌐 WEB INTERFACE:")
    print("  • Drag & drop PDF upload")
    print("  • Form validation")
    print("  • Real-time progress tracking")
    print("  • Detailed success/error feedback")
    
    print("\n🛠 TROUBLESHOOTING:")
    print("  • No questions found: PDF may have non-standard formatting")
    print("  • Web interface not loading: Check Flask installation")
    print("  • Images not showing: Verify folder permissions")
    print("  • Port conflicts: Try different ports or kill existing processes")
    
    print("\n📞 SUPPORT:")
    print("  • Check logs for detailed error information")
    print("  • Ensure PDF files are in pdf-extraction-test/ directory")
    print("  • Verify all form fields are completed in web interface")

def main():
    """
    Main function with enhanced menu system
    """
    print("🎯 Enhanced PDF Question Extractor v2.0")
    print("Multi-strategy detection • High-quality images • Web interface ready")
    print("=" * 70)
    
    # Check for PDFs
    base_dir = Path("/Users/wynceaxcel/Apps/axcelscore/pdf-extraction-test")
    pdf_files = list(base_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"📂 Found {len(pdf_files)} PDF file(s) in {base_dir.name}/:")
        for i, pdf_file in enumerate(pdf_files[:5], 1):  # Show max 5
            print(f"   {i}. {pdf_file.name}")
        if len(pdf_files) > 5:
            print(f"   ... and {len(pdf_files) - 5} more")
    else:
        print(f"📂 No PDF files found in {base_dir.name}/")
        print(f"   Place PDF files in: {base_dir}")
    
    print("\n🎯 Choose an option:")
    print("   1. Interactive extraction (CLI)")
    print("   2. Start web interface")
    print("   3. Test extraction")
    print("   4. Show help")
    print("   5. Exit")
    
    try:
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            if pdf_files:
                success = interactive_extraction()
                if success:
                    print("\n🎉 Extraction completed successfully!")
                else:
                    print("\n❌ Extraction failed or was cancelled")
            else:
                print("\n❌ No PDF files available for interactive extraction")
                print("   Add PDF files to pdf-extraction-test/ directory first")
                
        elif choice == "2":
            start_web_server()
            
        elif choice == "3":
            success = test_extraction()
            if success:
                print("\n🎉 Test completed successfully!")
            else:
                print("\n❌ Test failed")
                
        elif choice == "4":
            show_help()
            
        elif choice == "5":
            print("👋 Goodbye!")
            
        else:
            print("❌ Invalid choice. Use --help for usage information.")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error("Main execution error:", exc_info=True)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Configure logging for command line usage
    if len(sys.argv) > 1:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('extractor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--web":
            start_web_server()
            
        elif arg == "--test":
            success = test_extraction()
            sys.exit(0 if success else 1)
            
        elif arg == "--help" or arg == "-h":
            show_help()
            
        elif arg == "--interactive" or arg == "-i":
            success = interactive_extraction()
            sys.exit(0 if success else 1)
            
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        # Default: Run main menu
        main()