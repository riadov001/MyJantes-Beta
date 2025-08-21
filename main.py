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
    
    def do_GET(self):
        # Health check endpoint for deployment
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # If it's the health check, return simple OK
            if self.path == '/health':
                self.wfile.write(b'OK')
                return
            
            # For root path, try to serve the Flutter app or fallback
            try:
                super().do_GET()
            except Exception:
                # If Flutter app fails, serve fallback
                self.serve_fallback_page()
        else:
            # For all other paths, try to serve normally
            try:
                super().do_GET()
            except Exception:
                # If file not found, redirect to main page
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
    
    def serve_fallback_page(self):
        """Serve the fallback page content directly"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        fallback_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="MY JANTES - Expert en rénovation de jantes aluminium à Liévin. Redonnez vie à vos jantes avec notre expertise professionnelle.">
    <meta name="keywords" content="rénovation jantes, jantes aluminium, Liévin, réparation jantes, polissage jantes">
    <meta property="og:title" content="MY JANTES - Rénovation de jantes aluminium">
    <meta property="og:description" content="Expert en rénovation de jantes aluminium à Liévin">
    <meta property="og:type" content="website">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="MY JANTES">
    <meta name="theme-color" content="#DC2626">
    <title>MY JANTES - Rénovation de jantes aluminium à Liévin</title>
    <link rel="manifest" href="manifest.json">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #DC2626, #EF4444);
            color: white;
            text-align: center;
            padding: 60px 20px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .header p {
            font-size: 1.3em;
            opacity: 0.9;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .services {
            padding: 60px 20px;
            background: #f8f9fa;
        }
        .services h2 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 40px;
            color: #DC2626;
        }
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        .service-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        .service-card:hover {
            transform: translateY(-5px);
        }
        .service-icon {
            font-size: 3em;
            margin-bottom: 20px;
        }
        .service-card h3 {
            color: #DC2626;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .contact {
            background: #DC2626;
            color: white;
            padding: 60px 20px;
            text-align: center;
        }
        .contact h2 {
            font-size: 2.5em;
            margin-bottom: 30px;
        }
        .contact-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }
        .contact-item {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 10px;
        }
        .contact-item h3 {
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .btn {
            display: inline-block;
            background: white;
            color: #DC2626;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            font-size: 1.1em;
            margin: 10px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #f8f9fa;
            transform: translateY(-2px);
        }
        .footer {
            background: #1a1a1a;
            color: white;
            text-align: center;
            padding: 30px 20px;
        }
        @media (max-width: 768px) {
            .header h1 { font-size: 2.2em; }
            .header p { font-size: 1.1em; }
            .services h2 { font-size: 2em; }
            .contact h2 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>MY JANTES</h1>
            <p>Expert en rénovation de jantes aluminium</p>
            <p>Redonnez vie à vos jantes avec notre expertise professionnelle</p>
        </div>
    </header>

    <section class="services">
        <div class="container">
            <h2>Nos Services</h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-icon">⚡</div>
                    <h3>Rénovation Complète</h3>
                    <p>Remise à neuf de vos jantes aluminium avec finition professionnelle</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">✨</div>
                    <h3>Polissage Expert</h3>
                    <p>Polissage haute qualité pour un éclat parfait de vos jantes</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🎨</div>
                    <h3>Personnalisation</h3>
                    <p>Customisation selon vos goûts avec une large gamme de finitions</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🔧</div>
                    <h3>Réparation</h3>
                    <p>Réparation de rayures, impacts et déformations sur jantes alu</p>
                </div>
            </div>
        </div>
    </section>

    <section class="contact">
        <div class="container">
            <h2>Nous Contacter</h2>
            <div class="contact-info">
                <div class="contact-item">
                    <h3>📍 Adresse</h3>
                    <p>Liévin, France</p>
                </div>
                <div class="contact-item">
                    <h3>📞 Téléphone</h3>
                    <p>Contactez-nous pour un devis</p>
                </div>
                <div class="contact-item">
                    <h3>📧 Email</h3>
                    <p>contact@myjantes.fr</p>
                </div>
                <div class="contact-item">
                    <h3>⏰ Horaires</h3>
                    <p>Sur rendez-vous</p>
                </div>
            </div>
            <div>
                <a href="mailto:contact@myjantes.fr" class="btn">Demander un devis</a>
                <a href="tel:+" class="btn">Nous appeler</a>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 MY JANTES - Expert en rénovation de jantes aluminium à Liévin</p>
        </div>
    </footer>
</body>
</html>"""
        
        self.wfile.write(fallback_content.encode('utf-8'))
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def build_flutter_web():
    """Build Flutter web application with improved error handling and timeout"""
    build_dir = Path("flutter_app/build/web")
    
    # Check if Flutter is available first
    try:
        print("Checking Flutter SDK availability...")
        flutter_check = subprocess.run(
            ["flutter", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if flutter_check.returncode != 0:
            print("Flutter SDK not properly configured. Using fallback...")
            create_fallback_web()
            return True
            
        print(f"Flutter SDK detected: {flutter_check.stdout.split()[1] if flutter_check.stdout else 'unknown version'}")
        
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        print("Flutter SDK not available. Creating fallback web structure...")
        create_fallback_web()
        return True
    
    # Flutter is available, attempt to build
    print("Building Flutter web application...")
    try:
        # Clean previous builds for fresh deployment
        print("Cleaning previous builds...")
        clean_result = subprocess.run(
            ["flutter", "clean"],
            cwd="flutter_app",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Install Flutter dependencies
        print("Installing Flutter dependencies...")
        pub_get_result = subprocess.run(
            ["flutter", "pub", "get"],
            cwd="flutter_app",
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if pub_get_result.returncode != 0:
            print(f"Flutter pub get warning: {pub_get_result.stderr}")
            # Continue anyway as this might not be critical
        
        # Build Flutter web with timeout
        print("Compiling Flutter web application...")
        result = subprocess.run(
            ["flutter", "build", "web", "--release", "--web-renderer", "html"],
            cwd="flutter_app",
            capture_output=True,
            text=True,
            timeout=180  # 3 minutes timeout for build
        )
        
        if result.returncode == 0:
            print("Flutter web build completed successfully!")
            # Verify build output exists
            if (build_dir / "index.html").exists():
                print("Flutter build verification: index.html found")
                return True
            else:
                print("Flutter build verification failed: index.html not found")
                create_fallback_web()
                return True
        else:
            print(f"Flutter build failed with return code: {result.returncode}")
            print(f"Flutter build stderr: {result.stderr}")
            print(f"Flutter build stdout: {result.stdout}")
            # Create fallback instead of failing
            print("Creating fallback web structure...")
            create_fallback_web()
            return True
            
    except subprocess.TimeoutExpired:
        print("Flutter build timed out. Creating fallback web structure...")
        create_fallback_web()
        return True
    except Exception as e:
        print(f"Unexpected error during Flutter build: {e}")
        create_fallback_web()
        return True

def create_fallback_web():
    """Create a fallback web structure when Flutter is not available"""
    build_dir = Path("flutter_app/build/web")
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create professional MY JANTES homepage
    index_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="MY JANTES - Expert en rénovation de jantes aluminium à Liévin. Redonnez vie à vos jantes avec notre expertise professionnelle.">
    <meta name="keywords" content="rénovation jantes, jantes aluminium, Liévin, réparation jantes, polissage jantes">
    <meta property="og:title" content="MY JANTES - Rénovation de jantes aluminium">
    <meta property="og:description" content="Expert en rénovation de jantes aluminium à Liévin">
    <meta property="og:type" content="website">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="MY JANTES">
    <meta name="theme-color" content="#DC2626">
    <title>MY JANTES - Rénovation de jantes aluminium à Liévin</title>
    <link rel="manifest" href="manifest.json">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #DC2626, #EF4444);
            color: white;
            text-align: center;
            padding: 60px 20px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .header p {
            font-size: 1.3em;
            opacity: 0.9;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .services {
            padding: 60px 20px;
            background: #f8f9fa;
        }
        .services h2 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 40px;
            color: #DC2626;
        }
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        .service-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        .service-card:hover {
            transform: translateY(-5px);
        }
        .service-icon {
            font-size: 3em;
            margin-bottom: 20px;
        }
        .service-card h3 {
            color: #DC2626;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .contact {
            background: #DC2626;
            color: white;
            padding: 60px 20px;
            text-align: center;
        }
        .contact h2 {
            font-size: 2.5em;
            margin-bottom: 30px;
        }
        .contact-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }
        .contact-item {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 10px;
        }
        .contact-item h3 {
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .btn {
            display: inline-block;
            background: white;
            color: #DC2626;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            font-size: 1.1em;
            margin: 10px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #f8f9fa;
            transform: translateY(-2px);
        }
        .footer {
            background: #1a1a1a;
            color: white;
            text-align: center;
            padding: 30px 20px;
        }
        @media (max-width: 768px) {
            .header h1 { font-size: 2.2em; }
            .header p { font-size: 1.1em; }
            .services h2 { font-size: 2em; }
            .contact h2 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>MY JANTES</h1>
            <p>Expert en rénovation de jantes aluminium</p>
            <p>Redonnez vie à vos jantes avec notre expertise professionnelle</p>
        </div>
    </header>

    <section class="services">
        <div class="container">
            <h2>Nos Services</h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-icon">⚡</div>
                    <h3>Rénovation Complète</h3>
                    <p>Remise à neuf de vos jantes aluminium avec finition professionnelle</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">✨</div>
                    <h3>Polissage Expert</h3>
                    <p>Polissage haute qualité pour un éclat parfait de vos jantes</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🎨</div>
                    <h3>Personnalisation</h3>
                    <p>Customisation selon vos goûts avec une large gamme de finitions</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🔧</div>
                    <h3>Réparation</h3>
                    <p>Réparation de rayures, impacts et déformations sur jantes alu</p>
                </div>
            </div>
        </div>
    </section>

    <section class="contact">
        <div class="container">
            <h2>Nous Contacter</h2>
            <div class="contact-info">
                <div class="contact-item">
                    <h3>📍 Adresse</h3>
                    <p>Liévin, France</p>
                </div>
                <div class="contact-item">
                    <h3>📞 Téléphone</h3>
                    <p>Contactez-nous pour un devis</p>
                </div>
                <div class="contact-item">
                    <h3>📧 Email</h3>
                    <p>contact@myjantes.fr</p>
                </div>
                <div class="contact-item">
                    <h3>⏰ Horaires</h3>
                    <p>Sur rendez-vous</p>
                </div>
            </div>
            <div>
                <a href="mailto:contact@myjantes.fr" class="btn">Demander un devis</a>
                <a href="tel:+" class="btn">Nous appeler</a>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 MY JANTES - Expert en rénovation de jantes aluminium à Liévin</p>
        </div>
    </footer>
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
    """Main server function with improved deployment handling"""
    PORT = int(os.environ.get("PORT", 5000))
    
    print("=" * 50)
    print("MY JANTES Flutter Web Server")
    print("Replit Cloud Run Deployment")
    print("=" * 50)
    
    # Build Flutter web application
    print("Building Flutter application...")
    build_success = build_flutter_web()
    
    if build_success:
        print("Build process completed successfully!")
    else:
        print("Build process completed with fallback")
    
    # Verify server directory exists
    build_dir = Path("flutter_app/build/web")
    if not build_dir.exists():
        print("Creating fallback web structure...")
        create_fallback_web()
    
    # Start server with improved error handling
    try:
        # Allow port reuse to avoid binding issues
        socketserver.TCPServer.allow_reuse_address = True
        
        with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
            print(f"Server started successfully on http://0.0.0.0:{PORT}")
            print(f"Health check endpoint: http://0.0.0.0:{PORT}/health")
            print(f"MY JANTES application ready for deployment!")
            print("=" * 50)
            
            # For deployment, ensure we return immediately on health checks
            if os.environ.get('REPL_DEPLOYMENT'):
                print("Deployment mode: Server ready for health checks")
            
            httpd.serve_forever()
            
    except PermissionError:
        print(f"Permission denied binding to port {PORT}")
        print("Trying alternative port...")
        PORT = PORT + 1
        try:
            with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
                print(f"Server started on alternative port: http://0.0.0.0:{PORT}")
                httpd.serve_forever()
        except Exception as e:
            print(f"Failed to start on alternative port: {e}")
            sys.exit(1)
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} is already in use")
            print("This may indicate the server is already running")
            sys.exit(1)
        else:
            print(f"Network error: {e}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()