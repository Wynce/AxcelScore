#!/usr/bin/env python3
"""
AI Solver Interface Server
Serves the HTML interface with proper image access
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path
import threading
import time

class AISolverHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve AI solver interface with images"""
    
    def __init__(self, *args, base_dir=None, **kwargs):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        print(f"📍 Request: {self.path}")
        
        # Handle image requests specifically
        if self.path.startswith('/extracted_images/'):
            image_filename = self.path.split('/')[-1]  # Get just the filename
            image_path = self.base_dir / "extracted_images" / image_filename
            
            print(f"🖼️ Looking for image: {image_path}")
            
            if image_path.exists():
                print(f"✅ Found image: {image_path}")
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                with open(image_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                print(f"❌ Image not found: {image_path}")
                self.send_error(404, f"Image not found: {image_filename}")
                return
        
        # Handle HTML interface
        elif self.path in ['/', '/enhanced_claude_solver_interface.html', '']:
            html_file = self.base_dir / 'enhanced_claude_solver_interface.html'
            
            if html_file.exists():
                print(f"✅ Serving HTML: {html_file}")
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Ensure images use relative paths that our server can handle
                    content = content.replace('src="extracted_images/', 'src="/extracted_images/')
                    self.wfile.write(content.encode('utf-8'))
                return
            else:
                print(f"❌ HTML not found: {html_file}")
                self.send_error(404, "AI Solver interface not found")
                return
        
        # Handle other static files
        else:
            # Default file serving
            super().do_GET()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_ai_solver_server(base_dir=None, port=8080):
    """Start the AI solver interface server"""
    
    if base_dir is None:
        base_dir = "/Users/wynceaxcel/Apps/axcelscore/pdf-extraction-test"
    
    base_path = Path(base_dir)
    html_file = base_path / "enhanced_claude_solver_interface.html"
    images_dir = base_path / "extracted_images"
    
    print("🧠 AI Solver Interface Server")
    print("=" * 60)
    print(f"📂 Base directory: {base_path}")
    print(f"📄 HTML interface: {html_file}")
    print(f"🖼️ Images directory: {images_dir}")
    print(f"🌐 Server port: {port}")
    
    # Validation checks
    if not base_path.exists():
        print(f"❌ Base directory not found: {base_path}")
        print("   Please check the path and try again.")
        return False
    
    if not html_file.exists():
        print(f"❌ HTML interface not found: {html_file}")
        print("   Please create the AI solver interface first!")
        print("   Run: python main.py and use the 'Create AI Solver Interface' button")
        return False
    
    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        print("   Please extract questions first!")
        return False
    
    # Count available images
    image_files = list(images_dir.glob("question_*_enhanced.png"))
    print(f"📊 Available images: {len(image_files)}")
    
    if len(image_files) == 0:
        print("⚠️ No question images found!")
        print("   Please run question extraction first.")
        return False
    
    # Sample images found
    for i, img_file in enumerate(image_files[:3]):
        print(f"   📷 {img_file.name}")
    if len(image_files) > 3:
        print(f"   ... and {len(image_files) - 3} more")
    
    # Check if port is already in use
    try:
        test_socket = socketserver.TCPServer(("", port), None)
        test_socket.server_close()
    except OSError:
        print(f"❌ Port {port} is already in use!")
        print(f"   Try a different port or stop the other service.")
        print(f"   Your Flask app is likely running on port 5001.")
        print(f"   Trying port 8081 instead...")
        port = 8081
    
    # Change to base directory
    original_cwd = os.getcwd()
    os.chdir(base_path)
    
    try:
        # Create handler factory with base_dir
        def handler_factory(*args, **kwargs):
            return AISolverHandler(*args, base_dir=base_path, **kwargs)
        
        # Start server
        with socketserver.TCPServer(("", port), handler_factory) as httpd:
            print("=" * 60)
            print(f"🚀 AI Solver Server STARTED!")
            print(f"🌐 URL: http://localhost:{port}")
            print(f"📱 Interface: http://localhost:{port}/enhanced_claude_solver_interface.html")
            print("=" * 60)
            print("📋 Usage Instructions:")
            print("1. Browser will open automatically")
            print("2. Images should load correctly now")
            print("3. Copy prompts and use with Claude.ai")
            print("4. Use Ctrl+C to stop server")
            print("=" * 60)
            
            # Auto-open browser after a short delay
            def open_browser():
                time.sleep(2)
                url = f"http://localhost:{port}"
                print(f"🔗 Opening browser: {url}")
                webbrowser.open(url)
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Start serving
            print("⏳ Starting server... (opening browser in 2 seconds)")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user (Ctrl+C)")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def main():
    """Main function to start AI solver server"""
    print("🎯 AI Solver Interface Server Launcher")
    print("This will serve your AI solver interface with working images\n")
    
    # Default base directory
    base_dir = "/Users/wynceaxcel/Apps/axcelscore/pdf-extraction-test"
    
    # Check if custom base directory provided
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
        print(f"📂 Using custom base directory: {base_dir}")
    
    # Check if custom port provided
    port = 8080
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
            print(f"🌐 Using custom port: {port}")
        except ValueError:
            print("⚠️ Invalid port number, using default 8080")
    
    success = start_ai_solver_server(base_dir, port)
    
    if success:
        print("✅ Server shut down successfully")
    else:
        print("❌ Server failed to start")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you've created the AI solver interface first")
        print("2. Check that question extraction has been completed")
        print("3. Verify the base directory path is correct")
        print("4. Try running: python main.py first")

if __name__ == "__main__":
    main()