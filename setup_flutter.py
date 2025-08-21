#!/usr/bin/env python3
"""
Flutter SDK Setup and Installation Script for Replit Deployment
Ensures Flutter SDK is available for building the web application
"""

import os
import subprocess
import sys
import urllib.request
import tarfile
import shutil
from pathlib import Path

def check_flutter_installed():
    """Check if Flutter SDK is already installed and working"""
    try:
        result = subprocess.run(
            ['flutter', '--version'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print(f"Flutter SDK already available: {result.stdout.split()[1] if result.stdout else 'version unknown'}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False
    return False

def install_flutter_sdk():
    """Install Flutter SDK if not available"""
    print("Installing Flutter SDK for deployment...")
    
    # Flutter SDK download URL for Linux
    flutter_url = "https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.22.3-stable.tar.xz"
    flutter_archive = "flutter_linux_stable.tar.xz"
    flutter_dir = Path.home() / "flutter"
    
    try:
        # Download Flutter SDK
        print("Downloading Flutter SDK...")
        urllib.request.urlretrieve(flutter_url, flutter_archive)
        print("Flutter SDK downloaded successfully")
        
        # Extract Flutter SDK
        print("Extracting Flutter SDK...")
        with tarfile.open(flutter_archive, 'r:xz') as tar:
            tar.extractall(Path.home())
        
        # Clean up archive
        os.remove(flutter_archive)
        
        # Add Flutter to PATH
        flutter_bin = flutter_dir / "bin"
        current_path = os.environ.get('PATH', '')
        new_path = f"{flutter_bin}:{current_path}"
        os.environ['PATH'] = new_path
        
        print(f"Flutter SDK installed to: {flutter_dir}")
        print(f"Flutter bin added to PATH: {flutter_bin}")
        
        # Verify installation
        try:
            result = subprocess.run(
                [str(flutter_bin / "flutter"), '--version'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                print("Flutter SDK installation verified successfully")
                return True
            else:
                print(f"Flutter SDK verification failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"Flutter SDK verification error: {e}")
            return False
            
    except Exception as e:
        print(f"Failed to install Flutter SDK: {e}")
        return False

def setup_flutter_for_web():
    """Setup Flutter for web development"""
    try:
        print("Enabling Flutter web support...")
        result = subprocess.run(
            ['flutter', 'config', '--enable-web'], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("Flutter web support enabled")
            return True
        else:
            print(f"Failed to enable Flutter web: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error enabling Flutter web: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("Flutter SDK Setup for MY JANTES Deployment")
    print("=" * 50)
    
    # Check if Flutter is already available
    if check_flutter_installed():
        print("Flutter SDK is already available")
        return setup_flutter_for_web()
    
    # Try to install Flutter SDK
    if install_flutter_sdk():
        return setup_flutter_for_web()
    else:
        print("Failed to install Flutter SDK")
        print("Deployment will continue with fallback web structure")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)