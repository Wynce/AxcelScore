#!/usr/bin/env python3
"""
Direct web server launcher - bypasses interactive menu
"""

import sys
import os
from pathlib import Path

# Import the Flask app and functions from extractor
try:
    from extractor import WEB_MODE, app
    if not WEB_MODE:
        print("❌ Flask not available. Install with: pip install flask flask-cors")
        sys.exit(1)
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the backend directory")
    sys.exit(1)

def start_server():
    """Start the web server directly without menu"""
    print("🎯 Starting PDF Question Extractor Web Server")
    print("=" * 60)
    print("✅ Direct web server launch (no interactive menu)")
    print("=" * 60)
    
    # Configuration
    BASE_DIR = Path("/Users/wynceaxcel/Apps/axcelscore")
    BACKEND_DIR = BASE_DIR / "backend"
    UPLOAD_DIR = BACKEND_DIR / "uploads"
    PDF_EXTRACTION_TEST_DIR = BASE_DIR / "pdf-extraction-test"
    
    # Ensure directories exist
    UPLOAD_DIR.mkdir(exist_ok=True)
    PDF_EXTRACTION_TEST_DIR.mkdir(exist_ok=True)
    
    print(f"📂 Base directory: {BASE_DIR}")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print(f"🔬 PDF extraction test: {PDF_EXTRACTION_TEST_DIR}")
    print("=" * 60)
    
    # Try different ports if needed
    ports = [5555, 8080, 3000, 5001, 8000]
    
    for port in ports:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            
            print(f"🌐 Web interface available at: http://localhost:{port}")
            print("📱 Access this URL in your browser")
            print("⏹️ Press Ctrl+C to stop the server")
            print("=" * 60)
            
            # Start server WITHOUT debug mode to prevent restart loop
            app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
            return
            
        except OSError:
            print(f"⚠️ Port {port} is busy, trying next...")
            continue
    
    print("❌ All ports are busy!")

if __name__ == '__main__':
    start_server()
