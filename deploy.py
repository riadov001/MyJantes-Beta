#!/usr/bin/env python3
"""
Replit Deployment Script for MY JANTES Flutter App
This script handles the complete deployment process including building and serving the Flutter web app.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def setup_environment():
    """Setup environment variables for deployment"""
    os.environ['FLUTTER_WEB_PORT'] = os.environ.get('PORT', '5000')
    os.environ['PYTHON_UNBUFFERED'] = '1'
    print(f"Deployment environment configured (Port: {os.environ['FLUTTER_WEB_PORT']})")

def check_flutter_sdk():
    """Verify Flutter SDK is available and working"""
    try:
        result = subprocess.run(['flutter', '--version'], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"Flutter SDK found: {version_line}")
            return True
        else:
            print("Flutter SDK check failed")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"Flutter SDK not available: {e}")
        return False

def build_flutter_web_app():
    """Build the Flutter web application for production"""
    flutter_dir = Path('flutter_app')
    if not flutter_dir.exists():
        print("Error: flutter_app directory not found")
        return False
    
    print("Starting Flutter web build process...")
    
    original_dir = os.getcwd()
    try:
        # Change to Flutter project directory
        os.chdir('flutter_app')
        
        # Clean any previous builds
        print("Cleaning previous builds...")
        subprocess.run(['flutter', 'clean'], capture_output=True, timeout=30)
        
        # Install dependencies
        print("Installing Flutter dependencies...")
        pub_result = subprocess.run(['flutter', 'pub', 'get'], 
                                  capture_output=True, text=True, timeout=60)
        
        if pub_result.returncode != 0:
            print(f"Warning during pub get: {pub_result.stderr}")
        
        # Build web application
        print("Building web application...")
        build_result = subprocess.run([
            'flutter', 'build', 'web', '--release',
            '--web-renderer', 'html',
            '--dart-define=FLUTTER_WEB_USE_SKIA=false'
        ], capture_output=True, text=True, timeout=300)
        
        if build_result.returncode == 0:
            print("Flutter web build completed successfully!")
            
            # Verify build output exists
            build_path = Path('build/web/index.html')
            if build_path.exists():
                print(f"Build verification: index.html found ({build_path.stat().st_size} bytes)")
                return True
            else:
                print("Build verification failed: index.html not found")
                return False
        else:
            print(f"Flutter build failed:")
            print(f"STDOUT: {build_result.stdout}")
            print(f"STDERR: {build_result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Flutter build timed out")
        return False
    except Exception as e:
        print(f"Error during Flutter build: {e}")
        return False
    finally:
        os.chdir(original_dir)

def start_python_server():
    """Start the Python server to serve the Flutter web app"""
    print("Starting Python server to serve Flutter web application...")
    try:
        from main import main as start_main_server
        start_main_server()
    except Exception as e:
        print(f"Failed to start Python server: {e}")
        sys.exit(1)

def main():
    """Main deployment process"""
    print("=" * 60)
    print("MY JANTES Flutter Web Deployment")
    print("=" * 60)
    
    # Setup deployment environment
    setup_environment()
    
    # Check Flutter SDK availability
    flutter_available = check_flutter_sdk()
    
    if flutter_available:
        # Attempt to build Flutter web app
        build_success = build_flutter_web_app()
        
        if build_success:
            print("✅ Flutter build successful - starting server")
        else:
            print("⚠️  Flutter build failed - server will use fallback content")
    else:
        print("⚠️  Flutter SDK not available - server will use fallback content")
    
    # Always start the Python server (it handles both built Flutter app and fallback)
    print("=" * 60)
    start_python_server()

if __name__ == "__main__":
    main()