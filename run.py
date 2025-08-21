#!/usr/bin/env python3
"""
Flutter Web Runner for Replit Deployment
Handles Flutter web building and serving with improved deployment support
"""
import os
import subprocess
import sys
from pathlib import Path

def check_flutter_available():
    """Check if Flutter SDK is available"""
    try:
        result = subprocess.run(['flutter', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"Flutter available: {result.stdout.split()[1] if result.stdout else 'version unknown'}")
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def build_flutter_web():
    """Build Flutter web application for deployment"""
    print("Building Flutter web application...")
    
    try:
        # Clean previous builds
        subprocess.run(['flutter', 'clean'], capture_output=True)
        print("Cleaned previous builds")
        
        # Get dependencies
        result = subprocess.run(['flutter', 'pub', 'get'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: pub get failed: {result.stderr}")
        else:
            print("Dependencies installed successfully")
        
        # Build for web with explicit renderer
        result = subprocess.run([
            'flutter', 'build', 'web', '--release', 
            '--web-renderer', 'html'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Flutter web build completed successfully!")
            return True
        else:
            print(f"Flutter build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during Flutter build: {e}")
        return False

def run_flutter_dev_server():
    """Run Flutter development server for local development"""
    port = os.environ.get('PORT', '5000')
    print(f"Starting Flutter development server on port {port}...")
    
    try:
        subprocess.run([
            'flutter', 'run', 
            '-d', 'web-server',
            '--web-hostname', '0.0.0.0',
            '--web-port', str(port),
            '--release'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Flutter dev server failed: {e}")
        return False
    return True

def main():
    """Main deployment logic"""
    print("=" * 50)
    print("MY JANTES Flutter Deployment")
    print("=" * 50)
    
    # Detect environment
    is_deployment = os.environ.get('REPL_DEPLOYMENT') == 'true'
    
    # Change to flutter_app directory
    flutter_dir = Path('flutter_app')
    if not flutter_dir.exists():
        print("Error: flutter_app directory not found")
        sys.exit(1)
    
    os.chdir('flutter_app')
    
    # Check Flutter availability
    flutter_available = check_flutter_available()
    
    if not flutter_available:
        print("Flutter not available, switching to Python fallback server...")
        os.chdir('..')
        subprocess.run([sys.executable, 'main.py'])
        return
    
    # Handle deployment vs development
    if is_deployment:
        print("Deployment mode: Building Flutter web app...")
        if build_flutter_web():
            print("Build successful, switching to Python server to serve static files...")
            os.chdir('..')
            subprocess.run([sys.executable, 'main.py'])
        else:
            print("Build failed, switching to Python fallback server...")
            os.chdir('..')
            subprocess.run([sys.executable, 'main.py'])
    else:
        print("Development mode: Starting Flutter development server...")
        if not run_flutter_dev_server():
            print("Development server failed, switching to Python fallback server...")
            os.chdir('..')
            subprocess.run([sys.executable, 'main.py'])

if __name__ == "__main__":
    main()