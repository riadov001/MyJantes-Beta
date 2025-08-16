#!/usr/bin/env python3
"""
Flutter Web Runner for Replit Deployment
Handles Flutter web building and serving
"""
import os
import subprocess
import sys
from pathlib import Path

def main():
    # Change to flutter_app directory
    os.chdir('flutter_app')
    
    # Check if Flutter is available
    try:
        subprocess.run(['flutter', '--version'], check=True, capture_output=True)
        print("Flutter detected, building web version...")
        
        # Get dependencies
        subprocess.run(['flutter', 'pub', 'get'], check=True)
        
        # Build for web
        subprocess.run(['flutter', 'build', 'web', '--release'], check=True)
        
        # Run the web server
        subprocess.run([
            'flutter', 'run', 
            '-d', 'web-server',
            '--web-hostname=0.0.0.0',
            '--web-port=5000'
        ], check=True)
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Flutter not available, switching to Python fallback server...")
        os.chdir('..')
        subprocess.run([sys.executable, 'main.py'])

if __name__ == "__main__":
    main()