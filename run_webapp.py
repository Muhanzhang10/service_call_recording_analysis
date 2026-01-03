#!/usr/bin/env python3
"""
Simple HTTP server to run the web application locally
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent

# Configuration
PORT = 8000
WEBAPP_PATH = "/webapp/"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Change to project root directory
    os.chdir(PROJECT_ROOT)
    
    # Create server
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}{WEBAPP_PATH}"
        
        print("="*60)
        print("Service Call Analysis Web Application")
        print("="*60)
        print(f"\n✓ Server running at: http://localhost:{PORT}/")
        print(f"\n✓ Open in browser: {url}")
        print("\nPress Ctrl+C to stop the server")
        print("="*60)
        
        # Try to open browser automatically
        try:
            webbrowser.open(url)
            print("\n✓ Opening browser...")
        except:
            print("\n⚠️  Could not open browser automatically")
            print(f"   Please open {url} manually")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")
            return 0

if __name__ == "__main__":
    main()

