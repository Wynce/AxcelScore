#!/usr/bin/env python3
"""
review.py - Image Review Module for AI Tutor
Handles image review, replacement, and quality control functionality
FIXED VERSION - Standardized to use 'images' folder first, with enhanced cache-busting
"""

from flask import Blueprint, request, jsonify, send_from_directory, render_template_string
from pathlib import Path
import json
from datetime import datetime
import shutil
import os
from PIL import Image
import tempfile
import uuid
import hashlib

class ReviewManager:
    """Manages image review and replacement functionality"""
    
    def __init__(self, question_banks_dir):
        self.question_banks_dir = Path(question_banks_dir)
        self.current_paper_folder = None
        self.pending_replacements = {}  # Store pending image replacements
        
    def create_blueprint(self):
        """Create Flask blueprint for review routes"""
        review_bp = Blueprint('review', __name__, url_prefix='/api/review')
        
        @review_bp.route('/load-images', methods=['POST'])
        def load_images():
            return self._load_images()
        
        @review_bp.route('/replace-image', methods=['POST'])
        def replace_image():
            return self._replace_image()
        
        @review_bp.route('/update-all-images', methods=['POST'])
        def update_all_images():
            return self._update_all_images()
        
        @review_bp.route('/reset-replacements', methods=['POST'])
        def reset_replacements():
            return self._reset_replacements()
        
        @review_bp.route('/get-replacement-status', methods=['GET'])
        def get_replacement_status():
            return self._get_replacement_status()
        
        return review_bp
    
    def set_current_paper_folder(self, folder_name):
        """Set the current paper folder for review"""
        self.current_paper_folder = self.question_banks_dir / folder_name
        self.pending_replacements = {}  # Reset pending replacements
        return self.current_paper_folder.exists()
    
    def _get_file_hash(self, file_path):
        """Generate hash of file contents for cache-busting"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            print(f"Warning: Could not generate hash for {file_path}: {e}")
            return str(int(datetime.now().timestamp()))
    
    def _load_images(self):
        """Load all extracted images for review with standardized folder priority"""
        try:
            data = request.get_json()
            paper_folder = data.get('paper_folder')
            
            if not paper_folder:
                return jsonify({
                    "success": False,
                    "error": "No paper folder specified"
                }), 400
            
            if not self.set_current_paper_folder(paper_folder):
                return jsonify({
                    "success": False,
                    "error": f"Paper folder not found: {paper_folder}"
                }), 404
            
            # FIXED: Standardized folder priority - 'images' first, 'extracted_images' as fallback
            images_folder = self.current_paper_folder / "images"
            extracted_images_folder = self.current_paper_folder / "extracted_images"
            
            # Check which folder has images (UPDATED PRIORITY)
            active_folder = None
            folder_type = None
            folder_priority_info = []
            
            # Primary: Check 'images' folder first (standardized)
            if images_folder.exists() and list(images_folder.glob("question_*_enhanced.png")):
                active_folder = images_folder
                folder_type = "images"
                folder_priority_info.append(f"✅ Found images in standardized 'images/' folder")
                print(f"🎯 Using standardized 'images' folder: {images_folder}")
            
            # Fallback: Check 'extracted_images' folder for backward compatibility
            elif extracted_images_folder.exists() and list(extracted_images_folder.glob("question_*_enhanced.png")):
                active_folder = extracted_images_folder
                folder_type = "extracted_images"
                folder_priority_info.append(f"📁 Using 'extracted_images/' folder (compatibility)")
                print(f"📁 Using compatibility 'extracted_images' folder: {extracted_images_folder}")
            
            # Error: No images found in either folder
            else:
                error_details = []
                if not images_folder.exists():
                    error_details.append(f"❌ 'images/' folder does not exist")
                else:
                    img_count = len(list(images_folder.glob("question_*_enhanced.png")))
                    error_details.append(f"📁 'images/' folder exists but has {img_count} question images")
                
                if not extracted_images_folder.exists():
                    error_details.append(f"❌ 'extracted_images/' folder does not exist")
                else:
                    img_count = len(list(extracted_images_folder.glob("question_*_enhanced.png")))
                    error_details.append(f"📁 'extracted_images/' folder exists but has {img_count} question images")
                
                return jsonify({
                    "success": False,
                    "error": "No question images found in either folder",
                    "details": error_details,
                    "paper_folder": paper_folder,
                    "checked_folders": [str(images_folder), str(extracted_images_folder)]
                }), 404
            
            # Get all question images from active folder
            image_files = sorted(active_folder.glob("question_*_enhanced.png"))
            
            print(f"📊 Found {len(image_files)} images in {folder_type} folder")
            
            # Load metadata
            metadata_file = self.current_paper_folder / "metadata.json"
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            # Prepare image data with enhanced cache-busting
            images_data = []
            current_timestamp = int(datetime.now().timestamp() * 1000)
            
            for i, img_file in enumerate(image_files):
                try:
                    # Get image info
                    with Image.open(img_file) as img:
                        width, height = img.size
                    
                    file_size = img_file.stat().st_size
                    file_mtime = int(img_file.stat().st_mtime * 1000)
                    
                    # Generate file hash for unique cache-busting
                    file_hash = self._get_file_hash(img_file)
                    
                    # Create multiple cache-busting parameters for maximum effectiveness
                    cache_params = [
                        f"v={max(current_timestamp, file_mtime) + i}",
                        f"nocache={current_timestamp + i}",
                        f"hash={file_hash[:8]}",
                        f"mtime={file_mtime}",
                        f"refresh={datetime.now().microsecond}",
                        f"folder={folder_type}"  # Include folder type in cache params
                    ]
                    cache_string = "&".join(cache_params)
                    
                    # Construct URL based on detected folder structure
                    if folder_type == "images":
                        # Standard path for new 'images' folder
                        image_url = f"/images/{paper_folder}/{img_file.name}?{cache_string}"
                    else:
                        # Compatibility path for 'extracted_images' folder
                        image_url = f"/images/{paper_folder}/extracted_images/{img_file.name}?{cache_string}"
                    
                    print(f"🖼️ Generated URL for {img_file.name}: {image_url}")
                    
                    images_data.append({
                        "question_number": i + 1,
                        "filename": img_file.name,
                        "original_filename": img_file.name,
                        "file_size": file_size,
                        "file_size_mb": round(file_size / (1024*1024), 2),
                        "dimensions": f"{width}x{height}",
                        "width": width,
                        "height": height,
                        "url": image_url,
                        "status": "original",
                        "last_modified": datetime.fromtimestamp(img_file.stat().st_mtime).isoformat(),
                        "file_hash": file_hash[:8],
                        "cache_buster": current_timestamp + i,
                        "folder_type": folder_type
                    })
                    
                except Exception as e:
                    print(f"Error processing image {img_file}: {e}")
                    # Still create entry for broken images
                    error_cache_params = [
                        f"v={current_timestamp + i}",
                        f"error=true",
                        f"refresh={datetime.now().microsecond}",
                        f"folder={folder_type}"
                    ]
                    error_cache_string = "&".join(error_cache_params)
                    
                    if folder_type == "images":
                        error_url = f"/images/{paper_folder}/{img_file.name}?{error_cache_string}"
                    else:
                        error_url = f"/images/{paper_folder}/extracted_images/{img_file.name}?{error_cache_string}"
                    
                    images_data.append({
                        "question_number": i + 1,
                        "filename": img_file.name,
                        "original_filename": img_file.name,
                        "file_size": 0,
                        "file_size_mb": 0,
                        "dimensions": "Unknown",
                        "width": 0,
                        "height": 0,
                        "url": error_url,
                        "status": "error",
                        "error": str(e),
                        "last_modified": "",
                        "file_hash": "error",
                        "cache_buster": current_timestamp + i,
                        "folder_type": folder_type
                    })
            
            return jsonify({
                "success": True,
                "paper_folder": paper_folder,
                "total_images": len(images_data),
                "images": images_data,
                "metadata": metadata,
                "pending_replacements": len(self.pending_replacements),
                "load_timestamp": datetime.now().isoformat(),
                "cache_buster": current_timestamp,
                "folder_type": folder_type,
                "active_folder": str(active_folder),
                "folder_priority_info": folder_priority_info,
                "standardized_folder_used": folder_type == "images"
            })
            
        except Exception as e:
            print(f"❌ Error loading images: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def _replace_image(self):
        """Replace a specific image (stage for update)"""
        try:
            if 'file' not in request.files:
                return jsonify({
                    "success": False,
                    "error": "No file uploaded"
                }), 400
            
            file = request.files['file']
            question_number = int(request.form.get('question_number', 0))
            original_filename = request.form.get('original_filename', '')
            
            if not file or file.filename == '':
                return jsonify({
                    "success": False,
                    "error": "No file selected"
                }), 400
            
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                return jsonify({
                    "success": False,
                    "error": "Please upload a PNG or JPG image file"
                }), 400
            
            if not self.current_paper_folder:
                return jsonify({
                    "success": False,
                    "error": "No paper folder selected"
                }), 400
            
            # Validate file size
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return jsonify({
                    "success": False,
                    "error": "File too large. Maximum size is 10MB"
                }), 400
            
            # Create temp directory for pending replacements if not exists
            temp_dir = self.current_paper_folder / "temp_replacements"
            temp_dir.mkdir(exist_ok=True)
            
            # Generate temp filename
            file_extension = Path(file.filename).suffix.lower()
            temp_filename = f"question_{question_number}_replacement{file_extension}"
            temp_filepath = temp_dir / temp_filename
            
            # Save the uploaded file temporarily
            file.save(str(temp_filepath))
            
            # Convert to PNG if needed and get image info
            final_temp_path = temp_dir / f"question_{question_number}_replacement.png"
            
            try:
                with Image.open(temp_filepath) as img:
                    # Convert to RGB if necessary (for JPEGs with transparency)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Save as PNG
                    img.save(str(final_temp_path), 'PNG', optimize=True)
                    width, height = img.size
                
                # Remove original temp file if different
                if temp_filepath != final_temp_path and temp_filepath.exists():
                    temp_filepath.unlink()
                
                # Get final file info
                final_file_size = final_temp_path.stat().st_size
                
                # Enhanced cache-busting for preview
                preview_timestamp = int(datetime.now().timestamp() * 1000)
                file_hash = self._get_file_hash(final_temp_path)
                preview_cache_params = [
                    f"v={preview_timestamp}",
                    f"preview=true",
                    f"hash={file_hash[:8]}",
                    f"refresh={datetime.now().microsecond}"
                ]
                preview_cache_string = "&".join(preview_cache_params)
                preview_url = f"/images/{self.current_paper_folder.name}/temp_replacements/{final_temp_path.name}?{preview_cache_string}"
                
                # Store replacement info
                self.pending_replacements[question_number] = {
                    "original_filename": original_filename,
                    "new_filename": final_temp_path.name,
                    "temp_path": str(final_temp_path),
                    "file_size": final_file_size,
                    "file_size_mb": round(final_file_size / (1024*1024), 2),
                    "dimensions": f"{width}x{height}",
                    "width": width,
                    "height": height,
                    "uploaded_at": datetime.now().isoformat(),
                    "status": "pending",
                    "file_hash": file_hash[:8]
                }
                
                return jsonify({
                    "success": True,
                    "message": f"Image for Question {question_number} staged for replacement",
                    "question_number": question_number,
                    "replacement_info": self.pending_replacements[question_number],
                    "preview_url": preview_url,
                    "total_pending": len(self.pending_replacements)
                })
                
            except Exception as img_error:
                # Clean up temp file
                if temp_filepath.exists():
                    temp_filepath.unlink()
                if final_temp_path.exists() and final_temp_path != temp_filepath:
                    final_temp_path.unlink()
                
                return jsonify({
                    "success": False,
                    "error": f"Image processing error: {str(img_error)}"
                }), 400
            
        except Exception as e:
            print(f"❌ Error replacing image: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def _update_all_images(self):
        """Apply all pending image replacements with standardized folder handling"""
        try:
            if not self.current_paper_folder:
                return jsonify({
                    "success": False,
                    "error": "No paper folder selected"
                }), 400
            
            if not self.pending_replacements:
                return jsonify({
                    "success": False,
                    "error": "No pending replacements to apply"
                }), 400
            
            # FIXED: Use same folder detection logic as _load_images
            images_folder = self.current_paper_folder / "images"
            extracted_images_folder = self.current_paper_folder / "extracted_images"
            temp_dir = self.current_paper_folder / "temp_replacements"
            backup_dir = self.current_paper_folder / "backup_images"
            
            # Determine active folder using standardized priority
            active_folder = None
            folder_type = None
            
            # Primary: Check 'images' folder first
            if images_folder.exists() and list(images_folder.glob("question_*_enhanced.png")):
                active_folder = images_folder
                folder_type = "images"
                print(f"🎯 Updating images in standardized 'images' folder")
            
            # Fallback: Check 'extracted_images' folder
            elif extracted_images_folder.exists() and list(extracted_images_folder.glob("question_*_enhanced.png")):
                active_folder = extracted_images_folder
                folder_type = "extracted_images"
                print(f"📁 Updating images in compatibility 'extracted_images' folder")
            
            else:
                return jsonify({
                    "success": False,
                    "error": "No images folder with question images found for updating"
                }), 400
            
            # Create backup directory
            backup_dir.mkdir(exist_ok=True)
            
            applied_replacements = []
            failed_replacements = []
            
            for question_number, replacement_info in self.pending_replacements.items():
                try:
                    original_filename = replacement_info["original_filename"]
                    temp_path = Path(replacement_info["temp_path"])
                    
                    # Find the original file
                    original_path = active_folder / original_filename
                    
                    if not original_path.exists():
                        failed_replacements.append({
                            "question_number": question_number,
                            "error": f"Original file not found: {original_filename}"
                        })
                        continue
                    
                    if not temp_path.exists():
                        failed_replacements.append({
                            "question_number": question_number,
                            "error": f"Replacement file not found: {temp_path}"
                        })
                        continue
                    
                    # Create backup
                    backup_path = backup_dir / f"{original_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{original_path.suffix}"
                    shutil.copy2(original_path, backup_path)
                    
                    # Replace the original file
                    shutil.copy2(temp_path, original_path)
                    
                    # ENHANCED: Also update the file in the other folder if it exists (sync both folders)
                    try:
                        if folder_type == "images" and extracted_images_folder.exists():
                            # Also update in extracted_images folder if it exists
                            compat_path = extracted_images_folder / original_filename
                            if compat_path.exists():
                                shutil.copy2(temp_path, compat_path)
                                print(f"🔄 Also updated compatibility folder: {compat_path}")
                        
                        elif folder_type == "extracted_images" and images_folder.exists():
                            # Also update in images folder if it exists
                            std_path = images_folder / original_filename
                            if std_path.exists():
                                shutil.copy2(temp_path, std_path)
                                print(f"🔄 Also updated standard folder: {std_path}")
                                
                    except Exception as sync_error:
                        print(f"⚠️ Warning: Could not sync to other folder: {sync_error}")
                    
                    # Force file system sync and update modification time
                    try:
                        # Sync file system
                        if hasattr(os, 'sync'):
                            os.sync()
                        elif hasattr(os, 'fsync'):
                            with open(original_path, 'r+b') as f:
                                os.fsync(f.fileno())
                        
                        # Update modification time to current time
                        current_time = datetime.now().timestamp()
                        os.utime(original_path, (current_time, current_time))
                        
                        # Additional verification - check file size
                        new_size = original_path.stat().st_size
                        temp_size = temp_path.stat().st_size
                        
                        if new_size != temp_size:
                            print(f"⚠️ Warning: File size mismatch for {original_filename} (expected: {temp_size}, actual: {new_size})")
                        else:
                            print(f"✅ File replacement verified: {original_filename} ({new_size} bytes)")
                            
                    except Exception as sync_error:
                        print(f"⚠️ Warning: File sync failed for {original_filename}: {sync_error}")
                    
                    applied_replacements.append({
                        "question_number": question_number,
                        "original_filename": original_filename,
                        "backup_filename": backup_path.name,
                        "new_file_size": replacement_info["file_size"],
                        "dimensions": replacement_info["dimensions"],
                        "replacement_timestamp": datetime.now().isoformat(),
                        "active_folder": folder_type
                    })
                    
                    print(f"✅ Replaced Question {question_number}: {original_filename}")
                    
                except Exception as e:
                    failed_replacements.append({
                        "question_number": question_number,
                        "error": str(e)
                    })
                    print(f"❌ Failed to replace Question {question_number}: {e}")
            
            # Clean up temp directory
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                    print(f"🧹 Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    print(f"Warning: Could not clean up temp directory: {e}")
            
            # Clear pending replacements
            self.pending_replacements = {}
            
            # Update metadata with replacement info
            try:
                metadata_file = self.current_paper_folder / "metadata.json"
                metadata = {}
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                
                if "image_replacements" not in metadata:
                    metadata["image_replacements"] = []
                
                metadata["image_replacements"].append({
                    "timestamp": datetime.now().isoformat(),
                    "applied_count": len(applied_replacements),
                    "failed_count": len(failed_replacements),
                    "replacements": applied_replacements,
                    "failures": failed_replacements,
                    "active_folder": str(active_folder),
                    "folder_type": folder_type
                })
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                    
            except Exception as e:
                print(f"Warning: Could not update metadata: {e}")
            
            # Force system-wide cache invalidation
            try:
                # Additional file system operations to ensure cache invalidation
                for replacement in applied_replacements:
                    file_path = active_folder / replacement["original_filename"]
                    if file_path.exists():
                        # Touch the file again to ensure timestamp update
                        file_path.touch()
                
                print(f"🔄 Applied {len(applied_replacements)} file system cache invalidations")
            except Exception as e:
                print(f"Warning: Cache invalidation failed: {e}")
            
            return jsonify({
                "success": True,
                "message": f"Applied {len(applied_replacements)} image replacements",
                "applied_count": len(applied_replacements),
                "failed_count": len(failed_replacements),
                "applied_replacements": applied_replacements,
                "failed_replacements": failed_replacements,
                "backup_location": str(backup_dir),
                "update_timestamp": datetime.now().isoformat(),
                "active_folder": str(active_folder),
                "folder_type": folder_type
            })
            
        except Exception as e:
            print(f"❌ Error updating images: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def _reset_replacements(self):
        """Reset all pending replacements"""
        try:
            if not self.current_paper_folder:
                return jsonify({
                    "success": False,
                    "error": "No paper folder selected"
                }), 400
            
            # Clean up temp directory
            temp_dir = self.current_paper_folder / "temp_replacements"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            # Clear pending replacements
            cleared_count = len(self.pending_replacements)
            self.pending_replacements = {}
            
            return jsonify({
                "success": True,
                "message": f"Reset {cleared_count} pending replacements",
                "cleared_count": cleared_count
            })
            
        except Exception as e:
            print(f"❌ Error resetting replacements: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def _get_replacement_status(self):
        """Get current replacement status"""
        try:
            return jsonify({
                "success": True,
                "current_paper_folder": self.current_paper_folder.name if self.current_paper_folder else None,
                "pending_replacements": len(self.pending_replacements),
                "replacements": self.pending_replacements
            })
            
        except Exception as e:
            print(f"❌ Error getting replacement status: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

def create_review_html_tab():
    """Create the HTML content for the Review tab"""
    return '''
            <!-- Review Tab -->
            <div class="tab-pane" id="review-tab">
                <h2>🔍 Review Extracted Images</h2>
                <p style="margin-bottom: 2rem; color: #6c757d;">Review and replace extracted question images if needed (standardized folder structure)</p>

                <div id="reviewStatus">
                    <div class="alert alert-info">
                        <strong>📋 Review Process:</strong>
                        <ol style="margin-top: 10px; margin-left: 20px; line-height: 1.6;">
                            <li><strong>Review Quality:</strong> Check if images are correctly extracted</li>
                            <li><strong>Replace if Needed:</strong> Upload replacement images for poor extractions</li>
                            <li><strong>Update All:</strong> Apply all replacements (images auto-refresh)</li>
                        </ol>
                        <div style="margin-top: 15px; padding: 10px; background: #e8f5e9; border-radius: 6px;">
                            <strong>📁 Folder Priority:</strong> Uses standardized 'images/' folder first, falls back to 'extracted_images/' for compatibility
                        </div>
                    </div>
                </div>

                <div id="reviewControls" class="hidden" style="margin-bottom: 2rem;">
                    <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                        <button id="updateAllBtn" class="btn success" onclick="updateAllImages()" disabled>
                            💾 Update All Changes
                        </button>
                        <button id="resetReplacementsBtn" class="btn danger" onclick="resetReplacements()" disabled>
                            🔄 Reset Changes
                        </button>
                        <span id="pendingCount" class="status-pending" style="display: none;"></span>
                        <button id="goToSolveBtn" class="btn enhanced" onclick="goToSolve()">
                            🚀 Go to Solve
                        </button>
                    </div>
                </div>

                <div id="imageGallery" class="hidden">
                    <div id="galleryHeader" style="margin-bottom: 1rem;">
                        <h4>📸 Question Images</h4>
                        <p id="galleryInfo" style="color: #6c757d;"></p>
                        <div id="folderInfo" style="padding: 8px 12px; background: #f8f9fa; border-radius: 6px; margin-top: 10px; font-size: 14px;"></div>
                    </div>
                    
                    <div id="imageGrid" class="image-review-grid">
                        <!-- Images will be loaded here -->
                    </div>
                </div>

                <div id="reviewProgress" class="hidden">
                    <h4>🔄 Processing Images</h4>
                    <div class="progress">
                        <div id="reviewProgressBar" class="progress-bar" style="width: 0%">0%</div>
                    </div>
                    <p id="reviewProgressText">Loading images...</p>
                </div>

                <div id="reviewResults" class="hidden"></div>
            </div>
    '''

def get_review_css():
    """Get additional CSS for the Review tab"""
    return '''
        .image-review-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            margin-top: 1rem;
        }
        
        @media (max-width: 768px) {
            .image-review-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .image-review-card {
            background: #f8f9fa;
            border: 2px solid #dee2e6;
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .image-review-card:hover {
            border-color: #4facfe;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .image-review-card.has-replacement {
            border-color: #ffc107;
            background: #fff8e1;
        }
        
        .image-review-card.has-replacement::before {
            content: "🔄 Pending";
            position: absolute;
            top: -10px;
            right: -10px;
            background: #ffc107;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .image-review-card.standardized::after {
            content: "🎯 Standard";
            position: absolute;
            top: -10px;
            left: -10px;
            background: #28a745;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .image-preview {
            width: 100%;
            max-height: 300px;
            object-fit: contain;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #dee2e6;
            background: white;
        }
        
        .image-info {
            background: white;
            border-radius: 8px;
            padding: 0.75rem;
            margin-bottom: 1rem;
            font-size: 12px;
            color: #6c757d;
        }
        
        .image-info div {
            margin-bottom: 0.25rem;
        }
        
        .image-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 12px;
            border-radius: 6px;
        }
        
        .upload-replacement {
            display: none;
            background: #f8f9fa;
            border: 2px dashed #4facfe;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .upload-replacement:hover {
            background: #e6f3ff;
            border-color: #2196F3;
        }
        
        .upload-replacement.active {
            display: block;
        }
        
        .replacement-preview {
            display: none;
            margin-top: 1rem;
            padding: 1rem;
            background: #e8f5e9;
            border: 2px solid #4caf50;
            border-radius: 8px;
        }
        
        .replacement-preview.active {
            display: block;
        }
        
        .replacement-preview img {
            max-width: 100%;
            max-height: 200px;
            object-fit: contain;
            border-radius: 6px;
            margin-bottom: 0.5rem;
        }
        
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 0.5rem;
        }
        
        .status-original {
            background: #e8f5e9;
            color: #2f7d32;
        }
        
        .status-pending {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .folder-info-badge {
            display: inline-block;
            padding: 0.3rem 0.6rem;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            margin: 0.2rem;
        }
        
        .folder-standard {
            background: #d4edda;
            color: #155724;
        }
        
        .folder-compatibility {
            background: #fff3cd;
            color: #856404;
        }
    '''