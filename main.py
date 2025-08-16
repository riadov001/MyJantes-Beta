#!/usr/bin/env python3
"""
Simple web server to serve Flutter web application
"""
import os
import http.server
import socketserver
import subprocess
import sys
from pathlib import Path

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="flutter_app/build/web", **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def build_flutter_web():
    """Build Flutter web application if not already built"""
    build_dir = Path("flutter_app/build/web")
    
    if not build_dir.exists():
        print("Building Flutter web application...")
        try:
            # Try to build with flutter if available
            result = subprocess.run(
                ["flutter", "build", "web", "--release"],
                cwd="flutter_app",
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("Flutter web build completed successfully!")
                return True
            else:
                print(f"Flutter build failed: {result.stderr}")
                return False
        except FileNotFoundError:
            print("Flutter not found. Creating fallback web structure...")
            create_fallback_web()
            return True
    else:
        print("Flutter web build already exists.")
        return True

def create_fallback_web():
    """Create a fallback web structure when Flutter is not available"""
    build_dir = Path("flutter_app/build/web")
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a basic index.html
    index_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta content="IE=Edge" http-equiv="X-UA-Compatible">
    <meta name="description" content="MY JANTES - Expert en rénovation de jantes aluminium">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="MY JANTES">
    <meta name="msapplication-TileColor" content="#DC2626">
    <meta name="theme-color" content="#DC2626">
    <title>MY JANTES - Rénovation de jantes</title>
    <link rel="manifest" href="manifest.json">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #DC2626, #EF4444);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .container {
            max-width: 600px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 2.5em; margin-bottom: 20px; }
        p { font-size: 1.2em; margin-bottom: 15px; }
        .status {
            background: rgba(255, 255, 255, 0.2);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: white;
            color: #DC2626;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>MY JANTES</h1>
        <p>Expert en rénovation de jantes aluminium</p>
        
        <div class="status">
            <h3>🚀 Déploiement en cours</h3>
            <p>L'application Flutter est en cours de configuration pour le déploiement.</p>
            <p>Cette page sera automatiquement remplacée par l'application complète.</p>
        </div>
        
        <a href="#" class="btn">🔄 Actualiser</a>
        <a href="mailto:contact@myjantes.fr" class="btn">📧 Contact</a>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds to check for Flutter build
        setTimeout(() => location.reload(), 30000);
        
        // Simple click handler for refresh button
        document.querySelector('.btn').onclick = (e) => {
            e.preventDefault();
            location.reload();
        };
    </script>
</body>
</html>"""
    
    with open(build_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_content)
    
    # Create manifest.json
    manifest_content = """{
    "name": "MY JANTES",
    "short_name": "MY JANTES",
    "description": "Expert en rénovation de jantes aluminium",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#DC2626",
    "theme_color": "#DC2626",
    "icons": [
        {
            "src": "favicon.png",
            "sizes": "192x192",
            "type": "image/png"
        }
    ]
}"""
    
    with open(build_dir / "manifest.json", "w", encoding="utf-8") as f:
        f.write(manifest_content)

def main():
    """Main server function"""
    PORT = int(os.environ.get("PORT", 5000))
    
    print("=" * 50)
    print("MY JANTES Flutter Web Server")
    print("=" * 50)
    
    # Build Flutter web if needed
    if not build_flutter_web():
        print("Failed to build Flutter web application")
        sys.exit(1)
    
    # Start server
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
            print(f"🚀 Serving at http://0.0.0.0:{PORT}")
            print(f"📱 MY JANTES application ready!")
            print("=" * 50)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()